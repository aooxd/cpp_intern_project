import asyncio
from typing import AsyncIterator

# ─── Map Definitions ─────────────────────────────────────────────────────────

MAPS: dict[str, dict] = {
    "lotus":  {"name": "Lotus",  "region": "India",    "icon": "L", "type": "3-Site", "sites": ["A", "B", "C"]},
    "ascent": {"name": "Ascent", "region": "Italy",    "icon": "A", "type": "2-Site", "sites": ["A", "B"]},
    "bind":   {"name": "Bind",   "region": "Morocco",  "icon": "B", "type": "2-Site", "sites": ["A", "B"]},
    "haven":  {"name": "Haven",  "region": "Bhutan",   "icon": "H", "type": "3-Site", "sites": ["A", "B", "C"]},
    "split":  {"name": "Split",  "region": "Japan",    "icon": "S", "type": "2-Site", "sites": ["A", "B"]},
    "icebox": {"name": "Icebox", "region": "Arctic",   "icon": "I", "type": "2-Site", "sites": ["A", "B"]},
}

MAP_CALLOUTS: dict[str, list[dict]] = {
    "lotus": [
        {"id": "a_site",   "label": "A-Site",   "x": 18, "y": 24, "tag": "A"},
        {"id": "b_site",   "label": "B-Site",   "x": 50, "y": 60, "tag": "B"},
        {"id": "c_site",   "label": "C-Site",   "x": 80, "y": 24, "tag": "C"},
        {"id": "a_main",   "label": "A-Main",   "x": 10, "y": 46, "tag": "AM"},
        {"id": "mid",      "label": "Mid",      "x": 50, "y": 34, "tag": "M"},
        {"id": "c_stairs", "label": "C-Stairs", "x": 72, "y": 46, "tag": "CS"},
    ],
    "ascent": [
        {"id": "a_site",  "label": "A-Site",  "x": 18, "y": 22, "tag": "A"},
        {"id": "b_site",  "label": "B-Site",  "x": 80, "y": 22, "tag": "B"},
        {"id": "a_main",  "label": "A-Main",  "x": 12, "y": 52, "tag": "AM"},
        {"id": "b_main",  "label": "B-Main",  "x": 88, "y": 52, "tag": "BM"},
        {"id": "mid",     "label": "Mid",     "x": 50, "y": 42, "tag": "M"},
        {"id": "market",  "label": "Market",  "x": 50, "y": 65, "tag": "MK"},
    ],
    "bind": [
        {"id": "a_site",  "label": "A-Site",   "x": 18, "y": 28, "tag": "A"},
        {"id": "b_site",  "label": "B-Site",   "x": 80, "y": 28, "tag": "B"},
        {"id": "a_short", "label": "A-Short",  "x": 22, "y": 55, "tag": "AS"},
        {"id": "b_long",  "label": "B-Long",   "x": 76, "y": 55, "tag": "BL"},
        {"id": "tp_a",    "label": "TP Alpha", "x": 38, "y": 68, "tag": "TA"},
        {"id": "tp_b",    "label": "TP Beta",  "x": 62, "y": 68, "tag": "TB"},
    ],
    "haven": [
        {"id": "a_site",  "label": "A-Site",  "x": 14, "y": 30, "tag": "A"},
        {"id": "b_site",  "label": "B-Site",  "x": 50, "y": 30, "tag": "B"},
        {"id": "c_site",  "label": "C-Site",  "x": 84, "y": 30, "tag": "C"},
        {"id": "a_long",  "label": "A-Long",  "x": 14, "y": 62, "tag": "AL"},
        {"id": "mid",     "label": "Mid",     "x": 50, "y": 58, "tag": "M"},
        {"id": "c_long",  "label": "C-Long",  "x": 84, "y": 62, "tag": "CL"},
    ],
    "split": [
        {"id": "a_site",  "label": "A-Site",  "x": 18, "y": 25, "tag": "A"},
        {"id": "b_site",  "label": "B-Site",  "x": 80, "y": 25, "tag": "B"},
        {"id": "a_ramp",  "label": "A-Ramp",  "x": 18, "y": 56, "tag": "AR"},
        {"id": "b_main",  "label": "B-Main",  "x": 80, "y": 56, "tag": "BM"},
        {"id": "mid",     "label": "Mid",     "x": 50, "y": 40, "tag": "M"},
        {"id": "vent",    "label": "Vent",    "x": 50, "y": 62, "tag": "V"},
    ],
    "icebox": [
        {"id": "a_site",  "label": "A-Site",  "x": 18, "y": 30, "tag": "A"},
        {"id": "b_site",  "label": "B-Site",  "x": 80, "y": 30, "tag": "B"},
        {"id": "a_main",  "label": "A-Main",  "x": 18, "y": 60, "tag": "AM"},
        {"id": "b_green", "label": "B-Green", "x": 80, "y": 60, "tag": "BG"},
        {"id": "mid",     "label": "Mid",     "x": 50, "y": 45, "tag": "M"},
        {"id": "kitchen", "label": "Kitchen", "x": 50, "y": 65, "tag": "K"},
    ],
}

