import requests
import json

BASE_URL = 'http://localhost:5000/api/code'

def test_languages():
    print("Testing GET /languages...")
    try:
        res = requests.get(f'{BASE_URL}/languages')
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Languages found:", len(res.json().get('languages', [])))
        else:
            print("Error:", res.text)
    except Exception as e:
        print(f"Request failed: {e}")

def test_execute():
    print("\nTesting POST /execute (Python)...")
    payload = {
        "language": "python",
        "code": "print('Hello from Verification Script')",
        "input": ""
    }
    try:
        res = requests.post(f'{BASE_URL}/execute', json=payload)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if data.get('success'):
                print("Result:", data.get('result'))
            else:
                print("Execution failed:", data.get('error'))
        else:
            print("Error:", res.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_languages()
    test_execute()
