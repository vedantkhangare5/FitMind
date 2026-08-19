import httpx

API_URL = "http://localhost:8000/api"

def main():
    with httpx.Client(base_url=API_URL) as client:
        # Register User A
        try:
            client.post("/auth/register", json={"email": "usera@example.com", "password": "Password123!"})
        except:
            pass
        
        # Login User A
        client.post("/auth/login", json={"email": "usera@example.com", "password": "Password123!"})
        
        # Profile A
        headers = {"X-FitMind-CSRF": "1"}
        client.put("/profile", json={
            "age": 25, "sex": "male", "height_cm": 175.0, "weight_kg": 70.0,
            "activity_level": "moderate", "goal": "maintain"
        }, headers=headers)
        
        client.post("/progress", json={"weight_kg": 70.0}, headers=headers)
        print("User A created.")

    with httpx.Client(base_url=API_URL) as client:
        # Register User B
        try:
            client.post("/auth/register", json={"email": "userb@example.com", "password": "Password123!"})
        except:
            pass
        
        # Login User B
        client.post("/auth/login", json={"email": "userb@example.com", "password": "Password123!"})
        
        # Profile B
        headers = {"X-FitMind-CSRF": "1"}
        client.put("/profile", json={
            "age": 30, "sex": "female", "height_cm": 160.0, "weight_kg": 65.0,
            "activity_level": "sedentary", "goal": "lose"
        }, headers=headers)
        
        client.post("/progress", json={"weight_kg": 65.0}, headers=headers)
        print("User B created.")

if __name__ == "__main__":
    main()
