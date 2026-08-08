import pytest
from app.calculators import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_calorie_target,
    calculate_protein_target,
    validate_calorie_target,
)


def test_calculate_bmi():
    # Normal weight
    bmi, cat = calculate_bmi(70, 175)
    assert bmi == 22.9
    assert cat == "Normal weight"

    # Underweight
    bmi, cat = calculate_bmi(50, 175)
    assert bmi == 16.3
    assert cat == "Underweight"

    # Overweight
    bmi, cat = calculate_bmi(85, 175)
    assert bmi == 27.8
    assert cat == "Overweight"


def test_calculate_bmr():
    # Male: (10*80) + (6.25*180) - (5*30) + 5 = 800 + 1125 - 150 + 5 = 1780
    assert calculate_bmr(80, 180, 30, "male") == 1780
    
    # Female: (10*60) + (6.25*165) - (5*25) - 161 = 600 + 1031.25 - 125 - 161 = 1345
    assert calculate_bmr(60, 165, 25, "female") == 1345


def test_calculate_tdee():
    bmr = 1500
    assert calculate_tdee(bmr, "sedentary") == 1800  # 1500 * 1.2
    assert calculate_tdee(bmr, "lightly_active") == 2062  # 1500 * 1.375
    assert calculate_tdee(bmr, "moderately_active") == 2325  # 1500 * 1.55
    assert calculate_tdee(bmr, "very_active") == 2588  # 1500 * 1.725
    assert calculate_tdee(bmr, "extra_active") == 2850  # 1500 * 1.9
    # Fallback default (sedentary)
    assert calculate_tdee(bmr, "unknown_level") == 1800


def test_calculate_calorie_target():
    tdee = 2500
    assert calculate_calorie_target(tdee, "lose_fat") == 2000
    assert calculate_calorie_target(tdee, "maintain") == 2500
    assert calculate_calorie_target(tdee, "build_muscle") == 2800
    # Fallback default
    assert calculate_calorie_target(tdee, "unknown") == 2500


def test_calculate_protein_target():
    weight = 70.0
    # Lose fat: 1.6 - 2.2 -> 112 - 154
    min_p, max_p = calculate_protein_target(weight, "lose_fat")
    assert min_p == 112
    assert max_p == 154
    
    # Maintain: 1.2 - 1.6 -> 84 - 112
    min_p, max_p = calculate_protein_target(weight, "maintain")
    assert min_p == 84
    assert max_p == 112
    
    # Build muscle: 1.6 - 2.0 -> 112 - 140
    min_p, max_p = calculate_protein_target(weight, "build_muscle")
    assert min_p == 112
    assert max_p == 140


def test_validate_calorie_target():
    # Normal target (e.g. 2500 TDEE, 2000 target -> > 70%)
    warnings = validate_calorie_target(2000, 2500)
    assert len(warnings) == 0

    # Unusually aggressive deficit (< 70% of TDEE)
    warnings = validate_calorie_target(1500, 2500) # 1500 / 2500 = 60%
    assert len(warnings) == 1
    assert "unusually aggressive deficit" in warnings[0]
