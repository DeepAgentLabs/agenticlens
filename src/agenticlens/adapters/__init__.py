"""Optional auto-instrumentation adapters for third-party agent frameworks.

Adapters are not imported here so that `agenticlens` itself never requires
the frameworks they integrate with. Import the specific adapter module you
need, e.g. `from agenticlens.adapters.langchain import AgenticLensCallbackHandler`.
"""
