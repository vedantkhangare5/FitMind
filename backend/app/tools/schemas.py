from typing import Optional, Literal
from pydantic import BaseModel, Field
from google.genai.types import FunctionDeclaration, Type, Schema

# ==============================================================================
# PYDANTIC INPUT SCHEMAS (Runtime Validation)
# ==============================================================================

class CalculateBMIInput(BaseModel):
    weight_kg: float = Field(..., gt=10, lt=400)
    height_cm: float = Field(..., gt=50, lt=300)

class CalculateBMRInput(BaseModel):
    weight_kg: float = Field(..., gt=10, lt=400)
    height_cm: float = Field(..., gt=50, lt=300)
    age: int = Field(..., gt=0, lt=120)
    sex: Literal["male", "female"]

class CalculateTDEEInput(BaseModel):
    weight_kg: float = Field(..., gt=10, lt=400)
    height_cm: float = Field(..., gt=50, lt=300)
    age: int = Field(..., gt=0, lt=120)
    sex: Literal["male", "female"]
    activity_level: Literal["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"]

class CalculateProteinTargetInput(BaseModel):
    weight_kg: float = Field(..., gt=10, lt=400)
    goal: Literal["lose_fat", "maintain", "build_muscle"]

class ValidateCalorieTargetInput(BaseModel):
    target: int = Field(..., gt=500, lt=10000)
    weight_kg: float = Field(..., gt=10, lt=400)
    height_cm: float = Field(..., gt=50, lt=300)
    age: int = Field(..., gt=0, lt=120)
    sex: Literal["male", "female"]
    activity_level: Literal["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"]

class SearchKnowledgeInput(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=50)


class GetProgressSummaryInput(BaseModel):
    pass

# ==============================================================================
# GEMINI FUNCTION DECLARATIONS
# ==============================================================================

calculate_bmi_declaration = FunctionDeclaration(
    name="calculate_bmi",
    description="Calculates Body Mass Index (BMI) and provides a contextual weight category. Use this when you need to determine a user's BMI based on their weight and height.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "weight_kg": Schema(type=Type.NUMBER, description="Weight in kilograms"),
            "height_cm": Schema(type=Type.NUMBER, description="Height in centimeters"),
        },
        required=["weight_kg", "height_cm"]
    )
)

calculate_bmr_declaration = FunctionDeclaration(
    name="calculate_bmr",
    description="Calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation. Use this to find out how many calories a user burns at rest.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "weight_kg": Schema(type=Type.NUMBER, description="Weight in kilograms"),
            "height_cm": Schema(type=Type.NUMBER, description="Height in centimeters"),
            "age": Schema(type=Type.INTEGER, description="Age in years"),
            "sex": Schema(type=Type.STRING, description="Biological sex for the calculation ('male' or 'female')"),
        },
        required=["weight_kg", "height_cm", "age", "sex"]
    )
)

calculate_tdee_declaration = FunctionDeclaration(
    name="calculate_tdee",
    description="Calculates Total Daily Energy Expenditure (TDEE). Use this to determine total daily calories burned factoring in activity levels.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "weight_kg": Schema(type=Type.NUMBER, description="Weight in kilograms"),
            "height_cm": Schema(type=Type.NUMBER, description="Height in centimeters"),
            "age": Schema(type=Type.INTEGER, description="Age in years"),
            "sex": Schema(type=Type.STRING, description="Biological sex ('male' or 'female')"),
            "activity_level": Schema(type=Type.STRING, description="Activity level ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active')"),
        },
        required=["weight_kg", "height_cm", "age", "sex", "activity_level"]
    )
)

calculate_protein_target_declaration = FunctionDeclaration(
    name="calculate_protein_target",
    description="Calculates recommended daily protein targets in grams based on weight and fitness goal. Use this to advise on macronutrient targets.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "weight_kg": Schema(type=Type.NUMBER, description="Weight in kilograms"),
            "goal": Schema(type=Type.STRING, description="Fitness goal ('lose_fat', 'maintain', 'build_muscle')"),
        },
        required=["weight_kg", "goal"]
    )
)

validate_calorie_target_declaration = FunctionDeclaration(
    name="validate_calorie_target",
    description="Validates a proposed calorie target against TDEE to check for safety heuristics (e.g., excessively aggressive deficit). Use this before recommending a calorie deficit.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "target": Schema(type=Type.INTEGER, description="Proposed daily calorie target"),
            "weight_kg": Schema(type=Type.NUMBER, description="Weight in kilograms"),
            "height_cm": Schema(type=Type.NUMBER, description="Height in centimeters"),
            "age": Schema(type=Type.INTEGER, description="Age in years"),
            "sex": Schema(type=Type.STRING, description="Biological sex ('male' or 'female')"),
            "activity_level": Schema(type=Type.STRING, description="Activity level ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active')"),
        },
        required=["target", "weight_kg", "height_cm", "age", "sex", "activity_level"]
    )
)

search_knowledge_declaration = FunctionDeclaration(
    name="search_knowledge",
    description="Searches the FitMind knowledge base for evidence-based fitness and nutrition information. Use this to retrieve facts before answering scientific or health-related user queries.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "query": Schema(type=Type.STRING, description="The search query"),
            "top_k": Schema(type=Type.INTEGER, description="Number of results to retrieve (default 5)"),
        },
        required=["query"]
    )
)

get_progress_summary_declaration = FunctionDeclaration(
    name="get_progress_summary",
    description="Retrieves the user's historical progress summary (current weight, starting weight, total change, percentage change, and trend). Use this when the user asks about their past progress or weight trend. Do not calculate trends yourself; use this tool.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={},
        required=[]
    )
)
