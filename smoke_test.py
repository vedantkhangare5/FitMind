import os
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://api.localhost/api"
VERIFY = False

user_a_email = "usera3@example.com"
user_a_password = "passwordA123!"
user_b_email = "userb3@example.com"
user_b_password = "passwordB123!"

def register(session, email, password):
    r = session.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password}, verify=VERIFY)
    if r.status_code != 409:
        r.raise_for_status()

def login(session, email, password):
    r = session.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password}, verify=VERIFY)
    r.raise_for_status()

session_a = requests.Session()
session_a.headers.update({"X-FitMind-CSRF": "1"})
session_b = requests.Session()
session_b.headers.update({"X-FitMind-CSRF": "1"})

print("Registering User A...")
register(session_a, user_a_email, user_a_password)
login(session_a, user_a_email, user_a_password)

print("Registering User B...")
register(session_b, user_b_email, user_b_password)
login(session_b, user_b_email, user_b_password)

print("Creating Profile for User A...")
profile_data = {"age": 30, "sex": "male", "height_cm": 180.0, "weight_kg": 75.0, "activity_level": "moderate", "goal": "maintain"}
r = session_a.put(f"{BASE_URL}/profile", json=profile_data, verify=VERIFY)
r.raise_for_status()

print("Creating Progress for User A...")
progress_data = {"weight_kg": 74.5, "recorded_at": "2026-08-19T10:00:00Z"}
r = session_a.post(f"{BASE_URL}/progress", json=progress_data, verify=VERIFY)
r.raise_for_status()

print("Testing Isolation...")
r = session_a.get(f"{BASE_URL}/profile", verify=VERIFY)
assert r.status_code == 200

r = session_b.get(f"{BASE_URL}/profile", verify=VERIFY)
assert r.status_code == 404 or (r.status_code == 200 and r.json() is None)

print("Smoke test and A/B isolation test passed successfully.")
