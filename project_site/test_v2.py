import urllib.request, json

base = "http://127.0.0.1:8000"
ok = True

def check(label, cond, detail=""):
    global ok
    s = "PASS" if cond else "FAIL"
    if not cond: ok = False
    print(f"  [{s}] {label}{(' | ' + str(detail)) if detail else ''}")

def GET(path):
    r = urllib.request.urlopen(base + path)
    return r.status, json.loads(r.read())

def POST(path, body):
    data = json.dumps(body).encode()
    r = urllib.request.urlopen(urllib.request.Request(
        base + path, data=data,
        headers={"Content-Type": "application/json"}, method="POST"))
    return r.status, json.loads(r.read())

def SSE(path):
    r = urllib.request.urlopen(base + path)
    raw = r.read()
    chunks, done = [], False
    for line in raw.split(b"\n"):
        line = line.strip()
        if line.startswith(b"data:"):
            d = json.loads(line[5:].strip())
            if d.get("done"): done = True
            elif "chunk" in d: chunks.append(d["chunk"])
    return "".join(chunks), done

print("─── i18n ────────────────────────────────────")
s, d = GET("/api/i18n/strings?lang=en")
check("GET /api/i18n/strings?lang=en -> 200", s == 200)
check("Returns EN strings", d["lang"] == "en")
check("nav.roster key present", "nav.roster" in d["strings"])
check("EN nav.roster = AGENT ROSTER", d["strings"]["nav.roster"] == "AGENT ROSTER")

s, d = GET("/api/i18n/strings?lang=uk")
check("GET /api/i18n/strings?lang=uk -> 200", s == 200)
check("Returns UK strings", d["lang"] == "uk")
check("UK nav.roster translated", d["strings"]["nav.roster"] == "РЕЄСТР АГЕНТІВ")
check("UK btn.generate translated", "ЗГЕНЕРУВАТИ" in d["strings"].get("btn.generate",""))

s, d = POST("/api/i18n/set-lang", {"lang": "uk"})
check("POST /api/i18n/set-lang uk -> 200", s == 200)
check("set-lang returns strings", "strings" in d)

s, d = POST("/api/i18n/set-lang", {"lang": "en"})
check("POST /api/i18n/set-lang en -> 200", s == 200)

print("─── Tactics: Economy + Bilingual ────────────")
# Lock agent + select map first
POST("/api/cache/lock-agent", {"agent_id":"jett","agent_name":"Jett","agent_role":"Duelist"})
POST("/api/tactics/select-map", {"map_id": "lotus"})

# EN Full Buy
text, done = SSE("/api/tactics/stream?agent_id=jett&map_id=lotus&side=attack&round_type=full&lang=en&token=VANGUARD-7749-NEXVALO")
check("Tactics stream EN full -> done", done)
check("EN full briefing has Jett", "Jett" in text)
check("EN full briefing has Lotus", "Lotus" in text)
check("EN full briefing has FULL BUY", "FULL BUY" in text)
check("EN full briefing has WEAPON", "WEAPON:" in text)

# EN Eco
text, done = SSE("/api/tactics/stream?agent_id=jett&map_id=lotus&side=attack&round_type=eco&lang=en&token=")
check("Tactics stream EN eco -> done", done)
check("EN eco briefing has ECO ROUND", "ECO ROUND" in text, text[:80])
check("EN eco briefing has Sheriff", "Sheriff" in text)

# UK Full Buy
text, done = SSE("/api/tactics/stream?agent_id=sage&map_id=lotus&side=attack&round_type=full&lang=uk&token=VANGUARD-7749-NEXVALO")
check("Tactics stream UK full (sage+lotus) -> done", done)
check("UK full briefing has ПОВНА КУПІВЛЯ", "ПОВНА КУПІВЛЯ" in text, text[:80])
check("UK full briefing has ЗБРОЯ", "ЗБРОЯ:" in text)

# UK Semi
text, done = SSE("/api/tactics/stream?agent_id=jett&map_id=ascent&side=defense&round_type=semi&lang=uk&token=")
check("Tactics stream UK semi -> done", done)
check("UK semi has НАПІВ-КУПІВЛЯ", "НАПІВ-КУПІВЛЯ" in text, text[:80])

# SecurityProxy: Full Buy S-tier WITHOUT token
text, done = SSE("/api/tactics/stream?agent_id=omen&map_id=lotus&side=attack&round_type=full&lang=en&token=WRONG")
check("Restricted: full+S-tier+bad token -> done", done)
check("Restricted message returned", "ACCESS RESTRICTED" in text or "ДОСТУП ОБМЕЖЕНО" in text, text[:80])

# SecurityProxy: Full Buy NON-S-tier (raze) — should NOT be blocked
text, done = SSE("/api/tactics/stream?agent_id=raze&map_id=bind&side=attack&round_type=full&lang=en&token=")
check("Non-S-tier full buy (raze) not blocked", "ACCESS RESTRICTED" not in text and done)

# Fallback (unknown combo) UK
text, done = SSE("/api/tactics/stream?agent_id=unknown&map_id=lotus&side=attack&round_type=eco&lang=uk&token=")
check("Fallback UK returns content", len(text) > 10 and done)

print()
print("Result:", "ALL TESTS PASSED" if ok else "SOME TESTS FAILED")
