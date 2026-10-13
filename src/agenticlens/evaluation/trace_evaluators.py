"""Trace-aware evaluators.

These evaluators score a case from what the *trace* recorded, not only from
the final output: the tool trajectory, whether the agent reached its goal,
how agents handed off work, whether it looped, whether the answer is backed
by what retrieval actually returned, and whether sensitive data leaked into
the output or into tool arguments.

They read the span semantics `to_eval_trace()` copies into `EvalSpan`
attributes (`agenticlens.span_type`, `agenticlens.agent_name`, ...), so they
work on AgenticLens traces and on any `EvalTrace` producer that sets the
same keys.

All evaluators here are deterministic. The text-quality checks
(`groundedness`, `relevance`, `completeness`) are **lexical heuristics**:
they measure word overlap, not meaning. Use them as cheap first-pass
signals and pair them with an LLM judge (`structured_judge`) where semantic
accuracy matters; `analyze_scores()` then shows where the two disagree.

Configure an evaluator per case through `EvaluatorConfig.config`, for
example in a YAML suite::

    evaluators:
      - name: tool_trajectory
        config: {expected: [search, fetch, answer], mode: in_order}
      - name: groundedness
        threshold: 0.8
"""

import re
from collections.abc import Callable, Iterable
from typing import Any

from agentic_evals import (
    CallableEvaluator,
    EvalSpan,
    EvaluationContext,
    EvaluatorRegistry,
    Score,
)
from agentic_evals.scorers import default_registry as _evals_default_registry

from agenticlens.evaluation._trace_adapter import LENS_PREFIX

TRACE_EVALUATOR_VERSION = "1.0"
EVALUATOR_TYPE = "trace_rule"

_WORD = re.compile(r"[a-z0-9]+")
_SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
_STOPWORD_TEXT = (
    "a an and are as at be been but by can did do does for from had has have how i if in "
    "into is it its me my no not of on or our so than that the their them then there these "
    "they this to was we were what when where which who why will with you your"
)
_STOPWORDS = frozenset(_STOPWORD_TEXT.split())


# -- shared helpers ------------------------------------------------------------


def _lens(span: EvalSpan, key: str) -> Any:
    return span.attributes.get(LENS_PREFIX + key)


def _config(context: EvaluationContext, key: str, default: Any = None) -> Any:
    """Evaluator config first, then the case's metadata."""
    if key in context.config.config:
        return context.config.config[key]
    return context.case.metadata.get(key, default)


def _tool_calls(context: EvaluationContext) -> list[EvalSpan]:
    return [span for span in context.sample.trace.spans if span.tool_name]


def _stem(word: str) -> str:
    """Crude suffix stripping so 'arrives'/'arrive' and 'refunds'/'refund' match."""
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and not word.endswith("ss") and len(word) - len(suffix) >= 3:
            word = word[: -len(suffix)]
            break
    return word[:-1] if word.endswith("e") and len(word) > 3 else word


def _content_words(text: str) -> set[str]:
    return {_stem(w) for w in _WORD.findall(text.casefold()) if len(w) > 2 and w not in _STOPWORDS}


