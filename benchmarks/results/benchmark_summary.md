# AgenticLens Framework Benchmark Comparison

Use case: Practical customer support refund workflow.

The workflow includes:

- ticket intent classification
- query rewriting
- refund policy retrieval
- order lookup
- refund eligibility check
- customer reply generation

## Summary Results

| Framework | Total Tokens | Prompt Tokens | Completion Tokens | Cost USD | Latency Sec | Steps | Tool Calls | Retrieved Chunks | Highest Token Step |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| AutoGen | 2255 | 1970 | 285 | $0.00046650 | 0.00051530 | 6 | 1 | 4 | AutoGen - Generate Customer Reply |
| CrewAI | 2255 | 1970 | 285 | $0.00046650 | 0.00049570 | 6 | 1 | 4 | CrewAI - Generate Customer Reply |
| LlamaIndex | 2255 | 1970 | 285 | $0.00046650 | 0.00055400 | 6 | 1 | 4 | LlamaIndex - Generate Customer Reply |
| Native Python | 2255 | 1970 | 285 | $0.00046650 | 0.00084060 | 6 | 1 | 4 | Generate Customer Reply |
| Semantic Kernel | 2255 | 1970 | 285 | $0.00046650 | 0.00062650 | 6 | 1 | 4 | Semantic Kernel - Generate Customer Reply |
| LangGraph | 2460 | 2130 | 330 | $0.00051750 | 0.00093570 | 6 | 1 | 4 | LangGraph - Generate Customer Reply |

## Key Finding

The final customer reply step is the highest token-consuming step across the benchmark runs.

## Important Note

These results are workload-specific. They should not be treated as a universal ranking of frameworks.
The purpose is to show how AgenticLens can normalize and compare token, cost, latency, retrieval, and tool-call metrics across framework implementations.