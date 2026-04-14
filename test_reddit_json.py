import requests

def test_reddit():
    url = "https://www.reddit.com/r/forhire/new.json"
    headers = {
        "User-Agent": "python:lead-gen-app:v1.0 (by /u/testuser)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data['data']['children'])} posts")
            print(f"First post title: {data['data']['children'][0]['data']['title']}")
        else:
            print(response.text[:200])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_reddit()
