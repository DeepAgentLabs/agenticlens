import time
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import Any, Literal

from agenticlens.instrumentation.redaction import Redactor, redact_sensitive
from agenticlens.models.trace import Run, RunStatus, Span, SpanType

_current_trace: ContextVar["trace | None"] = ContextVar("current_trace", default=None)
_current_span: ContextVar[Span | None] = ContextVar("current_span", default=None)


class SpanHandle:
    def __init__(self, span: Span, redactor: Redactor) -> None:
        self.span = span
        self._redactor = redactor

    def record_tokens(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.span.input_tokens = input_tokens
        self.span.output_tokens = output_tokens

    def record_cost(self, estimated_cost_usd: float) -> None:
        self.span.estimated_cost_usd = estimated_cost_usd

    def set_attribute(self, name: str, value: Any) -> None:
        self.span.attributes[name] = self._redactor(value)

    def record_io(self, *, input_data: Any = None, output_data: Any = None) -> None:
        """Capture input/output only when explicitly requested by the caller."""
        self.span.input_data = self._redactor(input_data)
        self.span.output_data = self._redactor(output_data)


class SpanContext:
    def __init__(self, owner: "trace", name: str, span_type: SpanType | str, **attributes: Any):
        self.owner = owner
        self.name = name
        self.span_type = SpanType(span_type)
        self.attributes = attributes
        self.model: Span | None = None
        self._token: Token[Span | None] | None = None
        self._started = 0.0

    def __enter__(self) -> SpanHandle:
        parent = _current_span.get()
        self.model = Span(
            name=self.name,
            span_type=self.span_type,
            parent_span_id=parent.span_id if parent else None,
            attributes=self.owner.redactor(self.attributes),
        )
        self.owner.run.spans.append(self.model)
        self._token = _current_span.set(self.model)
        self._started = time.perf_counter()
        return SpanHandle(self.model, self.owner.redactor)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        assert self.model is not None and self._token is not None
        self.model.completed_at = datetime.now(timezone.utc)
        self.model.latency_ms = (time.perf_counter() - self._started) * 1000
        if exc_type is None:
            self.model.status = RunStatus.SUCCEEDED
        else:
            self.model.status = RunStatus.FAILED
            self.model.error_type = exc_type.__name__
            self.model.error_message = str(exc_value)
        _current_span.reset(self._token)
        return False


class trace:  # noqa: N801
    def __init__(
        self,
        application_name: str,
        *,
        redactor: Redactor = redact_sensitive,
        **metadata: Any,
    ) -> None:
        self.redactor = redactor
        self.run = Run(application_name=application_name, metadata=redactor(metadata))
        self._token: Token[trace | None] | None = None

    def __enter__(self) -> "trace":
        if _current_trace.get() is not None:
            raise RuntimeError("Nested trace() blocks are not supported.")
        self._token = _current_trace.set(self)
        return self

    def span(
        self,
        name: str,
        span_type: SpanType | str = SpanType.CUSTOM,
        **attributes: Any,
    ) -> SpanContext:
        return SpanContext(self, name, span_type, **attributes)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.run.model_dump_json(indent=2), encoding="utf-8")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        assert self._token is not None
        self.run.completed_at = datetime.now(timezone.utc)
        self.run.status = RunStatus.SUCCEEDED if exc_type is None else RunStatus.FAILED
        self.run.task_success = exc_type is None
        if exc_type is not None:
            self.run.error_type = exc_type.__name__
        _current_trace.reset(self._token)
        return False