CALLOUT_GUIDES: dict[str, dict[str, str]] = {
    "lotus": {
        "a_site":   "A-Site on Lotus is a wide open plant area with a large rock formation providing cover. Control A-Tree and A-Flowers to take site.",
        "b_site":   "B-Site is the central bombsite with a split-level design. Rotating players must watch both upper B and lower B angles.",
        "c_site":   "C-Site is compact and favors quick executes. A coordinated push through C-Bend with utility usage is standard.",
        "a_main":   "A-Main leads directly into A-Site. A common defender position is behind the crates at A-Rubble.",
        "mid":      "Mid on Lotus is a critical rotation path connecting all three sites. Securing Mid control provides map dominance.",
        "c_stairs": "C-Stairs is a contested angle between Mid and C-Site. Duelist lurks here are highly effective.",
    },
    "ascent": {
        "a_site":   "A-Site on Ascent has a market building and elevated heaven position. Clear market and place smokes on CT-Spawn before planting.",
        "b_site":   "B-Site has a key shop window and entrance from B-Main. The boat provides cover on-site during plant.",
        "a_main":   "A-Main is the primary attack route to A-Site. Coordinate with a Mid controller to prevent split pushes.",
        "b_main":   "B-Main funnels into B-Site. A common tactic is using the sewer tunnel from Mid for a split entry.",
        "mid":      "Mid on Ascent is a long-angle alley. Winning mid opens aggressive flanks to both bombsites.",
        "market":   "Market is a key Mid-adjacent area. Controlling market links A-Site and Mid, enabling split pressure.",
    },
    "bind": {
        "a_site":   "A-Site on Bind features tight corners at Showers and a teleporter exit. Block Showers with utility on execute.",
        "b_site":   "B-Site has a teleporter and narrow entrance through B-Long or B-Short. Stack utility to flush defenders from B-Garden.",
        "a_short":  "A-Short provides a fast rotate to A-Site. Sentinels often hold this angle with a Tripwire or Spycam.",
        "b_long":   "B-Long is the primary attacker approach to B-Site. Smoke the corner and use flashes to push.",
        "tp_a":     "Teleporter Alpha connects attacker-side to A-Short. Using it mid-round creates unexpected flanks.",
        "tp_b":     "Teleporter Beta connects attacker-side to B-Long. A lurker using this can catch rotators off-guard.",
    },
    "haven": {
        "a_site":   "A-Site on Haven is accessed via A-Long and A-Short. Smokes on CT and A-Heaven are essential for a safe plant.",
        "b_site":   "B-Site is the smallest on Haven. A fast two-man push with double flashes can overwhelm defenders.",
        "c_site":   "C-Site has a garage entry and C-Long. Coordinating a split from C-Long and Mid simultaneously is effective.",
        "a_long":   "A-Long is a wide open approach. Duelists with movement abilities can traverse it quickly.",
        "mid":      "Mid on Haven connects B-Site to C-Long. Mid control is critical for rotating defenders.",
        "c_long":   "C-Long leads to C-Site with minimal cover. Use Controller smokes to safely advance.",
    },
    "split": {
        "a_site":   "A-Site on Split features a ramp entry and elevated heaven position. Smokes on CT and Heaven are mandatory.",
        "b_site":   "B-Site has a narrow main entrance and a back-alley approach. A fast push through B-Main with a flash is strong.",
        "a_ramp":   "A-Ramp is the main route to A-Site. Holding it with a Sentinel trip or camera provides early intel.",
        "b_main":   "B-Main is a tight corridor. Flashing around the corner before entry is standard.",
        "mid":      "Mid on Split has a rope to reach elevated positions. Controlling mid allows flanks onto both sites.",
        "vent":     "Vent connects Mid to B-Site. A Sentinel or Initiator with utility on vent denies this sneaky flank route.",
    },
    "icebox": {
        "a_site":   "A-Site on Icebox features a zipline and elevated positions. Clear A-Rafters before committing to plant.",
        "b_site":   "B-Site has a large green container as central cover. Control B-Yellow and B-Orange before entering.",
        "a_main":   "A-Main is the primary A-Site attack route. Watch for aggressive defenders peeking from A-Pipes.",
        "b_green":  "B-Green is the approach to B-Site. A coordinated smoke on Kitchen and B-Yellow opens the entry.",
        "mid":      "Mid on Icebox is a long range duel area. Winning mid allows pressure on both site flanks.",
        "kitchen":  "Kitchen sits between B-Green and Mid. Sentinels frequently anchor this area with traps.",
    },
}

# ─── S-Tier agents (Full-Buy requires Vanguard token) ─────────────────────────
S_TIER_AGENTS: frozenset[str] = frozenset({"jett", "sage", "omen", "killjoy"})

# ─── Agent Economy Data ───────────────────────────────────────────────────────

