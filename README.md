NexValo Engine
NexValo Engine- це backend/frontend система для аналізу та управління тактики у грі Valorant.
Реалізовано як веб-застосунок на python з використанням асинхронного серверу та модульної архітектури ну і підв1язкою лаб 
-------------------------------
Основний функціонал
-----------------------------
Tactical Engine
-----------------
Модуль tactics_engine.py відповідає за
роботу з картами
tactical callouts
генерацію briefing-ів
аналіз агентів
побудову tactical data structures
------------------------------
Event Streaming
-------------------------------
Система підтримує SSE-потоки-
live logs
live agents update
tactical notifications
-------------------
Security System
----------------------
Модуль SecurityProxy реалізує-
перевірку токенів
контроль доступу
проксі-доступ до Vanguard системи.
-------------
Cache System
------------
CacheManager-
кешує tactical data
використовує TTL
підтримує singleton access
--------------------------
Internationalization
-------------------------
Система підтримує-
українську мову
англійську мову
динамічне перемикання локалізації
---------------------
На сайті можна
--------------------
працювати з агентами та тактичними схемами
аналізувати і генерувати tactical briefings
виконувати streaming оновлень у реальному часі
кешувати дані
використовувати систему безпеки через proxy pattern
працювати з мультимовністю
логувати події та транслювати їх через event bus
----------------------
Використані технології
----------------------
Backend
--------
Python
FastAPI
AsyncIO
REST API
SSE (Server-Sent Events)
---------
Frontend
--------
HTML5
CSS3
JavaScript
-----------
Архітектура
-----------
Singleton Pattern
Observer Pattern
Proxy Pattern
Event-Driven Architecture
Modular Architecture

-----------------
Інтегровані лаби
-----------------
Fibonacci (став фундаментом для реалізації алгоритмічної частини tactical engine)
---------
базова алгоритмічна логіка
робота зі структурами даних
оптимізація tactical calculations

це видно у 
tactics_engine.py
utility functions
async tactical calculations
-----------------
Singleton Pattern (забезпечує існування одного глобального екземпляра системи кешу та event system)
-----------------
CacheManager
EventBus

видно у 
class CacheManager:
_instance = None
--------------------------------
Observer Pattern / Event System (тримає систему підписів та передачі подій між модулями)
--------------------------------
EventBus
streaming logs
live tactical updates

видно у 
events.emit("log", data)
events.subscribe(...)

---------------
Proxy Pattern (контролює доступ до захищених API через авторизацію)
--------------
SecurityProxy
VanguardSystem

видно у 
proxy = APIProxy(JWTAuth(...))

-------------------
REST API / FastAPI (дружить взаємодії між frontend та backend частинами)
-------------------
/api/agents
/api/cache
/api/security
/api/tactics

видно у 
@app.get("/api/agents")

----------------
Streaming / SSE (оновлювює інформацію без перезавантаження сторінки)
---------------
live logs
agents stream

видно у 
StreamingResponse(...)

---------------------
для запуску 
--------------------
pip install -r requirements.txt 
uvicorn main:app --reload
