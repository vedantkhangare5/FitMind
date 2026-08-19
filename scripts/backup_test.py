import httpx

API_URL = "http://localhost:8000/api"

def main():
    print("Testing User A...")
    cookies_a = {}
    with httpx.Client(base_url=API_URL) as client_a:
        try:
            res_reg = client_a.post("/auth/register", json={"email": "usera100@example.com", "password": "Password123!"})
            print("Register A:", res_reg.status_code, res_reg.text)
        except Exception as e:
            print("Register exception:", e)
        res = client_a.post("/auth/login", json={"email": "usera100@example.com", "password": "Password123!"})
        print("Login A:", res.status_code, res.text)
        for c in res.headers.get_list("set-cookie"):
            name = c.split("=")[0]
            val = c.split("=")[1].split(";")[0]
            cookies_a[name] = val
        
        headers = {"X-FitMind-CSRF": cookies_a.get("csrf_token", "1")}
        res_prof_a = client_a.put("/profile", json={"age": 25, "sex": "male", "height_cm": 175.0, "weight_kg": 70.0, "activity_level": "moderately_active", "goal": "maintain"}, headers=headers, cookies=cookies_a)
        print("Profile A put:", res_prof_a.status_code, res_prof_a.text)
        
        client_a.post("/progress", json={"weight_kg": 70.0}, headers=headers, cookies=cookies_a)
        client_a.post("/behavior/nutrition", json={"date": "2026-08-19", "calories": 2500, "protein_g": 150}, headers=headers, cookies=cookies_a)
        prof_a = client_a.get("/profile", cookies=cookies_a).json()
        print(f"User A Profile: {prof_a}")
        
    print("Testing User B...")
    cookies_b = {}
    with httpx.Client(base_url=API_URL) as client_b:
        try:
            client_b.post("/auth/register", json={"email": "userb100@example.com", "password": "Password123!"})
        except:
            pass
        res = client_b.post("/auth/login", json={"email": "userb100@example.com", "password": "Password123!"})
        for c in res.headers.get_list("set-cookie"):
            name = c.split("=")[0]
            val = c.split("=")[1].split(";")[0]
            cookies_b[name] = val
        
        headers = {"X-FitMind-CSRF": cookies_b.get("csrf_token", "1")}
        client_b.put("/profile", json={"age": 30, "sex": "female", "height_cm": 160.0, "weight_kg": 65.0, "activity_level": "sedentary", "goal": "lose_fat"}, headers=headers, cookies=cookies_b)
        client_b.post("/progress", json={"weight_kg": 65.0}, headers=headers, cookies=cookies_b)
        prof_b = client_b.get("/profile", cookies=cookies_b).json()
        print(f"User B Profile: {prof_b}")
        
        # Test cross-user pollution
        print("Testing A/B Isolation...")
        if prof_a.get("profile", {}).get("age") != 25 or prof_b.get("profile", {}).get("age") != 30:
            raise Exception(f"Isolation failure! A: {prof_a}, B: {prof_b}")
            
    print("Health check...")
    res = httpx.get(f"{API_URL}/health")
    print(f"Health: {res.json()}")

if __name__ == "__main__":
    main()
