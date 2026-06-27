from enum import Enum


class StepType(str, Enum):
    PLANNER = "planner"
    RETRIEVER = "retriever"
    TOOL_CALL = "tool_call"
    LLM_CALL = "llm_call"
    MEMORY = "memory"
    FINAL_RESPONSE = "final_response"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
