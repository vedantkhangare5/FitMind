from app.calculators import (
    calculate_bmi as calc_bmi,
    calculate_bmr as calc_bmr,
    calculate_tdee as calc_tdee,
    calculate_protein_target as calc_protein_target,
    validate_calorie_target as val_calorie_target,
    ACTIVITY_MULTIPLIERS
)

def execute_calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    bmi, category = calc_bmi(weight_kg, height_cm)
    return {
        "bmi": bmi,
        "bmi_category": category
    }

def execute_calculate_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> dict:
    bmr = calc_bmr(weight_kg, height_cm, age, sex)
    return {
        "bmr": bmr
    }

def execute_calculate_tdee(weight_kg: float, height_cm: float, age: int, sex: str, activity_level: str) -> dict:
    bmr = calc_bmr(weight_kg, height_cm, age, sex)
    tdee = calc_tdee(bmr, activity_level)
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return {
        "tdee": tdee,
        "activity_multiplier": multiplier,
        "bmr_used": bmr
    }

def execute_calculate_protein_target(weight_kg: float, goal: str) -> dict:
    min_tgt, max_tgt = calc_protein_target(weight_kg, goal)
    return {
        "protein_target_min": min_tgt,
        "protein_target_max": max_tgt
    }

def execute_validate_calorie_target(target: int, weight_kg: float, height_cm: float, age: int, sex: str, activity_level: str) -> dict:
    bmr = calc_bmr(weight_kg, height_cm, age, sex)
    tdee = calc_tdee(bmr, activity_level)
    warnings = val_calorie_target(target, tdee)
    return {
        "warnings": warnings,
        "tdee_used": tdee
    }
