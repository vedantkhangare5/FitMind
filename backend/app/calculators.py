"""
Deterministic fitness calculation engine.
All formulas are based on established scientific equations or configurable application defaults.
NO LLM is used here.
"""
from typing import Tuple, List

# --- Activity Multipliers ---
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}

# --- Calorie Adjustments by Goal (Configurable Application Defaults) ---
# Note: Actual weight change varies between individuals and over time.
CALORIE_ADJUSTMENTS = {
    "lose_fat": -500,
    "maintain": 0,
    "build_muscle": 300,
}

# --- Protein Ranges (g/kg of body weight) ---
# Application defaults intended to support various contexts. 
# These are not universally optimal or medical prescriptions.
PROTEIN_RANGES = {
    "lose_fat": (1.6, 2.2),
    "maintain": (1.2, 1.6),
    "build_muscle": (1.6, 2.0),
}


def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
    """Calculates BMI and returns (numerical_bmi, category_string)."""
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)
    
    # Contextual screening categories (WHO)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
        
    return round(bmi, 1), category


def calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> int:
    """
    Calculates BMR using the Mifflin-St Jeor equation.
    A commonly used predictive equation for estimating resting energy expenditure in adults.
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if sex == "male":
        bmr = base + 5
    else:  # female
        bmr = base - 161
        
    return int(round(bmr))


def calculate_tdee(bmr: int, activity_level: str) -> int:
    """Calculates TDEE based on BMR and activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return int(round(bmr * multiplier))


def calculate_calorie_target(tdee: int, goal: str) -> int:
    """Calculates the daily calorie target based on goal application defaults."""
    adjustment = CALORIE_ADJUSTMENTS.get(goal, 0)
    return tdee + adjustment


def calculate_protein_target(weight_kg: float, goal: str) -> Tuple[int, int]:
    """Calculates a protein target range based on goal."""
    min_mult, max_mult = PROTEIN_RANGES.get(goal, (1.2, 1.6))
    return int(round(weight_kg * min_mult)), int(round(weight_kg * max_mult))


def validate_calorie_target(target: int, tdee: int) -> List[str]:
    """
    Validates calorie targets to catch unusually aggressive deficits.
    Returns a list of warnings if any safety heuristics are triggered.
    Does NOT modify the target or enforce a hard floor.
    """
    warnings = []
    
    # Isolated heuristic: Warn if the deficit is greater than 30% of TDEE
    if target < (tdee * 0.7):
        warnings.append(
            "Calculated calorie target reflects an unusually aggressive deficit. "
            "Please consult a healthcare professional before pursuing extreme calorie restriction."
        )
        
    return warnings


def generate_fitness_summary(
    age: int, sex: str, height_cm: float, weight_kg: float, activity_level: str, goal: str
) -> dict:
    """Executes the full suite of fitness calculations and returns a structured dictionary."""
    bmi, bmi_category = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(weight_kg, height_cm, age, sex)
    tdee = calculate_tdee(bmr, activity_level)
    calorie_target = calculate_calorie_target(tdee, goal)
    protein_min, protein_max = calculate_protein_target(weight_kg, goal)
    warnings = validate_calorie_target(calorie_target, tdee)
    
    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": calorie_target,
        "protein_target_min": protein_min,
        "protein_target_max": protein_max,
        "warnings": warnings
    }
