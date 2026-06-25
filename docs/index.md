# TokenLens

Profile, analyze, and optimize token consumption in LLM-powered applications and agentic workflows.

See the [project specification](../TokenLens_Spec.md) for the full design.

```python
from tokenlens import profile, step

with profile("Customer Support"):
    with step("Planner", type="planner") as s:
        response = planner_llm.invoke(prompt)
        s.record(response)
```
