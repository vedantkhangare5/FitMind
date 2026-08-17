import pytest
from pydantic import BaseModel, ValidationError
from app.tools.registry import ToolRegistry

class DummyInput(BaseModel):
    value: int
    text: str

def dummy_tool(value: int, text: str):
    if value < 0:
        raise ValueError("Negative values are not allowed in this tool!")
    return f"{text}_{value}"

@pytest.fixture
def registry():
    reg = ToolRegistry()
    reg.register("dummy_tool", dummy_tool, DummyInput)
    return reg

def test_tool_registry_rejects_unlisted(registry):
    """Execution of an unlisted tool must return an explicit structural error, not throw an unhandled exception."""
    res = registry.execute("malicious_tool", {"foo": "bar"})
    assert res["success"] is False
    assert res["error"]["code"] == "UNKNOWN_TOOL"
    assert "malicious_tool" in res["error"]["message"]

def test_tool_registry_catches_malformed_arguments(registry):
    """Pydantic validation errors should be caught and returned as structural errors, without raw tracebacks."""
    res = registry.execute("dummy_tool", {"value": "not-a-number", "text": "hello"})
    assert res["success"] is False
    assert res["error"]["code"] == "INVALID_ARGUMENT"
    assert "value" in res["error"]["message"]

def test_tool_registry_catches_internal_exceptions(registry):
    """If a tool raises an internal Python exception, it should be caught and structured to avoid leaking stack traces to the LLM."""
    res = registry.execute("dummy_tool", {"value": -1, "text": "hello"})
    assert res["success"] is False
    assert res["error"]["code"] == "EXECUTION_ERROR"
    assert "Negative values" in res["error"]["message"]