AGENT_ECONOMY: dict[str, dict[str, dict[str, str]]] = {
    "jett": {
        "eco":  {"en": "WEAPON: Classic / Sheriff  |  ABILITIES: Save Tailwind. 1× Cloudburst if credits allow.",
                 "uk": "ЗБРОЯ: Класик / Шериф  |  ЗДІБНОСТІ: Зберегти Попутний вітер. 1× Хмарний спалах за можливості."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Cloudburst + Tailwind. Save Updraft.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Хмарний спалах + Попутний вітер. Зберегти Підйом."},
        "full": {"en": "WEAPON: Vandal (Phantom on Bind)  |  ABILITIES: Full kit — Cloudburst ×2 + Updraft + Tailwind. Save Blade Storm for 1v1.",
                 "uk": "ЗБРОЯ: Вандал (Примара на Bind)  |  ЗДІБНОСТІ: Повний набір — Хмарний спалах ×2 + Підйом + Попутний вітер. Ульта для 1v1."},
    },
    "reyna": {
        "eco":  {"en": "WEAPON: Ghost / Sheriff  |  ABILITIES: Save Dismiss. Buy Leer only if credits allow.",
                 "uk": "ЗБРОЯ: Привид / Шериф  |  ЗДІБНОСТІ: Зберегти Відхід. Купити Зір за можливості."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Leer + Devour. Save Dismiss.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Зір + Пожирання. Зберегти Відхід."},
        "full": {"en": "WEAPON: Vandal  |  ABILITIES: Full kit — Leer + Devour + Dismiss. Stack kills for Empress.",
                 "uk": "ЗБРОЯ: Вандал  |  ЗДІБНОСТІ: Повний набір — Зір + Пожирання + Відхід. Накопичувати вбивства для Імператриці."},
    },
    "sage": {
        "eco":  {"en": "WEAPON: Classic / Sheriff  |  ABILITIES: Buy Slow Orb only. Save Wall + Heal for later rounds.",
                 "uk": "ЗБРОЯ: Класик / Шериф  |  ЗДІБНОСТІ: Купити лише Куля уповільнення. Зберегти Стіну + Лікування."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Slow Orb + Healing Orb. Save Wall for site execute.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Куля уповільнення + Куля лікування. Зберегти Стіну для виконання."},
        "full": {"en": "WEAPON: Vandal / Phantom  |  ABILITIES: Full kit — Wall + Slow Orb + Healing Orb. Resurrection for clutch retake.",
                 "uk": "ЗБРОЯ: Вандал / Примара  |  ЗДІБНОСТІ: Повний набір — Стіна + Куля уповільнення + Куля лікування. Воскресіння для ретейку."},
    },
    "sova": {
        "eco":  {"en": "WEAPON: Ghost  |  ABILITIES: Buy 1× Shock Dart lineup. Save Owl Drone + Recon Bolt.",
                 "uk": "ЗБРОЯ: Привид  |  ЗДІБНОСТІ: Купити 1× Шокова дротик лайнап. Зберегти Дрон + Болт розвідки."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Recon Bolt + 1× Shock Dart. Save Owl Drone.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Болт розвідки + 1× Шокова дротик. Зберегти Дрон."},
        "full": {"en": "WEAPON: Vandal  |  ABILITIES: Full kit — Recon Bolt + Owl Drone + Shock Darts. Hunter's Fury for multi-kill.",
                 "uk": "ЗБРОЯ: Вандал  |  ЗДІБНОСТІ: Повний набір — Болт розвідки + Дрон + Шокові дротики. Ярість мисливця для мульти-кілу."},
    },
    "brimstone": {
        "eco":  {"en": "WEAPON: Classic / Sheriff  |  ABILITIES: Buy 1× Sky Smoke. Save Stim Beacon + Orbital Strike.",
                 "uk": "ЗБРОЯ: Класик / Шериф  |  ЗДІБНОСТІ: Купити 1× Небесний дим. Зберегти Маяк + Орбітальний удар."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy 2× Sky Smoke + Stim Beacon. Save Orbital Strike.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити 2× Небесний дим + Маяк стимуляції. Зберегти Орбітальний удар."},
        "full": {"en": "WEAPON: Vandal  |  ABILITIES: Full kit — 3× Sky Smoke + Stim Beacon. Orbital Strike for post-plant.",
                 "uk": "ЗБРОЯ: Вандал  |  ЗДІБНОСТІ: Повний набір — 3× Небесний дим + Маяк. Орбітальний удар для пост-плант."},
    },
    "viper": {
        "eco":  {"en": "WEAPON: Ghost  |  ABILITIES: Buy 1× Snake Bite. Save Toxic Screen + Poison Cloud.",
                 "uk": "ЗБРОЯ: Привид  |  ЗДІБНОСТІ: Купити 1× Зміїний укус. Зберегти Токсичний екран + Отруйна хмара."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Poison Cloud + Snake Bite. Save Toxic Screen.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Отруйна хмара + Зміїний укус. Зберегти Токсичний екран."},
        "full": {"en": "WEAPON: Phantom (preferred) / Vandal  |  ABILITIES: Full kit — Toxic Screen + Poison Cloud + Snake Bite ×2. Viper's Pit to win post-plant.",
                 "uk": "ЗБРОЯ: Примара (перевага) / Вандал  |  ЗДІБНОСТІ: Повний набір — Токсичний екран + Отруйна хмара + Зміїний укус ×2. Лігво Вайпер для пост-планту."},
    },
    "cypher": {
        "eco":  {"en": "WEAPON: Ghost  |  ABILITIES: Buy 1× Cyber Cage. Save Tripwire + Spycam.",
                 "uk": "ЗБРОЯ: Привид  |  ЗДІБНОСТІ: Купити 1× Кіберклітка. Зберегти Пасткодріт + Шпигунська камера."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Tripwire + Cyber Cage. Save Spycam.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Пасткодріт + Кіберклітка. Зберегти Шпигунська камера."},
        "full": {"en": "WEAPON: Vandal  |  ABILITIES: Full kit — Tripwire + Spycam + Cyber Cage ×2. Neural Theft on first kill for full map info.",
                 "uk": "ЗБРОЯ: Вандал  |  ЗДІБНОСТІ: Повний набір — Пасткодріт + Камера + Кіберклітка ×2. Нейрокрадіжка для повної карти ворогів."},
    },
    "phoenix": {
        "eco":  {"en": "WEAPON: Ghost  |  ABILITIES: Buy Curveball only. Save Blaze + Run it Back.",
                 "uk": "ЗБРОЯ: Привид  |  ЗДІБНОСТІ: Купити лише Кривий постріл. Зберегти Полум'я + Знову в гру."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Blaze + Curveball. Save Hot Hands.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Полум'я + Кривий постріл. Зберегти Гарячі руки."},
        "full": {"en": "WEAPON: Vandal  |  ABILITIES: Full kit — Blaze + Curveball + Hot Hands. Run it Back for aggressive entry.",
                 "uk": "ЗБРОЯ: Вандал  |  ЗДІБНОСТІ: Повний набір — Полум'я + Кривий постріл + Гарячі руки. Знову в гру для агресивного входу."},
    },
    "omen": {
        "eco":  {"en": "WEAPON: Ghost  |  ABILITIES: Buy 1× Dark Cover. Save Paranoia + From the Shadows.",
                 "uk": "ЗБРОЯ: Привид  |  ЗДІБНОСТІ: Купити 1× Темне покриття. Зберегти Параноя + З тіней."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Dark Cover ×2 + Paranoia. Save Shrouded Step.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Темне покриття ×2 + Параноя. Зберегти Окутаний крок."},
        "full": {"en": "WEAPON: Phantom (Omen's signature) / Vandal  |  ABILITIES: Full kit — Dark Cover ×2 + Paranoia + Shrouded Step. From the Shadows for map pressure.",
                 "uk": "ЗБРОЯ: Примара (класика Омена) / Вандал  |  ЗДІБНОСТІ: Повний набір — Темне покриття ×2 + Параноя + Окутаний крок. З тіней для тиску на карті."},
    },
    "killjoy": {
        "eco":  {"en": "WEAPON: Ghost  |  ABILITIES: Buy Alarmbot only. Save Turret + Nanoswarm.",
                 "uk": "ЗБРОЯ: Привид  |  ЗДІБНОСТІ: Купити лише Тривожного бота. Зберегти Турель + Нанорій."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Alarmbot + Nanoswarm. Save Turret.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Тривожного бота + Нанорій. Зберегти Турель."},
        "full": {"en": "WEAPON: Vandal  |  ABILITIES: Full kit — Turret + Alarmbot + Nanoswarm ×2. Lockdown for site retake or post-plant.",
                 "uk": "ЗБРОЯ: Вандал  |  ЗДІБНОСТІ: Повний набір — Турель + Тривожний бот + Нанорій ×2. Блокування для ретейку або пост-планту."},
    },
    "breach": {
        "eco":  {"en": "WEAPON: Ghost  |  ABILITIES: Buy 1× Flashpoint. Save Fault Line + Rolling Thunder.",
                 "uk": "ЗБРОЯ: Привид  |  ЗДІБНОСТІ: Купити 1× Точка спалаху. Зберегти Лінія розлому + Гучний грім."},
        "semi": {"en": "WEAPON: Spectre  |  ABILITIES: Buy Fault Line + Flashpoint. Save Aftershock.",
                 "uk": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити Лінія розлому + Точка спалаху. Зберегти Афтершок."},
        "full": {"en": "WEAPON: Vandal  |  ABILITIES: Full kit — Fault Line + Flashpoint ×2 + Aftershock. Rolling Thunder to clear a stacked defense.",
                 "uk": "ЗБРОЯ: Вандал  |  ЗДІБНОСТІ: Повний набір — Лінія розлому + Точка спалаху ×2 + Афтершок. Гучний грім для знищення скупченої оборони."},
    },
    "raze": {
        "eco":  {"en": "WEAPON: Classic  |  ABILITIES: Buy 1× Blast Pack. Save Boom Bot + Paint Shells.",
                 "uk": "ЗБРОЯ: Класик  |  ЗДІБНОСТІ: Купити 1× Вибуховий рюкзак. Зберегти Вибухового бота + Фарбувальні гільзи."},
        "semi": {"en": "WEAPON: Spectre / Stinger  |  ABILITIES: Buy Boom Bot + Blast Pack. Save Paint Shells.",
                 "uk": "ЗБРОЯ: Спектр / Стінгер  |  ЗДІБНОСТІ: Купити Вибуховий бот + Рюкзак. Зберегти Фарбувальні гільзи."},
        "full": {"en": "WEAPON: Vandal / Odin  |  ABILITIES: Full kit — Boom Bot + Blast Pack ×2 + Paint Shells. Showstopper for post-plant clear.",
                 "uk": "ЗБРОЯ: Вандал / Одін  |  ЗДІБНОСТІ: Повний набір — Вибуховий бот + Рюкзак ×2 + Гільзи. Зупинник вистави для пост-планту."},
    },
}

# ─── Bilingual Tactics Matrix ─────────────────────────────────────────────────

TACTICS_MATRIX: dict[tuple[str, str], dict[str, dict[str, str]]] = {
    ("jett", "lotus"): {
        "en": {
            "attack":  "Execute a fast push through A-Main with Tailwind dash to entry A-Site. Deploy Cloudburst smokes on A-Stairs and A-Rubble to isolate defenders. Use Updraft to reach the elevated rock formation for a surprise plant angle.",
            "defense": "Play an aggressive solo angle at C-Stairs with Jett's mobility. Hold a wide peek and use Tailwind to disengage after securing a pick. Rotate to B-Site to reinforce the most pressured flank.",
        },
        "uk": {
            "attack":  "Виконайте швидкий пуш через A-Main за допомогою ривку Попутного вітру на вхід A-Сайту. Використайте Хмарні спалахи на A-Stairs та A-Rubble для ізоляції захисників. Підйом дозволить зайняти підвищену скелю для несподіваного куту планту.",
            "defense": "Грайте агресивно з позиції на C-Stairs завдяки мобільності Джетт. Зробіть широкий піп та використайте Попутний вітер після отримання фрагу. Обертайтесь на B-Сайт для підтримки найбільш атакованого флангу.",
        },
    },
    ("jett", "ascent"): {
        "en": {
            "attack":  "Open Mid control by dashing aggressively into B-Short or A-Link. Use Cloudburst to block CT angles and Updraft to reach elevated Market positions. Once Mid is split, commit to the weaker site.",
            "defense": "Play a passive reactive role on B-Site. Self-smoke with Cloudburst when peeked, and save Blade Storm for late-round 1v1 situations. Rotate through Market mid-round for a surprise retake angle.",
        },
        "uk": {
            "attack":  "Відкрийте контроль Міду агресивним ривком у B-Short або A-Link. Використайте Хмарні спалахи для блокування кутів CT та Підйом для досягнення підвищеного Маркету. Після розколу Міду — атакуйте слабший сайт.",
            "defense": "Грайте пасивно та реактивно на B-Сайті. Самодимуйтесь Хмарним спалахом при пік-знятті та зберігайте Бурю клинків для пізнього 1v1. Обертайтесь через Маркет для несподіваного ретейку.",
        },
    },
    ("jett", "bind"): {
        "en": {
            "attack":  "Sprint through the Teleporter for an unexpected A-Short or B-Site entry. Deploy Cloudburst on B-Garden or Showers to clear angles. A Jett lurk via teleporter while the team pressures the other site is highly disruptive.",
            "defense": "Anchor B-Site aggressively. Peek B-Long early and use Tailwind to escape any retaliation. Hold the teleporter exit to prevent attacker flank routes mid-round.",
        },
        "uk": {
            "attack":  "Пробіжіть через телепортер для несподіваного входу на A-Short або B-Сайт. Поставте Хмарні спалахи на B-Garden або Showers для зачищення кутів. Лурк Джетт через телепортер при тиску команди на іншому сайті є дуже дестабілізуючим.",
            "defense": "Тримайте B-Сайт агресивно. Робіть ранні пік-знімання на B-Long та використайте Попутний вітер для відступу. Тримайте вихід телепортера для блокування обхідних маршрутів атакуючих.",
        },
    },
    ("sage", "lotus"): {
        "en": {
            "attack":  "Place a Sage Wall at A-Main base to boost teammates onto the elevated crate for an unexpected entry angle. Use Slow Orbs at B-Site chokepoints to delay rotating defenders during the plant.",
            "defense": "Anchor A-Site by walling off A-Main entrance mid-round. Position Healing Orbs on the front-line duelist. A well-timed Resurrection in a B-Site retake can single-handedly win the round.",
        },
        "uk": {
            "attack":  "Поставте Стіну Сейдж у основі A-Main для підйому союзників на підвищені ящики під несподіваним кутом входу. Використайте Кулі уповільнення у вузьких місцях B-Сайту для затримки ротуючих захисників під час планту.",
            "defense": "Тримайте A-Сайт, замурувавши вхід A-Main у середині раунду. Розміщуйте Кулі лікування на дуелісті першої лінії. Вчасне Воскресіння під час ретейку B-Сайту може самостійно вирішити раунд.",
        },
    },
    ("sage", "ascent"): {
        "en": {
            "attack":  "Boost a teammate with Sage Wall at A-Main for early Market control. Use Slow Orbs on the catwalk to deny CT rotations while planting. Heal forward players to sustain through a long execute.",
            "defense": "Wall the B-Main entrance early to buy time for teammate rotations. Heal the duelist holding Mid. A late-round Resurrection on a planted-site anchor player is Sage's highest-value play.",
        },
        "uk": {
            "attack":  "Підніміть союзника Стіною в A-Main для раннього контролю Маркету. Використайте Кулі уповільнення на каткоті для відхилення ротацій CT під час планту. Лікуйте передову для підтримки в тривалому виконанні.",
            "defense": "Замуруйте вхід B-Main на початку для виграшу часу ротацій. Лікуйте дуеліста, що тримає Мід. Пізнє Воскресіння якорного гравця на вже захищеному сайті є найціннішою грою Сейдж.",
        },
    },
    ("omen", "lotus"): {
        "en": {
            "attack":  "Smoke all three site approaches with Omen's long-range Dark Cover. Paranoia through A-Rubble before committing to A-Site. Use Shrouded Step to teleport behind defenders holding aggressive forward angles.",
            "defense": "Play a lurking Mid presence using Shrouded Step teleport. Deny C-Stairs control with Paranoia. From the Shadows ultimate provides map-wide pressure to prevent mid-round defender aggression.",
        },
        "uk": {
            "attack":  "Задиміть всі три підходи до сайтів за допомогою далекодіючого Темного покриття Омена. Параноя через A-Rubble перед входом на A-Сайт. Використайте Окутаний крок для телепортації за захисниками на агресивних передових позиціях.",
            "defense": "Грайте у лурк посередині за допомогою телепортації Окутаним кроком. Відхиляйте контроль C-Stairs Параноєю. Ультімейт З тіней забезпечує тиск по всій карті для запобігання агресії захисників у середині раунду.",
        },
    },
    ("killjoy", "ascent"): {
        "en": {
            "attack":  "Place Nanoswarm behind the B-Site boat for post-plant activation. Push B-Main with teammates while Alarmbot provides intel on defenders pushing through B-Short or Market.",
            "defense": "Deploy Turret deep in A-Site to gain early intel on A-Main push. Stack Nanoswarms on the plant zone. Lockdown on B-Site mid-round forces defenders out of anchored positions.",
        },
        "uk": {
            "attack":  "Поставте Нанорій за човном на B-Сайті для активації після планту. Пушіть B-Main з командою, поки Тривожний бот забезпечує інформацію про захисників, що рухаються через B-Short або Маркет.",
            "defense": "Розгорніть Турель глибоко на A-Сайті для раннього виявлення пушу через A-Main. Нагромаджуйте Нанорії на зоні планту. Блокування на B-Сайті у середині раунду виштовхує захисників із закріплених позицій.",
        },
    },
    ("killjoy", "bind"): {
        "en": {
            "attack":  "Deploy Alarmbot at B-Long entrance to detect an early defensive push. Plant and activate Nanoswarm on the post-plant position to prevent the defuse during the retake.",
            "defense": "Lock down B-Site with Turret and Nanoswarm. The teleporter exit is a critical Alarmbot placement to catch rotating attackers. Lockdown from a safe distance to retake A-Site.",
        },
        "uk": {
            "attack":  "Розгорніть Тривожного бота на вході B-Long для виявлення раннього пушу захисників. Заплантуйте та активуйте Нанорій на позиції пост-планту для запобігання знешкодженню під час ретейку.",
            "defense": "Закрийте B-Сайт Тореллю та Нанорієм. Вихід телепортера — критична позиція для Тривожного бота, щоб зловити ротуючих атакуючих. Блокування з безпечної дистанції для ретейку A-Сайту.",
        },
    },
    ("reyna", "haven"): {
        "en": {
            "attack":  "Use Leer to blind the B-Site defender before a fast two-man push. Stack kills to fuel Empress snowball across multiple sites. A lurk through C-Long while the team pressures A-Long creates extreme map pressure.",
            "defense": "Play an aggressive off-angle at A-Long. Leer into the corner and punish any peeking attacker. After securing a pick, Dismiss immediately and hold a second angle to deny the full team push.",
        },
        "uk": {
            "attack":  "Використайте Зір для осліплення захисника B-Сайту перед швидким пушем удвох. Накопичуйте вбивства для снобола Імператриці на кількох сайтах. Лурк через C-Long при тиску команди на A-Long створює крайній тиск по карті.",
            "defense": "Грайте агресивно під нестандартним кутом на A-Long. Запустіть Зір у кут та покарайте кожного атакуючого, що дивиться. Після фрагу відразу активуйте Відхід та займіть другий кут для відхилення командного пушу.",
        },
    },
    ("viper", "icebox"): {
        "en": {
            "attack":  "Use Toxic Screen splitting B-Green and B-Yellow simultaneously. Snake Bite the B-Site plant area and advance under Viper's Screen. Viper's Pit on B-Site makes the post-plant situation nearly unwinnable for defenders.",
            "defense": "Anchor B-Site using Viper's Pit as a one-sided advantage zone. Deploy Toxic Screen to cut off CT-to-B-Green rotation. Use Poison Cloud on Kitchen to delay Mid control and prevent a site split.",
        },
        "uk": {
            "attack":  "Використайте Токсичний екран, розділяючи B-Green та B-Yellow одночасно. Зміїний укус на зоні планту B-Сайту та просувайтесь під прикриттям Екрану. Лігво Вайпер на B-Сайті робить ситуацію пост-планту майже нерозв'язною для захисників.",
            "defense": "Тримайте B-Сайт за допомогою Лігва Вайпер як зони односторонньої переваги. Розгорніть Токсичний екран для відрізання ротації CT-to-B-Green. Використайте Отруйну хмару на Кухні для затримки контролю Міду та запобігання розколу сайту.",
        },
    },
    ("sova", "split"): {
        "en": {
            "attack":  "Fire a Recon Bolt over the A-Ramp wall to reveal the defender behind the box. Use Owl Drone to scout B-Main before committing. Hunter's Fury ultimate clears a stacked B-Site through walls.",
            "defense": "Deploy a Shock Dart lineup at B-Vent to punish Mid rotators. Use Recon Bolt on A-Ramp to detect an early rush. Hold Mid control with Sova's Owl Drone to maintain intel dominance throughout the round.",
        },
        "uk": {
            "attack":  "Вистрілюйте Болт розвідки через стіну A-Ramp для виявлення захисника за ящиком. Використайте Дрон-сову для розвідки B-Main перед рішучим пушем. Ульта Ярість мисливця знищує скупчений B-Сайт крізь стіни.",
            "defense": "Розмістіть лайнап Шокового дротика на B-Vent для покарання ротаторів Міду. Використайте Болт розвідки на A-Ramp для виявлення раннього ранш. Тримайте контроль Міду Дроном-совою для збереження переваги в інформації протягом раунду.",
        },
    },
    ("cypher", "ascent"): {
        "en": {
            "attack":  "Place Tripwire at the Market door to detect and delay CT mid-rotate. Use Cyber Cage to create a one-way smoke on A-Heaven during the A-Site execute. Neural Theft on the first kill reveals all remaining defender positions.",
            "defense": "Lock B-Main with a Tripwire at the entrance corner. Deploy Spycam facing B-Short for passive Mid intel. A well-placed Cyber Cage one-way on A-Site creates a deadly information advantage.",
        },
        "uk": {
            "attack":  "Поставте Пасткодріт біля дверей Маркету для виявлення та затримки ротації CT. Використайте Кіберклітку для створення одностороннього диму на A-Heaven під час атаки A-Сайту. Нейрокрадіжка на першому вбивстві відкриває всі позиції захисників.",
            "defense": "Заблокуйте B-Main Пасткодротом у кутку входу. Розгорніть Шпигунську камеру навпроти B-Short для пасивного спостереження за Мідом. Добре розміщена одностороння Кіберклітка на A-Сайті дає смертоносну інформаційну перевагу.",
        },
    },
    ("breach", "split"): {
        "en": {
            "attack":  "Fault Line through the A-Ramp wall to stun defenders holding the A-Site entrance. Aftershock clears corners on B-Site before team entry. Rolling Thunder from attacker-side Mid flushes an entire stacked defense in one activation.",
            "defense": "Use Fault Line to punish any attacker pushing through Mid Vent. Flashpoint through the B-Main wall to blind a fast-rushing team. Breach's stuns force attackers to hold positioning during a mid-round defensive push.",
        },
        "uk": {
            "attack":  "Лінія розлому крізь стіну A-Ramp для оглушення захисників, що тримають вхід на A-Сайт. Афтершок зачищає кути B-Сайту перед входом команди. Гучний грім з боку атакуючих на Міді вимітає всю скупчену оборону однією активацією.",
            "defense": "Використайте Лінію розлому для покарання будь-якого атакуючого, що проходить через Вентиляцію Міду. Точка спалаху крізь стіну B-Main для осліплення команди при швидкому рашу. Оглушення Бріча змушують атакуючих зупинятись під час оборонного пушу в середині раунду.",
        },
    },
    ("raze", "bind"): {
        "en": {
            "attack":  "Blast Pack jump through the Teleporter for an unexpected B-Short or A-Site entry. Deploy Boom Bot in B-Long to clear corners before entry. Showstopper rocket in the post-plant position instantly clears a retaking defender squad.",
            "defense": "Play an aggressive B-Long forward position. Boom Bot a potential A-Short push to detect early and deny. Blast Pack jump over the wall for a surprise retake angle that defenders won't expect.",
        },
        "uk": {
            "attack":  "Стрибок Вибуховим рюкзаком через телепортер для несподіваного входу на B-Short або A-Сайт. Запустіть Вибухового бота на B-Long для зачищення кутів перед входом. Ракета Зупинника вистав у позиції пост-планту миттєво знищує команду захисників, що ретейкує.",
            "defense": "Займіть агресивну передову позицію на B-Long. Запустіть Вибухового бота для раннього виявлення потенційного пушу з A-Short. Стрибок Вибуховим рюкзаком через стіну дає несподіваний кут ретейку, якого захисники не очікують.",
        },
    },
    ("phoenix", "haven"): {
        "en": {
            "attack":  "Use Blaze wall across A-Short to cut the defender's sightline on entry. Flash around the C-Long corner before a full team execute. Run it Back ultimate lets Phoenix play aggressively on B-Site without fear of permanent death.",
            "defense": "Hold a hot angle at C-Long with Phoenix. Throw a Curveball flash around the corner to blind an aggressive attacker. After securing a kill, use Blaze to heal and reposition to B-Site quickly.",
        },
        "uk": {
            "attack":  "Використайте Стіну полум'я через A-Short для перекриття прямого кута захисника при вході. Фліш за кут C-Long перед повним виконанням команди. Ульт Знову в гру дозволяє Фенікс агресивно грати на B-Сайті без страху постійної смерті.",
            "defense": "Тримайте гострий кут на C-Long. Киньте Кривий постріл за кут для осліплення агресивного атакуючого. Після отримання фрагу використайте Полум'я для лікування та швидко перейдіть на B-Сайт.",
        },
    },
    ("brimstone", "lotus"): {
        "en": {
            "attack":  "Place three Sky Smokes to fully cover A-Site: one on A-Steps, one on the back-corner, one on the CT entrance. Stim Beacon the entry player for a faster push. Orbital Strike on the plant zone seals the post-plant.",
            "defense": "Deploy an early Incendiary at B-Site entrance to delay a rush and burn utility. Smoke off the A-Main entrance mid-round to block attack rotation sight. Orbital Strike punishes a grouped attacker plant attempt.",
        },
        "uk": {
            "attack":  "Поставте три Небесних диму для повного покриття A-Сайту: один на A-Steps, один у задньому куті, один на вход із CT. Маяк стимуляції для дуеліста першого входу. Орбітальний удар на зоні планту запечатує пост-плант.",
            "defense": "Розгорніть ранній Запальник на вході B-Сайту для затримки рашу та спалення утиліт. Задиміть вхід A-Main у середині раунду для блокування огляду ротації атаки. Орбітальний удар карає скупчену спробу планту атакуючих.",
        },
    },
}

FALLBACK_TACTICS: dict[str, dict[str, str]] = {
    "en": {
        "attack":  "Coordinate with your team to establish Mid control first, then commit to the site with the weakest defense. Use your agent's utility to block key defender sightlines on entry and maintain post-plant control with grenades or area-denial abilities.",
        "defense": "Set up a layered defense by placing utility at primary attack routes. Maintain communication for early rotations. Play reactively in the first half and take aggressive early duels only when you hold an information advantage.",
    },
    "uk": {
        "attack":  "Координуйте з командою для встановлення контролю Міду, потім атакуйте сайт із найслабшою обороною. Використовуйте утиліти агента для блокування ключових ліній огляду захисників при вході та підтримуйте контроль пост-планту гранатами або здібностями заборони зони.",
        "defense": "Налаштуйте ешелоновану оборону, розміщуючи утиліти на основних маршрутах атаки. Підтримуйте комунікацію для ранніх ротацій. Грайте реактивно в першій половині та вступайте в агресивні дуелі лише при наявності інформаційної переваги.",
    },
}


def get_tactics(agent_id: str, map_id: str) -> dict[str, dict[str, str]]:
    return TACTICS_MATRIX.get((agent_id.lower(), map_id.lower()), FALLBACK_TACTICS)


def get_economy_line(agent_id: str, round_type: str, lang: str) -> str:
    agent_data = AGENT_ECONOMY.get(agent_id.lower())
    if not agent_data:
        defaults = {
            "en": {"eco": "WEAPON: Classic / Sheriff  |  ABILITIES: Save all abilities.",
                   "semi": "WEAPON: Spectre  |  ABILITIES: Buy 1-2 basic abilities.",
                   "full": "WEAPON: Vandal / Phantom  |  ABILITIES: Full kit."},
            "uk": {"eco": "ЗБРОЯ: Класик / Шериф  |  ЗДІБНОСТІ: Зберегти всі.",
                   "semi": "ЗБРОЯ: Спектр  |  ЗДІБНОСТІ: Купити 1-2 базові здібності.",
                   "full": "ЗБРОЯ: Вандал / Примара  |  ЗДІБНОСТІ: Повний набір."},
        }
        return defaults.get(lang, defaults["en"]).get(round_type, "")
    tier = agent_data.get(round_type, agent_data.get("full", {}))
    return tier.get(lang, tier.get("en", ""))


async def stream_tactics(
    agent_id: str,
    map_id: str,
    side: str,
    round_type: str = "full",
    lang: str = "en",
) -> AsyncIterator[str]:
    tactics = get_tactics(agent_id, map_id)
    lang_tactics = tactics.get(lang, tactics.get("en", FALLBACK_TACTICS["en"]))
    strategy_text = lang_tactics.get(side, lang_tactics.get("attack", ""))

    agent_name = agent_id.capitalize()
    map_name = MAPS.get(map_id, {}).get("name", map_id.capitalize())
    side_label = side.upper()

    economy_line = get_economy_line(agent_id, round_type, lang)
    round_labels = {
        "eco":  {"en": "ECO ROUND",   "uk": "ЕКО РАУНД"},
        "semi": {"en": "SEMI-BUY",    "uk": "НАПІВ-КУПІВЛЯ"},
        "full": {"en": "FULL BUY",    "uk": "ПОВНА КУПІВЛЯ"},
    }
    round_label = round_labels.get(round_type, {"en": "FULL BUY", "uk": "ПОВНА КУПІВЛЯ"}).get(lang, "FULL BUY")

    header = (
        f"[ {agent_name} // {map_name} // {side_label} // {round_label} ]\n\n"
        f"{economy_line}\n\n"
    )

    full_text = header + strategy_text
    words = full_text.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.055)
