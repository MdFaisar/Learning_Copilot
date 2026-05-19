import requests
import json

BASE_URL = 'http://localhost:5000/api/code'

def test_explain_code():
    print("\nTesting POST /explain (AI)...")
    payload = {
        "language": "python",
        "code": "print('Hello from Verification Script')",
        "output": "Hello from Verification Script"
    }
    try:
        res = requests.post(f'{BASE_URL}/explain', json=payload)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if data.get('success'):
                # Avoid printing entire analysis as it might be long
                print("Explanation received (preview):", data.get('explanation')[:100] + "...")
            else:
                print("Explanation failed:", data.get('error'))
        else:
            print("Error:", res.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_explain_code()
