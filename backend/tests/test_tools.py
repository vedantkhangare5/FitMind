import pytest
from app.tools.registry import ToolRegistry
from pydantic import BaseModel, Field

class MockSchema(BaseModel):
    x: int
    y: int

def mock_tool_func(x: int, y: int):
    if x < 0:
        raise ValueError("x cannot be negative")
    return {"result": x + y}

@pytest.fixture
def test_registry():
    r = ToolRegistry()
    r.register("mock_tool", mock_tool_func, MockSchema)
    return r

def test_unknown_tool_rejected(test_registry):
    res = test_registry.execute("does_not_exist", {"x": 1})
    assert res["success"] is False
    assert res["error"]["code"] == "UNKNOWN_TOOL"
    assert "does_not_exist" in res["error"]["message"]

def test_malformed_arguments_rejected(test_registry):
    # Missing required 'y', and 'x' is invalid type
    res = test_registry.execute("mock_tool", {"x": "not_an_int"})
    assert res["success"] is False
    assert res["error"]["code"] == "INVALID_ARGUMENT"
    # Should not have reached the function

def test_successful_execution(test_registry):
    res = test_registry.execute("mock_tool", {"x": 5, "y": 10})
    assert res["success"] is True
    assert res["error"] is None
    assert res["data"]["result"] == 15

def test_execution_error_caught_no_stack_trace_leak(test_registry):
    # Function throws ValueError for x < 0
    res = test_registry.execute("mock_tool", {"x": -1, "y": 10})
    assert res["success"] is False
    assert res["error"]["code"] == "EXECUTION_ERROR"
    assert "x cannot be negative" in res["error"]["message"]
    assert "Traceback" not in res["error"]["message"]

def test_calculate_tdee_does_not_accept_bmr():
    from app.tools.schemas import CalculateTDEEInput
    # Verify bmr is not part of the schema
    assert "bmr" not in CalculateTDEEInput.model_fields
    
    # Verify the schema requires weight, height, age, sex, activity_level
    fields = CalculateTDEEInput.model_fields.keys()
    assert "weight_kg" in fields
    assert "height_cm" in fields
    assert "age" in fields
    assert "sex" in fields
    assert "activity_level" in fields

def test_calculate_tdee_uses_internal_bmr(mocker):
    # We want to ensure calculate_tdee calls calc_bmr internally
    import app.tools.fitness as fitness
    
    spy_bmr = mocker.spy(fitness, "calc_bmr")
    spy_tdee = mocker.spy(fitness, "calc_tdee")
    
    res = fitness.execute_calculate_tdee(
        weight_kg=70, height_cm=175, age=30, sex="male", activity_level="sedentary"
    )
    
    # Verify internal calls were made
    spy_bmr.assert_called_once_with(70, 175, 30, "male")
    
    # Get the bmr that was calculated
    calculated_bmr = spy_bmr.spy_return
    spy_tdee.assert_called_once_with(calculated_bmr, "sedentary")
    
    assert res["bmr_used"] == calculated_bmr

def test_validate_calorie_target_uses_internal_bmr_and_tdee(mocker):
    import app.tools.fitness as fitness
    
    spy_bmr = mocker.spy(fitness, "calc_bmr")
    spy_tdee = mocker.spy(fitness, "calc_tdee")
    spy_validate = mocker.spy(fitness, "val_calorie_target")
    
    res = fitness.execute_validate_calorie_target(
        target=1500, weight_kg=70, height_cm=175, age=30, sex="male", activity_level="sedentary"
    )
    
    spy_bmr.assert_called_once_with(70, 175, 30, "male")
    calculated_bmr = spy_bmr.spy_return
    spy_tdee.assert_called_once_with(calculated_bmr, "sedentary")
    calculated_tdee = spy_tdee.spy_return
    spy_validate.assert_called_once_with(1500, calculated_tdee)
    
    assert res["tdee_used"] == calculated_tdee
