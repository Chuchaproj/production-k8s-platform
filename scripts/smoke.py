#!/usr/bin/env python3
import json
import os
import time
import urllib.request

base = os.getenv("BASE_URL", "http://127.0.0.1:8280")
for attempt in range(30):
    try:
        with urllib.request.urlopen(base + "/ready", timeout=5) as response:
            assert response.status == 200
        break
    except OSError:
        if attempt == 29:
            raise
        time.sleep(1)
request = urllib.request.Request(base + "/items", data=json.dumps({"name": "smoke"}).encode(),
                                 headers={"Content-Type": "application/json"})
with urllib.request.urlopen(request, timeout=5) as response:
    assert response.status == 201
with urllib.request.urlopen(base + "/items", timeout=5) as response:
    assert any(item["name"] == "smoke" for item in json.load(response))
print("REST readiness, write and read passed")
