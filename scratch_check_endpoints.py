import requests

endpoints = [
    ("GET", "/frameworks"),
    ("GET", "/db/status"),
    ("GET", "/suggestions"),
    ("GET", "/documents/stats"),
    # ("/analyse/nlp-cluster") # might be slow
    ("GET", "/analyse/summary"),
    ("GET", "/analyse/agrontology-summary"),
    ("GET", "/analyse/design-summary"),
    ("GET", "/analyse/agrontology-design-summary")
]

base_url = "http://localhost:8000"
results = {}

for method, path in endpoints:
    url = f"{base_url}{path}"
    try:
        if method == "GET":
            res = requests.get(url, timeout=5)
        elif method == "POST":
            res = requests.post(url, timeout=5)
        results[path] = {"status_code": res.status_code, "ok": res.ok}
    except Exception as e:
        results[path] = {"error": str(e)}

import json
print(json.dumps(results, indent=2))
