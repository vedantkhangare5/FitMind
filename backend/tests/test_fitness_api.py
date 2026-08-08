from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

valid_payload = {
    "age": 30,
    "sex": "male",
    "height_cm": 180,
    "weight_kg": 80,
    "activity_level": "moderately_active",
    "goal": "lose_fat"
}


def test_calculate_fitness_success():
    response = client.post("/api/fitness/calculate", json=valid_payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "bmi" in data
    assert "bmi_category" in data
    assert "bmr" in data
    assert "tdee" in data
    assert "calorie_target" in data
    assert "protein_target_min" in data
    assert "protein_target_max" in data
    assert "warnings" in data
    
    # Check specific deterministic math based on the payload
    # BMR: (10*80) + (6.25*180) - (5*30) + 5 = 1780
    assert data["bmr"] == 1780
    # TDEE: 1780 * 1.55 = 2759
    assert data["tdee"] == 2759
    # Calorie Target: 2759 - 500 = 2259
    assert data["calorie_target"] == 2259


def test_calculate_fitness_invalid_input():
    invalid_payload = {
        "age": -5,  # Invalid
        "sex": "alien", # Invalid
        "height_cm": 0, # Invalid
        "weight_kg": -10, # Invalid
        "activity_level": "super_hero", # Invalid
        "goal": "fly" # Invalid
    }
    response = client.post("/api/fitness/calculate", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Ensure there are multiple validation errors caught by Pydantic
    assert len(data["detail"]) > 1


def test_calculate_fitness_aggressive_deficit_warning():
    # If someone has a massive TDEE but wants to lose fat, and the manual 
    # configuration implies a severe deficit, they should get a warning.
    # To force the warning (target < 70% of TDEE), let's artificially 
    # test a case where we simulate a huge deficit. Since our logic is static
    # -500 kcal, it's hard to hit <70% for large TDEEs, but what if TDEE is very low?
    # BMR: 10*40 + 6.25*140 - 5*60 - 161 = 400 + 875 - 300 - 161 = 814
    # TDEE: 814 * 1.2 = 977
    # Target: 977 - 500 = 477. 
    # 477 < 977 * 0.7 (which is 683). Warning should trigger!
    
    small_person = {
        "age": 60,
        "sex": "female",
        "height_cm": 140,
        "weight_kg": 40,
        "activity_level": "sedentary",
        "goal": "lose_fat"
    }
    response = client.post("/api/fitness/calculate", json=small_person)
    assert response.status_code == 200
    data = response.json()
    assert len(data["warnings"]) == 1
    assert "unusually aggressive deficit" in data["warnings"][0]
