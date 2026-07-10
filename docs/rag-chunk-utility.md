# RAG Chunk Utility Scoring

AgenticLens can identify low-utility retrieved chunks that waste tokens without
contributing to the final answer. This guide explains the supported signal types
and how to use them.

---

## How It Works

When a retriever step includes `retrieved_chunks` in its metadata, the
`RAGChunkUtilityRecommender` scores each chunk to determine whether it was
useful. Chunks scoring below the threshold (`rag_min_chunk_utility_score`,
default 0.08) are flagged as low-utility.

---

## Supported Signals (Priority Order)

### 1. Citation Signals

Boolean fields that indicate whether the chunk was actually used in the response.

```python
{"text": "Refunds take 5-10 days.", "cited": True}
{"text": "Warehouse inventory system.", "cited": False}
{"text": "Used in answer.", "referenced": True}
{"text": "Old policy doc.", "used": False}
```

**Fields:** `cited`, `used`, `referenced`
**Values:** `True` → score 1.0, `False` → score 0.0

### 2. Reranker Scores

Cross-encoder or reranker confidence scores (0 to 1).

```python
{"text": "Highly relevant passage.", "reranker_score": 0.95}
{"text": "Marginally relevant.", "reranker_score": 0.45}
{"text": "Irrelevant noise.", "cross_encoder_score": 0.02}
```

**Fields:** `reranker_score`, `rerank_score`, `cross_encoder_score`
**Values:** Float 0.0–1.0

### 3. Embedding Similarity

Cosine similarity between chunk embedding and query/answer embedding.

```python
{"text": "Semantically close.", "cosine_similarity": 0.88}
{"text": "Distant meaning.", "embedding_similarity": 0.12}
{"text": "Moderate match.", "semantic_score": 0.55}
```

**Fields:** `embedding_similarity`, `cosine_similarity`, `semantic_score`
**Values:** Float 0.0–1.0

### 4. Generic Utility Scores

Any custom scoring your pipeline provides.

```python
{"text": "Custom scored chunk.", "utility_score": 0.73}
{"text": "Low relevance.", "relevance_score": 0.05}
```

**Fields:** `utility_score`, `relevance_score`, `answer_overlap`
**Values:** Float 0.0–1.0

### 5. Fallback: Word Overlap

If none of the above fields are present, the rule computes word overlap between
the chunk text and the final answer found in the workflow. This is intentionally
conservative — it only catches obviously irrelevant chunks.

---

## Confidence and Quality Risk

| Signal Source | Confidence Range | Quality Risk |
|--------------|-----------------|--------------|
| Citation / Reranker / Embedding | 0.65–0.95 | low |
| Word-overlap fallback | 0.45–0.85 | medium |

Rich signals yield higher confidence because they come from models specifically
designed to assess relevance, whereas word overlap is a rough heuristic.

---

## Usage Example

```python
from agenticlens import profile, step

with profile("RAG Pipeline") as workflow:
    with step(
        "Retriever",
        type="retriever",
        chunk_count=6,
        avg_tokens_per_chunk=80,
        retrieved_chunks=[
            {"text": "Refund policy: within 30 days.", "reranker_score": 0.92},
            {"text": "Returns must be unused.", "reranker_score": 0.78},
            {"text": "Office hours: 9-5 weekdays.", "reranker_score": 0.03},
            {"text": "Parking info for visitors.", "reranker_score": 0.01},
            {"text": "Shipping takes 5-7 days.", "cosine_similarity": 0.41},
            {"text": "CEO biography page.", "cosine_similarity": 0.05},
        ],
    ):
        pass

    with step(
        "Final Answer",
        type="final_response",
        provider="openai",
        model="gpt-4o-mini",
        final_answer="You can return within 30 days if unused.",
    ) as s:
        s.record(response)
```

### Expected Output

```text
Budget Optimization Run cost: $0.0045; reducible: ~$0.0019/run (42%)

Optimization Suggestions
  * Low-utility retrieved chunks
    Step 'Retriever' retrieved 3 chunks that appear unlikely to
    influence the final answer (6 chunks scored). Consider lowering
    top-k, tightening retrieval filters, or reranking before generation.

    Tokens saved: 240
    Confidence: 0.90
    Quality risk: low
```

---

## Configuration

In your AgenticLens config (YAML):

```yaml
recommender:
  rag_min_chunk_utility_score: 0.08   # Threshold below which a chunk is "low-utility"
  rag_min_low_utility_chunks: 2       # Minimum low-utility chunks before flagging
```

---

## When to Use Which Signal

| Your Setup | Best Signal |
|-----------|-------------|
| You have a reranker in your pipeline | `reranker_score` |
| You store cosine similarity from vector search | `cosine_similarity` |
| You track which chunks the LLM actually cited | `cited` |
| You have a custom relevance model | `utility_score` |
| No scoring available | Automatic word-overlap fallback |
