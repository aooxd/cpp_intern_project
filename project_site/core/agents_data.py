import asyncio
from typing import AsyncIterator

AGENTS_DATA = [
    {"id": "jett",    "name": "Jett",    "role": "Duelist",    "origin": "South Korea", "ability": "Cloudburst",     "tier": "S"},
    {"id": "reyna",   "name": "Reyna",   "role": "Duelist",    "origin": "Mexico",       "ability": "Leer",           "tier": "A"},
    {"id": "sage",    "name": "Sage",    "role": "Sentinel",   "origin": "China",        "ability": "Healing Orb",    "tier": "S"},
    {"id": "sova",    "name": "Sova",    "role": "Initiator",  "origin": "Russia",       "ability": "Recon Bolt",     "tier": "A"},
    {"id": "brimstone","name": "Brimstone","role": "Controller","origin": "USA",          "ability": "Sky Smoke",      "tier": "B"},
    {"id": "viper",   "name": "Viper",   "role": "Controller", "origin": "USA",          "ability": "Snake Bite",     "tier": "A"},
    {"id": "cypher",  "name": "Cypher",  "role": "Sentinel",   "origin": "Morocco",      "ability": "Spycam",         "tier": "A"},
    {"id": "phoenix", "name": "Phoenix", "role": "Duelist",    "origin": "UK",           "ability": "Blaze",          "tier": "B"},
    {"id": "omen",    "name": "Omen",    "role": "Controller", "origin": "Unknown",      "ability": "Paranoia",       "tier": "S"},
    {"id": "killjoy", "name": "Killjoy", "role": "Sentinel",   "origin": "Germany",      "ability": "Nanoswarm",      "tier": "S"},
    {"id": "breach",  "name": "Breach",  "role": "Initiator",  "origin": "Sweden",       "ability": "Fault Line",     "tier": "B"},
    {"id": "raze",    "name": "Raze",    "role": "Duelist",    "origin": "Brazil",       "ability": "Blast Pack",     "tier": "A"},
]


async def agent_stream() -> AsyncIterator[dict]:
    for agent in AGENTS_DATA:
        await asyncio.sleep(0.08)
        yield agent
