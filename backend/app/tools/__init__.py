from app.tools.registry import ToolRegistry
from app.tools import fitness
from app.tools import rag
from app.tools import progress
from app.tools import behavior
from app.tools import schemas

# Global Tool Registry Instance
registry = ToolRegistry()

# Register Fitness Tools
registry.register(
    name="calculate_bmi",
    func=fitness.execute_calculate_bmi,
    input_schema=schemas.CalculateBMIInput
)
registry.register(
    name="calculate_bmr",
    func=fitness.execute_calculate_bmr,
    input_schema=schemas.CalculateBMRInput
)
registry.register(
    name="calculate_tdee",
    func=fitness.execute_calculate_tdee,
    input_schema=schemas.CalculateTDEEInput
)
registry.register(
    name="calculate_protein_target",
    func=fitness.execute_calculate_protein_target,
    input_schema=schemas.CalculateProteinTargetInput
)
registry.register(
    name="validate_calorie_target",
    func=fitness.execute_validate_calorie_target,
    input_schema=schemas.ValidateCalorieTargetInput
)

# Register RAG Tools
registry.register(
    name="search_knowledge",
    func=rag.execute_search_knowledge,
    input_schema=schemas.SearchKnowledgeInput
)

# Register Progress Tools
registry.register(
    name="get_progress_summary",
    func=progress.execute_get_progress_summary,
    input_schema=schemas.GetProgressSummaryInput
)

# Register Behavior Tools
registry.register(
    name="get_behavior_summary",
    func=behavior.execute_get_behavior_summary,
    input_schema=schemas.GetBehaviorSummaryInput
)

# Export Function Declarations for Gemini
tool_declarations = [
    schemas.calculate_bmi_declaration,
    schemas.calculate_bmr_declaration,
    schemas.calculate_tdee_declaration,
    schemas.calculate_protein_target_declaration,
    schemas.validate_calorie_target_declaration,
    schemas.search_knowledge_declaration,
    schemas.get_progress_summary_declaration,
    schemas.get_behavior_summary_declaration
]

__all__ = ["registry", "tool_declarations"]
