import urllib.request, json

base = "http://127.0.0.1:8000"
ok = True

def check(label, cond, detail=""):
    global ok
    s = "PASS" if cond else "FAIL"
    if not cond: ok = False
    print(f"  [{s}] {label}{(' | ' + str(detail)) if detail else ''}")

# Maps list
req = urllib.request.urlopen(base + "/api/tactics/maps")
data = json.loads(req.read())
check("GET /api/tactics/maps -> 200", req.status == 200)
check("Returns 6 maps", len(data["maps"]) == 6, len(data["maps"]))
check("Lotus present", any(m["map_id"] == "lotus" for m in data["maps"]))
check("All maps have icon/type/region", all("icon" in m and "type" in m and "region" in m for m in data["maps"]))

# Select map
payload = json.dumps({"map_id": "lotus"}).encode()
req = urllib.request.urlopen(urllib.request.Request(
    base + "/api/tactics/select-map", data=payload,
    headers={"Content-Type": "application/json"}, method="POST"
))
data = json.loads(req.read())
check("POST /api/tactics/select-map -> 200", req.status == 200)
check("Map selection returns ok status", data["status"] == "ok")
check("Selected map is lotus", data["map"]["map_id"] == "lotus")

# Callouts for lotus
req = urllib.request.urlopen(base + "/api/tactics/callouts?map_id=lotus")
data = json.loads(req.read())
check("GET /api/tactics/callouts?map_id=lotus -> 200", req.status == 200)
check("Lotus has 6 callout zones", len(data["callouts"]) == 6, len(data["callouts"]))
check("All callouts have x/y/tag/label", all("x" in c and "y" in c and "tag" in c and "label" in c for c in data["callouts"]))

# Callout info
req = urllib.request.urlopen(base + "/api/tactics/callout-info?map_id=lotus&zone_id=a_site")
data = json.loads(req.read())
check("GET /api/tactics/callout-info (a_site) -> 200", req.status == 200)
check("Callout info has guide text", len(data.get("guide", "")) > 10)
check("Zone label returned", data.get("zone_label") == "A-Site")

# Tactics status
req = urllib.request.urlopen(base + "/api/tactics/status")
data = json.loads(req.read())
check("GET /api/tactics/status -> 200", req.status == 200)
check("active_map populated after select", data["active_map"] is not None)

# Lock an agent (needed for stream test)
payload = json.dumps({"agent_id": "jett", "agent_name": "Jett", "agent_role": "Duelist"}).encode()
urllib.request.urlopen(urllib.request.Request(
    base + "/api/cache/lock-agent", data=payload,
    headers={"Content-Type": "application/json"}, method="POST"
))

# Tactics stream (Jett + Lotus attack)
req = urllib.request.urlopen(base + "/api/tactics/stream?agent_id=jett&map_id=lotus&side=attack")
raw = req.read()
chunks = []
done_flag = False
for line in raw.split(b"\n"):
    line = line.strip()
    if line.startswith(b"data:"):
        d = json.loads(line[5:].strip())
        if d.get("done"):
            done_flag = True
        elif "chunk" in d:
            chunks.append(d["chunk"])
full_text = "".join(chunks)
check("GET /api/tactics/stream yields chunks", len(chunks) > 5, len(chunks))
check("Stream ends with done=true", done_flag)
check("Briefing mentions Jett", "Jett" in full_text)
check("Briefing mentions Lotus", "Lotus" in full_text)
check("Briefing mentions attack side", "ATTACK" in full_text)

# Fallback tactics (unknown combo)
req = urllib.request.urlopen(base + "/api/tactics/stream?agent_id=unknown&map_id=lotus&side=attack")
raw2 = req.read()
fb_chunks = []
for line in raw2.split(b"\n"):
    line = line.strip()
    if line.startswith(b"data:"):
        d = json.loads(line[5:].strip())
        if "chunk" in d:
            fb_chunks.append(d["chunk"])
check("Fallback tactics returned for unknown agent", len(fb_chunks) > 0)

print()
print("Result:", "ALL TESTS PASSED" if ok else "SOME TESTS FAILED")
