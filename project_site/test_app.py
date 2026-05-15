import urllib.request, json

base = "http://127.0.0.1:8000"
ok = True

def check(label, condition, detail=""):
    global ok
    status = "PASS" if condition else "FAIL"
    if not condition:
        ok = False
    print(f"  [{status}] {label}{(' | ' + detail) if detail else ''}")

# 1. Homepage
req = urllib.request.urlopen(base + "/")
body = req.read().decode()
check("GET /  -> 200", req.status == 200)
check("HTML contains NexValo title", "NexValo" in body)
check("HTML contains agent-grid", "agent-grid" in body)
check("HTML contains console-body", "console-body" in body)

# 2. Cache status (empty)
req = urllib.request.urlopen(base + "/api/cache/status")
data = json.loads(req.read())
check("GET /api/cache/status -> 200", req.status == 200)
check("locked_agent is None initially", data["locked_agent"] is None)

# 3. Lock agent
payload = json.dumps({"agent_id": "jett", "agent_name": "Jett", "agent_role": "Duelist"}).encode()
req = urllib.request.urlopen(urllib.request.Request(
    base + "/api/cache/lock-agent", data=payload,
    headers={"Content-Type": "application/json"}, method="POST"
))
data = json.loads(req.read())
check("POST /api/cache/lock-agent -> 200", req.status == 200)
check("Locked agent is Jett", data["locked_agent"]["agent_name"] == "Jett")

# 4. Cache status after lock
req = urllib.request.urlopen(base + "/api/cache/status")
data = json.loads(req.read())
check("Cache has locked_agent after lock", data["locked_agent"] is not None)
check("locked_agent name == Jett", data["locked_agent"]["agent_name"] == "Jett")
check("Cache entries >= 1", data["total_entries"] >= 1)

# 5. Vanguard scan - valid token
payload = json.dumps({"token": "VANGUARD-7749-NEXVALO"}).encode()
req = urllib.request.urlopen(urllib.request.Request(
    base + "/api/security/scan", data=payload,
    headers={"Content-Type": "application/json"}, method="POST"
))
data = json.loads(req.read())
check("POST /api/security/scan (valid) -> 200", req.status == 200)
check("authorized == True", data["authorized"] is True)
check("integrity between 94-100", 94 <= data["integrity"] <= 100, str(data["integrity"]))
check("status is CLEAN or WARNING", data["status"] in ("CLEAN", "WARNING"))

# 6. Vanguard scan - invalid token
payload = json.dumps({"token": "WRONG-TOKEN"}).encode()
req = urllib.request.urlopen(urllib.request.Request(
    base + "/api/security/scan", data=payload,
    headers={"Content-Type": "application/json"}, method="POST"
))
data = json.loads(req.read())
check("POST /api/security/scan (invalid) -> 200", req.status == 200)
check("authorized == False for bad token", data["authorized"] is False)
check("denial message present", "denied" in data["message"].lower() or "invalid" in data["message"].lower())

# 7. Agent stream - collect all agents
def read_sse(url):
    req = urllib.request.urlopen(url)
    raw = req.read()
    results = []
    done = False
    for line in raw.split(b"\n"):
        line = line.strip()
        if line.startswith(b"data:"):
            d = json.loads(line[5:].strip())
            if d.get("done"):
                done = True
            else:
                results.append(d)
    return results, done

agents_full, stream_done = read_sse(base + "/api/agents/stream")
agents_seen = [a["id"] for a in agents_full]
check("GET /api/agents/stream yields 12 agents", len(agents_seen) == 12, str(len(agents_seen)))
check("SSE stream ends with done=true", stream_done)
check("jett in stream", "jett" in agents_seen)
check("killjoy in stream", "killjoy" in agents_seen)
all_have_fields = all(all(k in a for k in ("id","name","role","origin","ability","tier")) for a in agents_full)
check("All agent objects have required fields", all_have_fields)

# 8. Logs stream opens
req = urllib.request.urlopen(base + "/api/logs/stream")
chunk = req.read(1)
check("GET /api/logs/stream opens", True)

print()
print("Result:", "ALL TESTS PASSED" if ok else "SOME TESTS FAILED")
