import requests
import json
import time
from datetime import datetime, timedelta

GITHUB_TOKEN = ""  

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

# Query templates with variations
query_templates = {
    "open_issues": 'accessibility label:"good first issue" is:open is:issue created:{start}..{end}',
    "all_issues": 'accessibility label:"good first issue" created:{start}..{end}',
    # "open_issues_alt": 'accessibility label:"good-first-issue" is:open is:issue created:{start}..{end}',
    # "all_issues_alt": 'accessibility label:"good-first-issue" created:{start}..{end}'
}

# Time range (extending as needed)
# this is created between October 1, 2023 and May 1, 2024 (in 15-day chunks)
start_date = datetime(2023, 10, 1)
end_date = datetime(2024, 5, 1)
step = timedelta(days=15)

all_issues = []
seen = set()

try:
    for variant, query_template in query_templates.items():
        print(f"\nRunning query variant: {variant}")

        current_start = start_date
        while current_start < end_date:
            current_end = min(current_start + step, end_date)
            date_range = f"{current_start.date()}..{current_end.date()}"
            query = query_template.format(start=current_start.date(), end=current_end.date())

            print(f"Date Range: {date_range}")
            page = 1

            while True:
                params = {
                    "q": query,
                    "per_page": 100,
                    "page": page,
                    "sort": "created",
                    "order": "desc"
                }

                try:
                    response = requests.get("https://api.github.com/search/issues",
                                            headers=headers, params=params, timeout=10)
                except requests.exceptions.Timeout:
                    print("Request timed out. Skipping this page.")
                    break

                if response.status_code == 403 and "rate limit" in response.text.lower():
                    print("Rate limit hit, sleeping for 60 seconds...")
                    time.sleep(60)
                    continue
                elif response.status_code != 200:
                    print(f"Error {response.status_code}: {response.text}")
                    break

                items = response.json().get("items", [])
                print(f"Page {page}: {len(items)} issues")

                if not items:
                    break

                for issue in items:
                    if issue['html_url'] not in seen:
                        seen.add(issue['html_url'])
                        repo = "/".join(issue['repository_url'].split('/')[-2:])
                        all_issues.append({
                            "title": issue["title"],
                            "url": issue["html_url"],
                            "repository": repo,
                            "created_at": issue["created_at"],
                            "state": issue["state"],
                            "labels": [label["name"] for label in issue["labels"]],
                            "body": issue["body"],
                            "query_variant": variant,
                            "date_chunk": date_range
                        })

                if len(items) < 100:
                    break

                page += 1
                time.sleep(1)

            current_start = current_end
            time.sleep(1)

except KeyboardInterrupt:
    print("\nInterrupted by user.")

# Save results
with open("github_accessibility_issues.json", "w", encoding="utf-8") as f:
    json.dump(all_issues, f, indent=4)

print(f"\nFinished. Saved {len(all_issues)} unique issues to github_accessibility_issues.json.")
