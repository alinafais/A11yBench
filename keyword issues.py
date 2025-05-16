import requests
import time

GITHUB_TOKEN = ""

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

keywords = [
    "accessibility",
    "a11y",
    "ally",
    '"accessibility" OR "a11y"',
    '"accessibility" OR "ally"',
    '"accessibility" OR "ally" OR "a11y"'
]

results = {}

for keyword in keywords:
    query = f'{keyword} is:issue'
    print(f"Querying: {query}")
    url = "https://api.github.com/search/issues"
    params = {
        "q": query,
        "per_page": 1 
    }

    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 403 and "rate limit" in response.text.lower():
            print("Rate limit hit. sleeping for 60 seconds...")
            time.sleep(60)
            continue
        elif response.status_code != 200:
            print(f"Failed: {response.status_code} - {response.text}")
            results[keyword] = None
            break

        data = response.json()
        results[keyword] = data.get("total_count", 0)
        break

print("\n=== Keyword Issue Counts ===")
for keyword, count in results.items():
    print(f"{keyword:40} -> {count} issues")
