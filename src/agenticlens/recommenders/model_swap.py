import warnings
from dataclasses import dataclass

from agenticlens.config.live_pricing import (
    LivePricingConfig,
    get_live_pricing_table,
    parse_litellm_entry,
)
from agenticlens.config.pricing import (
    ModelPricing,
    UnknownModelPricingWarning,
    bundled_pricing_table,
    calculate_cost,
    resolve_pricing,
)
from agenticlens.config.settings import RecommenderConfig
from agenticlens.models.enums import Severity
from agenticlens.models.recommendation import Recommendation
from agenticlens.models.workflow import Workflow
from agenticlens.recommenders.base import BaseRecommender


@dataclass(frozen=True)
class _Candidate:
    provider: str
    model: str
    pricing: ModelPricing
    max_input_tokens: int | None


def _candidate_label(candidate: _Candidate) -> str:
    """Human-readable identifier for a candidate.

    Some live-feed keys are already provider-qualified (e.g. LiteLLM's Gemini
    entries are all named "gemini/gemini-2.5-flash"), so "provider:model" would
    read as a redundant "gemini:gemini/gemini-2.5-flash". Show the raw key
    as-is in that case.
    """
    if candidate.model.startswith(f"{candidate.provider}/"):
        return candidate.model
    return f"{candidate.provider}:{candidate.model}"


class ModelSwapRecommender(BaseRecommender):
    """Flags steps that could have used a cheaper model for the same token usage.

    Compares each step's cost (recomputed fresh, not the possibly-stale stored
    `step.metrics.cost`) against a pool of candidate models -- by default, the
    live LiteLLM pricing feed filtered to a curated set of direct/first-party
    providers (see `DEFAULT_MODEL_SWAP_PROVIDERS`), falling back to the small
    bundled static table when live pricing is disabled or unreachable.
    """

    def __init__(
        self,
        candidates: list[str] | None = None,
        pricing_overrides: dict[str, ModelPricing] | None = None,
        live_pricing: LivePricingConfig | None = None,
    ) -> None:
        self._explicit_candidates = candidates
        self._pricing_overrides = pricing_overrides
        self._live_pricing = live_pricing or LivePricingConfig()

    def evaluate(self, workflow: Workflow, config: RecommenderConfig) -> list[Recommendation]:
        candidates = self._resolve_candidates(config.model_swap_providers)
        if not candidates:
            return []

        recommendations: list[Recommendation] = []
        for step in workflow.steps:
            if step.provider is None or step.model is None:
                continue
            prompt_tokens = step.metrics.prompt_tokens
            completion_tokens = step.metrics.completion_tokens
            if prompt_tokens == 0 and completion_tokens == 0:
                continue

            current_cost = self._current_cost(
                step.provider, step.model, prompt_tokens, completion_tokens
            )
            if current_cost is None:
                continue

            current_key = f"{step.provider}:{step.model}"
            best: _Candidate | None = None
            best_cost = current_cost
            for candidate in candidates:
                key = f"{candidate.provider}:{candidate.model}"
                if key == current_key:
                    continue
                if (
                    candidate.max_input_tokens is not None
                    and prompt_tokens > candidate.max_input_tokens
                ):
                    continue
                candidate_cost = (prompt_tokens / 1000) * candidate.pricing.input_per_1k + (
                    completion_tokens / 1000
                ) * candidate.pricing.output_per_1k
                if candidate_cost < best_cost:
                    best_cost = candidate_cost
                    best = candidate

            if best is None or current_cost <= 0:
                continue

            savings = current_cost - best_cost
            savings_pct = (savings / current_cost) * 100
            if savings_pct < config.model_swap_min_savings_pct:
                continue

            recommendations.append(
                Recommendation(
                    title="Cheaper model available",
                    description=(
                        f"Step '{step.name}' used {current_key} (${current_cost:.4f}). "
                        f"{_candidate_label(best)} would cost ~${best_cost:.4f} for the "
                        f"same token usage -- {savings_pct:.0f}% cheaper."
                    ),
                    severity=Severity.WARNING,
                    cost_savings=savings,
                )
            )
        return recommendations

    def _current_cost(
        self, provider: str, model: str, prompt_tokens: int, completion_tokens: int
    ) -> float | None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UnknownModelPricingWarning)
            return calculate_cost(
                provider,
                model,
                prompt_tokens,
                completion_tokens,
                overrides=self._pricing_overrides,
                live_pricing=self._live_pricing,
            )

    def _resolve_candidates(self, allowed_providers: list[str]) -> list[_Candidate]:
        if self._explicit_candidates is not None:
            return self._candidates_from_explicit_list()

        candidates = self._candidates_from_live_feed(set(allowed_providers))
        if candidates:
            return candidates

        return self._candidates_from_static_table()

    def _candidates_from_explicit_list(self) -> list[_Candidate]:
        candidates: list[_Candidate] = []
        for spec in self._explicit_candidates or []:
            provider, _, model = spec.partition(":")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UnknownModelPricingWarning)
                pricing = resolve_pricing(
                    provider, model, self._pricing_overrides, self._live_pricing
                )
            if pricing is not None:
                candidates.append(
                    _Candidate(
                        provider=provider, model=model, pricing=pricing, max_input_tokens=None
                    )
                )
        return candidates

    def _candidates_from_live_feed(self, allowed_providers: set[str]) -> list[_Candidate]:
        table = get_live_pricing_table(self._live_pricing) if self._live_pricing.enabled else None
        if not table:
            return []

        candidates: list[_Candidate] = []
        for key, entry in table.items():
            if not isinstance(entry, dict):
                continue
            if key.startswith("ft:"):
                continue
            if entry.get("mode") != "chat":
                continue
            provider = entry.get("litellm_provider")
            if provider not in allowed_providers:
                continue
            pricing = parse_litellm_entry(entry)
            if pricing is None:
                continue
            candidates.append(
                _Candidate(
                    provider=provider,
                    model=key,
                    pricing=pricing,
                    max_input_tokens=entry.get("max_input_tokens"),
                )
            )
        return candidates

    def _candidates_from_static_table(self) -> list[_Candidate]:
        candidates: list[_Candidate] = []
        for key, pricing in bundled_pricing_table().items():
            provider, _, model = key.partition(":")
            candidates.append(
                _Candidate(provider=provider, model=model, pricing=pricing, max_input_tokens=None)
            )
        return candidates
