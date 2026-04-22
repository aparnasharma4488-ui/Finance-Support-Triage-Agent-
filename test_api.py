import requests

try:
    print("Testing Health Endpoint...")
    r = requests.get("http://127.0.0.1:8000/health")
    print(r.json())

    print("\nTesting Triage Endpoint with Indian Currency...")
    r2 = requests.post("http://127.0.0.1:8000/api/triage", json={"message": "Urgent: I noticed an unauthorized charge of ₹20,000 on my account 9912 today, please investigate this fraud immediately."})
    print(r2.json())
    
    print("\nTests passed!")
except Exception as e:
    print(f"Error testing server: {e}")