def _text_of(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("text", "content", "page_content", "chunk", "snippet"):
            if isinstance(value.get(key), str):
                return str(value[key])
        return " ".join(_text_of(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return " ".join(_text_of(v) for v in value)
    return "" if value is None else str(value)


def _documents(context: EvaluationContext) -> list[Any]:
    """Retrieved documents: explicit config/case context, then retrieval spans."""
    explicit = _config(context, "context")
    if explicit is not None:
        return list(explicit) if isinstance(explicit, (list, tuple)) else [explicit]
    found: list[Any] = []
    for span in context.sample.trace.spans:
        for key in (LENS_PREFIX + "retrieved", "documents", "retrieval.documents", "chunks"):
            value = span.attributes.get(key)
            if isinstance(value, list):
                found.extend(value)
                break
            if isinstance(value, str):
                found.append(value)
                break
    return found


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def _evaluator(name: str, function: Callable[[EvaluationContext], Score]) -> CallableEvaluator:
    return CallableEvaluator(
        name, function, evaluator_type=EVALUATOR_TYPE, version=TRACE_EVALUATOR_VERSION
    )


# -- trajectory and agent behavior --------------------------------------------


def _subsequence_matched(expected: list[str], actual: list[str]) -> int:
    """Longest common subsequence length (order-preserving matches)."""
    previous = [0] * (len(actual) + 1)
    for wanted in expected:
        current = [0]
        for index, got in enumerate(actual):
            current.append(
                previous[index] + 1 if wanted == got else max(previous[index + 1], current[index])
            )
        previous = current
    return previous[-1]


def tool_trajectory(context: EvaluationContext) -> Score:
    """Compare the recorded tool sequence with an expected one.

    Config: ``expected`` (list of tool names, required) and ``mode``:
    ``exact`` (same tools in the same order, nothing extra), ``in_order``
    (expected tools appear in order; extra calls allowed; partial credit is
    the longest in-order match), or ``any_order`` (multiset recall).
    """
    expected = _config(context, "expected")
    if not isinstance(expected, list) or not expected:
        return Score.skip("tool_trajectory", "No expected trajectory configured.")
    expected = [str(item) for item in expected]
    mode = str(_config(context, "mode", "in_order"))
    actual = [str(span.tool_name) for span in _tool_calls(context)]
    if mode == "exact":
        value = 1.0 if actual == expected else 0.0
    elif mode == "any_order":
        remaining = list(actual)
        hits = 0
        for tool in expected:
            if tool in remaining:
                remaining.remove(tool)
                hits += 1
        value = hits / len(expected)
    elif mode == "in_order":
        value = _subsequence_matched(expected, actual) / len(expected)
    else:
        raise ValueError(f"tool_trajectory mode must be exact, in_order, or any_order: {mode!r}")
    return Score(
        name="tool_trajectory",
        value=value,
        passed=value >= 1.0,
        explanation=f"{mode} match {value:.0%}: expected {expected}, recorded {actual}.",
        metadata={"mode": mode, "expected": expected, "actual": actual},
    )


def agent_goal(context: EvaluationContext) -> Score:
    """Did the run reach its goal?

    Checks, each worth an equal share: the trace reports task success
    (``require_task_success``, default true; skipped when the trace does not
    say), the run did not fail, no span failed (``allow_failed_spans``,
    default false), the last agent is ``final_agent`` (if configured), and the
    output contains every ``goal_contains`` string (if configured).
    """
    trace = context.sample.trace
    checks: dict[str, bool] = {}
    task_success = trace.metadata.get(LENS_PREFIX + "task_success")
    if _config(context, "require_task_success", True) and isinstance(task_success, bool):
        checks["task_success"] = task_success
    status = trace.metadata.get(LENS_PREFIX + "run_status")
    if isinstance(status, str):
        checks["run_not_failed"] = status != "failed"
    if not _config(context, "allow_failed_spans", False):
        statuses = [_lens(span, "status") for span in trace.spans]
        if any(isinstance(s, str) for s in statuses):
            checks["no_failed_spans"] = "failed" not in statuses
    final_agent = _config(context, "final_agent")
    if isinstance(final_agent, str):
        agents = [a for a in (_lens(span, "agent_name") for span in trace.spans) if a]
        checks["final_agent"] = bool(agents) and agents[-1] == final_agent
    goal_text = _config(context, "goal_contains")
    if isinstance(goal_text, list):
        output = context.sample.output.casefold()
        for item in goal_text:
            checks[f"contains:{item}"] = str(item).casefold() in output
    if not checks:
        return Score.skip("agent_goal", "The trace records no goal signals to check.")
    met = [name for name, ok in checks.items() if ok]
    missed = [name for name, ok in checks.items() if not ok]
    value = len(met) / len(checks)
    return Score(
        name="agent_goal",
        value=value,
        passed=not missed,
        explanation=(
            f"Goal checks met {len(met)}/{len(checks)}"
            + (f"; missed: {', '.join(missed)}." if missed else ".")
        ),
        metadata={"checks": checks},
    )


_HANDOFF_TARGET_KEYS = ("to_agent", "target_agent", "handoff.to", "handoff_to")


def _handoffs(context: EvaluationContext) -> list[tuple[str, str]]:
    spans = context.sample.trace.spans
    found: list[tuple[str, str]] = []
    for index, span in enumerate(spans):
        if _lens(span, "span_type") != "delegation":
            continue
        source = span.attributes.get("from_agent") or _lens(span, "agent_name")
        target = next(
            (span.attributes[k] for k in _HANDOFF_TARGET_KEYS if span.attributes.get(k)), None
        )
        if target is None:
            target = next(
                (
                    _lens(later, "agent_name")
                    for later in spans[index + 1 :]
                    if _lens(later, "agent_name") and _lens(later, "agent_name") != source
                ),
                None,
            )
        if isinstance(source, str) and isinstance(target, str) and source != target:
            found.append((source, target))
    return found


def handoff(context: EvaluationContext) -> Score:
    """Check agent handoffs against limits.

    Config: ``max_handoffs`` (int), ``allowed`` (list of ``"from->to"``
    strings), ``max_round_trips`` (default 1: A->B->A is allowed once).
    """
    transitions = _handoffs(context)
    problems: list[str] = []
    max_handoffs = _config(context, "max_handoffs")
    if isinstance(max_handoffs, int) and len(transitions) > max_handoffs:
        problems.append(f"{len(transitions)} handoffs exceed the limit of {max_handoffs}")
    allowed = _config(context, "allowed")
    if isinstance(allowed, list):
        permitted = {str(item).replace(" ", "") for item in allowed}
        for source, target in transitions:
            if f"{source}->{target}" not in permitted:
                problems.append(f"handoff {source}->{target} is not allowed")
    limit = int(_config(context, "max_round_trips", 1))
    counts: dict[tuple[str, str], int] = {}
    for pair in transitions:
        counts[pair] = counts.get(pair, 0) + 1
    for (source, target), forward in counts.items():
        back = counts.get((target, source), 0)
        if source < target and min(forward, back) > limit:
            problems.append(
                f"{source} and {target} bounced {min(forward, back)} times (limit {limit})"
            )
    if not transitions and max_handoffs is None and allowed is None:
        return Score.skip("handoff", "No handoffs recorded and no handoff limits configured.")
    return Score(
        name="handoff",
        value=0.0 if problems else 1.0,
        passed=not problems,
        explanation="; ".join(problems) + "."
        if problems
        else f"{len(transitions)} handoff(s) within limits.",
        metadata={"handoffs": [f"{s}->{t}" for s, t in transitions], "problems": problems},
    )


def loop(context: EvaluationContext) -> Score:
    """Fail when a tool is called with the same input more than ``max_repeats`` times in a row.

    Calls compare by tool name plus the input fingerprint (or ``tool_args``);
    calls with no recorded input compare by tool name alone.
    """
    limit = int(_config(context, "max_repeats", 2))
    longest, tool, streak = 0, None, 0
    previous: Any = None
    for span in _tool_calls(context):
        key = (
            span.tool_name,
            _lens(span, "input_fingerprint") or repr(span.attributes.get("tool_args")),
        )
        streak = streak + 1 if key == previous else 1
        previous = key
        if streak > longest:
            longest, tool = streak, span.tool_name
    value = 1.0 if longest <= limit else limit / longest
    return Score(
        name="loop",
        value=value,
        passed=longest <= limit,
        explanation=(
            f"Longest identical tool-call streak: {longest} ({tool}); limit {limit}."
            if longest
            else "No tool calls recorded."
        ),
        metadata={"longest_streak": longest, "tool": tool, "max_repeats": limit},
    )


# -- retrieval-grounded quality (lexical heuristics) --------------------------


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE.split(text) if len(_content_words(s)) >= 2]


def groundedness(context: EvaluationContext) -> Score:
    """Share of output sentences whose content words appear in retrieved context.

    A sentence counts as supported when at least ``min_overlap`` (default
    0.6) of its content words occur in the documents. Lexical heuristic:
    paraphrases count as unsupported and copied-but-wrong claims as supported.
    """
    documents = _documents(context)
    if not documents:
        return Score.skip("groundedness", "No retrieved context recorded or configured.")
    vocabulary = _content_words(_text_of(documents))
    threshold = float(_config(context, "min_overlap", 0.6))
    sentences = _sentences(context.sample.output)
    if not sentences:
        return Score.skip("groundedness", "Output has no sentences to check.")
    unsupported = [
        s
        for s in sentences
        if len(_content_words(s) & vocabulary) / len(_content_words(s)) < threshold
    ]
    value = 1 - len(unsupported) / len(sentences)
    return Score(
        name="groundedness",
        value=value,
        passed=not unsupported,
        explanation=(
            f"{len(sentences) - len(unsupported)}/{len(sentences)} sentence(s) supported by "
            f"{len(documents)} retrieved document(s) (lexical overlap >= {threshold:.0%})."
        ),
        metadata={"unsupported_sentences": unsupported[:10], "method": "lexical_overlap"},
    )


def relevance(context: EvaluationContext) -> Score:
    """Share of the query's content words the output addresses (lexical heuristic).

    The query is ``query`` from config, else the case input.
    """
    query = _config(context, "query", context.case.input)
    terms = _content_words(_text_of(query))
    if not terms:
        return Score.skip("relevance", "No query text to compare with.")
    covered = terms & _content_words(context.sample.output)
    value = len(covered) / len(terms)
    return Score(
        name="relevance",
        value=value,
        passed=value >= 1.0,
        explanation=f"Output covers {len(covered)}/{len(terms)} query term(s).",
        metadata={"missing_terms": sorted(terms - covered), "method": "lexical_overlap"},
    )


def completeness(context: EvaluationContext) -> Score:
    """Share of ``required_points`` the output mentions.

    Each point is a string or a list of alternative phrasings; matching is
    case-insensitive substring search. Falls back to the case's
    ``expected_contains``.
    """
    points = _config(context, "required_points") or list(context.case.expected_contains)
    if not points:
        return Score.skip("completeness", "No required points configured.")
    output = context.sample.output.casefold()
    missing: list[str] = []
    for point in points:
        options = point if isinstance(point, list) else [point]
        if not any(str(option).casefold() in output for option in options):
            missing.append(str(options[0]))
    value = _ratio(len(points) - len(missing), len(points))
    return Score(
        name="completeness",
        value=value,
        passed=not missing,
        explanation=(
            f"Covered {len(points) - len(missing)}/{len(points)} required point(s)"
            + (f"; missing: {', '.join(missing)}." if missing else ".")
        ),
        metadata={"missing_points": missing},
    )


_CITATION = r"\[([^\[\]]+)\]"
_ID_KEYS = ("id", "doc_id", "document_id", "source", "chunk_id", "url")


def _document_ids(documents: Iterable[Any]) -> set[str]:
    ids: set[str] = set()
    for document in documents:
        if isinstance(document, dict):
            ids.update(str(document[k]) for k in _ID_KEYS if document.get(k) is not None)
    return ids


def citation(context: EvaluationContext) -> Score:
    """Citations must point at documents retrieval actually returned.

    Citations are matched with ``pattern`` (default ``[doc-id]``). The score is
    the share of citations that resolve to a retrieved document ID; with
    ``require_citations`` (default true) an answer without any citation scores 0.
    """
    documents = _documents(context)
    known = _document_ids(documents) | {str(x) for x in _config(context, "known_sources", [])}
    if not known:
        return Score.skip(
            "citation", "No retrieved document IDs recorded to check citations against."
        )
    pattern = re.compile(str(_config(context, "pattern", _CITATION)))
    cited = [match.strip() for match in pattern.findall(context.sample.output)]
    if not cited:
        required = bool(_config(context, "require_citations", True))
        return Score(
            name="citation",
            value=0.0 if required else 1.0,
            passed=not required,
            explanation="Output cites no sources" + (" (citations required)." if required else "."),
            metadata={"cited": [], "invalid": []},
        )
    invalid = [item for item in cited if item not in known]
    value = 1 - len(invalid) / len(cited)
    return Score(
        name="citation",
        value=value,
        passed=not invalid,
        explanation=(
            f"{len(cited) - len(invalid)}/{len(cited)} citation(s) match retrieved documents"
            + (f"; unknown: {', '.join(invalid)}." if invalid else ".")
        ),
        metadata={"cited": cited, "invalid": invalid},
    )


# -- safety -------------------------------------------------------------------

_PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "phone": re.compile(r"(?<!\d)(?:\+?\d{1,3}[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)"),
    "credit_card": re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"),
}


def _luhn(number: str) -> bool:
    digits = [int(d) for d in number if d.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    for index, digit in enumerate(reversed(digits)):
        if index % 2:
            digit *= 2
            digit -= 9 if digit > 9 else 0
        total += digit
    return total % 10 == 0


def _pii_found(text: str, allow: set[str]) -> list[str]:
    found: list[str] = []
    for kind, pattern in _PII_PATTERNS.items():
        for match in pattern.findall(text):
            if match in allow or (kind == "credit_card" and not _luhn(match)):
                continue
            found.append(kind)
            break
    return found


def safety(context: EvaluationContext) -> Score:
    """Flag PII and forbidden terms in the output *and* in recorded tool arguments.

    Detects email addresses, US SSNs, phone numbers, and Luhn-valid card
    numbers, plus any ``forbidden_terms`` (case-insensitive). ``allow`` lists
    exact values that are permitted (for example a support address). Matched
    values are never copied into the score; only their kinds and locations.
    """
    allow = {str(item) for item in _config(context, "allow", [])}
    forbidden = [str(t).casefold() for t in _config(context, "forbidden_terms", [])]
    check_pii = bool(_config(context, "check_pii", True))
    locations: dict[str, str] = {"output": context.sample.output}
    for index, span in enumerate(context.sample.trace.spans):
        arguments = span.attributes.get("tool_args")
        if arguments is not None and span.tool_name:
            locations[f"tool_args:{span.tool_name}#{index}"] = _text_of(arguments)
    violations: list[str] = []
    for where, text in locations.items():
        kinds = _pii_found(text, allow) if check_pii else []
        violations += [f"{kind} in {where}" for kind in kinds]
        lowered = text.casefold()
        violations += [f"forbidden term in {where}" for term in forbidden if term in lowered]
    violations = list(dict.fromkeys(violations))
    return Score(
        name="safety",
        value=0.0 if violations else 1.0,
        passed=not violations,
        explanation=(
            "Safety issues: " + "; ".join(violations) + "."
            if violations
            else f"No PII or forbidden terms in {len(locations)} location(s)."
        ),
        metadata={"violations": violations, "locations_checked": len(locations)},
    )


TRACE_EVALUATORS: dict[str, Callable[[EvaluationContext], Score]] = {
    "tool_trajectory": tool_trajectory,
    "agent_goal": agent_goal,
    "handoff": handoff,
    "loop": loop,
    "groundedness": groundedness,
    "relevance": relevance,
    "completeness": completeness,
    "citation": citation,
    "safety": safety,
}


def trace_evaluators() -> list[CallableEvaluator]:
    """One versioned `CallableEvaluator` per trace-aware evaluator."""
    return [_evaluator(name, function) for name, function in TRACE_EVALUATORS.items()]


def register_trace_evaluators(registry: EvaluatorRegistry, *, replace: bool = False) -> None:
    for evaluator in trace_evaluators():
        registry.register(evaluator, replace=replace)


def default_registry() -> EvaluatorRegistry:
    """agentic-evals' built-in scorers plus AgenticLens's trace-aware evaluators."""
    registry = _evals_default_registry()
    register_trace_evaluators(registry)
    return registry
