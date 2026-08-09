from agenticlens.models.trace import Finding


def next_best_analyses(findings: list[Finding]) -> list[str]:
    categories = {finding.category for finding in findings}
    suggestions: list[str] = []
    if not findings:
        return suggestions
    if "retry" in categories:
        suggestions.append(
            "Inspect retry parent spans and failure types to separate transient "
            "tool errors from prompt issues."
        )
    if "memory" in categories:
        suggestions.append(
            "Review memory-read and memory-write spans to trim context that is "
            "high-cost but low-signal."
        )
    if "context" in categories:
        suggestions.append(
            "Compare duplicated context groups to consolidate repeated retrieval "
            "or prompt assembly work."
        )
    if not suggestions:
        suggestions.append(
            "Re-run the workflow with repeated samples and compare baseline "
            "versus candidate traces."
        )
    return suggestions
