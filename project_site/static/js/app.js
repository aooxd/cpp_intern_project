/* ─────────────────────────────────────────
   NexValo – Vanguard Dashboard
   app.js  |  Vanilla JS, async/await, SSE
───────────────────────────────────────── */

const UI = {
  agentGrid:     document.getElementById("agent-grid"),
  agentCount:    document.getElementById("agent-count"),
  gridPlaceholder: document.getElementById("grid-placeholder"),
  lockedName:    document.getElementById("locked-name"),
  lockedRole:    document.getElementById("locked-role"),
  statusDot:     document.getElementById("status-dot"),
  statusText:    document.getElementById("status-text"),
  consoleBody:   document.getElementById("console-body"),
  tokenInput:    document.getElementById("token-input"),
  cacheEntries:  document.getElementById("cache-entries"),
  cacheKeys:     document.getElementById("cache-keys"),
  btnSync:       document.getElementById("btn-sync"),
  btnScan:       document.getElementById("btn-scan"),
  btnCache:      document.getElementById("btn-cache"),
  btnClear:      document.getElementById("btn-clear-console"),
};

// ─── State ───────────────────────────────
const state = {
  agents: [],
  lockedAgentId: null,
  logSource: null,
};

// ─── Console Logger ───────────────────────
const TAG_CLASS = {
  INFO:     "tag-info",
  SUCCESS:  "tag-success",
  CACHE:    "tag-cache",
  SECURITY: "tag-security",
  BOOT:     "tag-boot",
  ERROR:    "tag-error",
};

function consoleLog(timestamp, tag, message) {
  const line = document.createElement("div");
  line.className = "console-line";

  const timeEl = document.createElement("span");
  timeEl.className = "con-time";
  timeEl.textContent = timestamp;

  const tagEl = document.createElement("span");
  tagEl.className = `con-tag ${TAG_CLASS[tag] || "tag-info"}`;
  tagEl.textContent = `[${tag}]`;

  const msgEl = document.createElement("span");
  msgEl.className = "con-msg";
  msgEl.textContent = message;

  line.append(timeEl, tagEl, msgEl);
  UI.consoleBody.appendChild(line);
  UI.consoleBody.scrollTop = UI.consoleBody.scrollHeight;
}

function localLog(tag, message) {
  const now = new Date();
  const ts = now.toTimeString().slice(0, 8);
  consoleLog(ts, tag, message);
}

// ─── SSE: Log Stream from backend ────────
function startLogStream() {
  if (state.logSource) return;

  state.logSource = new EventSource("/api/logs/stream");

  state.logSource.onmessage = (event) => {
    try {
      const log = JSON.parse(event.data);
      consoleLog(log.timestamp, log.tag, log.message);
    } catch (_) {}
  };

  state.logSource.onerror = () => {
    state.logSource.close();
    state.logSource = null;
    setTimeout(startLogStream, 3000);
  };
}

// ─── Agent Card Builder ───────────────────
function buildAgentCard(agent) {
  const card = document.createElement("div");
  card.className = "agent-card";
  card.dataset.id = agent.id;

  if (state.lockedAgentId === agent.id) card.classList.add("active");

  card.innerHTML = `
    <span class="card-tier tier-${agent.tier}">${agent.tier}</span>
    <div class="card-name">${agent.name}</div>
    <div class="card-role">${agent.role.toUpperCase()}</div>
    <div class="card-origin">${agent.origin}</div>
    <div class="card-ability">&#9670; ${agent.ability}</div>
  `;

  card.addEventListener("click", () => lockAgent(agent));
  return card;
}

// ─── Sync Agents (SSE stream) ─────────────
async function syncAgents() {
  UI.btnSync.disabled = true;
  UI.agentGrid.innerHTML = "";
  state.agents = [];

  localLog("INFO", "Connecting to agent data stream...");

  const source = new EventSource("/api/agents/stream");

  source.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.done) {
      source.close();
      UI.btnSync.disabled = false;
      UI.agentCount.textContent = `${state.agents.length} AGENTS`;
      updateCacheStatus();
      return;
    }

    state.agents.push(data);
    const card = buildAgentCard(data);
    UI.agentGrid.appendChild(card);
    UI.agentCount.textContent = `${state.agents.length} AGENTS`;
  };

  source.onerror = () => {
    source.close();
    UI.btnSync.disabled = false;
    localLog("ERROR", "Agent stream connection failed.");
  };
}

// ─── Lock Agent ───────────────────────────
async function lockAgent(agent) {
  localLog("INFO", `Requesting lock on agent: ${agent.name}...`);

  try {
    const res = await fetch("/api/cache/lock-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agent_id:   agent.id,
        agent_name: agent.name,
        agent_role: agent.role,
      }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    state.lockedAgentId = agent.id;

    UI.lockedName.textContent = agent.name.toUpperCase();
    UI.lockedRole.textContent = agent.role.toUpperCase();

    document.querySelectorAll(".agent-card").forEach((c) => {
      c.classList.toggle("active", c.dataset.id === agent.id);
    });

    await updateCacheStatus();
  } catch (err) {
    localLog("ERROR", `Failed to lock agent: ${err.message}`);
  }
}

// ─── Vanguard Scan ────────────────────────
async function runVanguardScan() {
  const token = UI.tokenInput.value.trim();
  if (!token) {
    localLog("ERROR", "No token provided. Scan aborted.");
    return;
  }

  UI.btnScan.disabled = true;
  localLog("SECURITY", "Initiating Vanguard security scan...");

  setSystemStatus("scanning", "SCANNING...");

  try {
    const res = await fetch("/api/security/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    });

    const data = await res.json();

    if (!data.authorized) {
      setSystemStatus("danger", "ACCESS DENIED");
      localLog("SECURITY", data.message);
    } else {
      const status = data.status === "CLEAN" ? "nominal" : "warning";
      setSystemStatus(status, `INTEGRITY ${data.integrity}%`);
    }
  } catch (err) {
    setSystemStatus("danger", "SCAN FAILED");
    localLog("ERROR", `Scan error: ${err.message}`);
  } finally {
    UI.btnScan.disabled = false;
  }
}

// ─── System Status ────────────────────────
function setSystemStatus(state, text) {
  UI.statusText.textContent = text;
  UI.statusDot.className = "status-dot";
  if (state === "danger" || state === "scanning") UI.statusDot.classList.add("danger");
  else if (state === "warning") UI.statusDot.classList.add("warning");
}

// ─── Cache Status ─────────────────────────
async function updateCacheStatus() {
  try {
    const res = await fetch("/api/cache/status");
    const data = await res.json();
    UI.cacheEntries.textContent = data.total_entries;
    UI.cacheKeys.textContent = data.active_keys.join(", ") || "—";
  } catch (_) {}
}

// ─── Event Bindings ───────────────────────
UI.btnSync.addEventListener("click", syncAgents);
UI.btnScan.addEventListener("click", runVanguardScan);
UI.btnCache.addEventListener("click", () => {
  localLog("INFO", "Manual cache refresh requested.");
  updateCacheStatus();
});
UI.btnClear.addEventListener("click", () => {
  UI.consoleBody.innerHTML = "";
  localLog("BOOT", "Console cleared.");
});

// ─── Init ─────────────────────────────────
(function init() {
  startLogStream();
  updateCacheStatus();
})();
