import re
from collections.abc import Iterable
from typing import Any

from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity, StepType
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender

_WORD_RE = re.compile(r"[a-zA-Z0-9]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


class RAGChunkUtilityRecommender(BaseRecommender):
    """Flags retrieved chunks that appear unlikely to influence the final answer.

    Reads `metadata["retrieved_chunks"]` on retriever steps. Chunks may be plain
    strings or dictionaries with `text`/`content`, `utility_score`, `used`, or
    `cited` fields. If explicit utility signals are absent, the rule falls back
    to lexical overlap against a final answer found in workflow metadata.
    """

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        final_answer = self._find_final_answer(workflow)
        recommendations: list[Recommendation] = []

        for step in workflow.steps:
            if step.type != StepType.RETRIEVER:
                continue

            chunks = step.metadata.get("retrieved_chunks")
            if not isinstance(chunks, list) or not chunks:
                continue

            low_utility_count = 0
            scored_count = 0
            for chunk in chunks:
                utility_score = self._explicit_utility_score(chunk)
                if utility_score is None and final_answer:
                    utility_score = self._answer_overlap_score(
                        self._chunk_text(chunk),
                        final_answer,
                    )

                if utility_score is None:
                    continue

                scored_count += 1
                if utility_score < config.rag_min_chunk_utility_score:
                    low_utility_count += 1

            if low_utility_count < config.rag_min_low_utility_chunks:
                continue

            avg_tokens_per_chunk = step.metadata.get("avg_tokens_per_chunk")
            if avg_tokens_per_chunk is None:
                avg_tokens_per_chunk = self._estimate_avg_tokens(chunks)
            tokens_saved = round(low_utility_count * avg_tokens_per_chunk)

            recommendations.append(
                Recommendation(
                    title="Low-utility retrieved chunks",
                    description=(
                        f"Step '{step.name}' retrieved {low_utility_count} chunks "
                        f"that appear unlikely to influence the final answer "
                        f"({scored_count} chunks scored). Consider lowering top-k, "
                        "tightening retrieval filters, or reranking before generation."
                    ),
                    severity=Severity.WARNING,
                    tokens_saved=tokens_saved,
                    confidence=min(0.95, 0.45 + (scored_count / max(len(chunks), 1)) * 0.4),
                    quality_risk="medium",
                )
            )

        return recommendations

    @staticmethod
    def _find_final_answer(workflow: Workflow) -> str | None:
        for step in reversed(workflow.steps):
            for key in ("final_answer", "answer", "output", "response"):
                value = step.metadata.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        return None

    @staticmethod
    def _explicit_utility_score(chunk: Any) -> float | None:
        if not isinstance(chunk, dict):
            return None

        for key in ("used", "cited"):
            value = chunk.get(key)
            if isinstance(value, bool):
                return 1.0 if value else 0.0

        for key in ("utility_score", "relevance_score", "answer_overlap"):
            value = chunk.get(key)
            if isinstance(value, int | float):
                return max(0.0, min(1.0, float(value)))

        return None

    @staticmethod
    def _chunk_text(chunk: Any) -> str:
        if isinstance(chunk, str):
            return chunk
        if isinstance(chunk, dict):
            for key in ("text", "content", "document", "chunk"):
                value = chunk.get(key)
                if isinstance(value, str):
                    return value
        return ""

    @classmethod
    def _answer_overlap_score(cls, chunk_text: str, final_answer: str) -> float | None:
        chunk_words = cls._meaningful_words(chunk_text)
        if not chunk_words:
            return None
        answer_words = cls._meaningful_words(final_answer)
        if not answer_words:
            return None
        return len(chunk_words.intersection(answer_words)) / len(chunk_words)

    @staticmethod
    def _meaningful_words(text: str) -> set[str]:
        return {
            word
            for word in (match.group(0).lower() for match in _WORD_RE.finditer(text))
            if len(word) > 2 and word not in _STOPWORDS
        }

    @classmethod
    def _estimate_avg_tokens(cls, chunks: Iterable[Any]) -> float:
        token_counts = [
            max(1, round(len(cls._chunk_text(chunk).split()) * 1.3)) for chunk in chunks
        ]
        if not token_counts:
            return 0.0
        return sum(token_counts) / len(token_counts)
