# Chartflix Backend — Beginner's Guide

A plain-English explanation of every concept, pattern, and decision used in this project.
Read this when you come back after a break and need a refresher.

---

## Table of Contents

1. [How a request travels through the app](#1-how-a-request-travels-through-the-app)
2. [The 4-file module pattern](#2-the-4-file-module-pattern)
3. [FastAPI basics](#3-fastapi-basics)
4. [SQLAlchemy — talking to the database](#4-sqlalchemy--talking-to-the-database)
5. [Pydantic — validating data](#5-pydantic--validating-data)
6. [Authentication — JWT + bcrypt](#6-authentication--jwt--bcrypt)
7. [The standard API response shape](#7-the-standard-api-response-shape)
8. [Alembic — database migrations](#8-alembic--database-migrations)
9. [pydantic-settings — config and .env](#9-pydantic-settings--config-and-env)
10. [Dependency Injection — Depends()](#10-dependency-injection--depends)
11. [Exceptions — clean error handling](#11-exceptions--clean-error-handling)
12. [Folder structure explained](#12-folder-structure-explained)
13. [Webhooks — receiving signals from trading platforms](#13-webhooks--receiving-signals-from-trading-platforms)
14. [Background Tasks — non-blocking processing](#14-background-tasks--non-blocking-processing)
15. [Design Patterns — Strategy, Factory, Singleton, Cache-Aside](#15-design-patterns--strategy-factory-singleton-cache-aside)
16. [Redis Pub/Sub — real-time WebSocket broadcasting](#16-redis-pubsub--real-time-websocket-broadcasting)
17. [WebSocket — live alerts in the browser](#17-websocket--live-alerts-in-the-browser)
18. [User approval flow](#18-user-approval-flow)

---

## 1. How a request travels through the app

Imagine a customer (HTTP request) walking into a restaurant:

```
HTTP Request
    │
    ▼
main.py          ← The front door. Sets up the app, registers all routes.
    │
    ▼
router.py        ← The waiter. Receives the order, knows which kitchen to send it to.
    │
    ▼
controller.py    ← The expeditor. Takes the finished dish, plates it nicely (APIResponse).
    │
    ▼
service.py       ← The chef. Actual cooking — business logic, decisions, validation.
    │
    ▼
repository.py    ← The pantry. Only knows how to fetch/store ingredients (SQL queries).
    │
    ▼
database         ← The actual fridge (PostgreSQL on Supabase).
```

---

## 2. The 4-file module pattern

Every feature has exactly 4 files:

```
app/modules/auth/
├── router.py       → Define URLs and HTTP methods
├── controller.py   → Receive request, call service, wrap response
├── service.py      → Business logic (the "brain")
└── repository.py   → Database queries only (no logic)
```

| File | Responsibility | What it should NOT do |
|------|---------------|----------------------|
| router.py | URL + HTTP method + dependencies | Any logic |
| controller.py | Call service, build response | Business decisions |
| service.py | All business logic | SQL queries |
| repository.py | SQL queries only | Business logic, HTTP stuff |

---

## 3. FastAPI basics

### Defining a route

```python
@router.post("/login")
async def login(
    data: LoginRequest,                        # request body — Pydantic validates it
    db: AsyncSession = Depends(get_db)         # injected DB session
):
    return await controller.login(db, data)
```

### async / await

FastAPI is async — it handles many requests at the same time.
Think of a waiter taking orders from multiple tables, not finishing one before moving to the next.

- `async def` = this function can be paused while waiting
- `await` = pause here and wait for this slow operation (DB call, HTTP request)

---

## 4. SQLAlchemy — talking to the database

SQLAlchemy is an ORM — lets you write Python instead of raw SQL.

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
```

```python
# SELECT
result = await db.execute(select(User).where(User.email == email))
user = result.scalar_one_or_none()

# INSERT
user = User(email="x@x.com", password="hashed")
db.add(user)
await db.commit()
await db.refresh(user)
```

---

## 5. Pydantic — validating data

Pydantic validates incoming data automatically. Wrong data → 422 error before your code runs.

```python
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str | None = None
```

`model_dump(exclude_unset=True)` — returns only fields the client sent, not all fields. Critical for PATCH endpoints so you don't accidentally wipe fields.

---

## 6. Authentication — JWT + bcrypt

### bcrypt
Passwords are hashed — one-way, cannot be reversed. Cost factor 12 = slow by design (brute force protection).

### JWT
Signed token proving who you are. Contains `sub` (user id), `role`, `exp` (expiry).

- **Access token** — 15 min. Sent in every request: `Authorization: Bearer <token>`
- **Refresh token** — 7 days. Used only to get a new access token.

```
Login → access_token + refresh_token
Every request → Authorization: Bearer <access_token>
Expired → POST /auth/refresh → new tokens
Logout → refresh token deleted from DB
```

---

## 7. The standard API response shape

Every response looks the same:

```json
{ "success": true, "data": {}, "message": "Done" }
{ "success": false, "data": null, "message": "Not found" }
```

The `success()` helper in `app/utils/response.py` builds this automatically.

---

## 8. Alembic — database migrations

Version control for your DB schema. Add a column in Python → generate migration → apply it.

```bash
alembic revision --autogenerate -m "add is_approved to users"
alembic upgrade head
```

**Important:** When adding a `NOT NULL` column to a table with existing rows, always add `server_default` in the migration file, otherwise PostgreSQL will reject it.

```python
# Wrong — will fail if table has rows
op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=False))

# Correct
op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='false'))
```

---

## 9. pydantic-settings — config and .env

```python
class Settings(BaseSettings):
    SECRET_KEY: str          # required — app crashes on startup if missing
    DATABASE_URL: str
    DEBUG: bool = False      # optional with default
    WEBHOOK_SECRET: str

settings = Settings()        # reads .env automatically
```

Better than `os.getenv()` — crashes immediately with a clear error if a variable is missing.

---

## 10. Dependency Injection — Depends()

`Depends()` runs setup code before your route and injects the result.

```python
# DB session — automatically opened and closed
async def get_db():
    async with AsyncSessionFactory() as session:
        yield session

# Auth check — raises 401 if token is invalid
async def get_current_user(credentials = Depends(security), db = Depends(get_db)):
    ...

# Role check — raises 403 if wrong role
def require_role(*roles):
    async def check(user = Depends(get_current_user)):
        if user.role not in roles:
            raise ForbiddenException()
    return check

# Approval check — raises 403 if is_approved = false
async def require_approved(user = Depends(get_current_user)):
    if user.role != "admin" and not user.is_approved:
        raise HTTPException(403, "Access not approved")
    return user
```

---

## 11. Exceptions — clean error handling

```python
raise NotFoundException("Alert not found")
raise UnauthorizedException("Invalid token")
raise ForbiddenException("Access denied")
```

All produce the same JSON shape. The `app_exception_handler` in `main.py` catches them all.

---

## 12. Folder structure explained

```
chartflix-backend/
├── main.py               ← App entry point. CORS, routers, exception handlers, startup tasks.
├── start.py              ← (legacy) — now replaced by CMD in Dockerfile
├── Dockerfile            ← Python 3.10-slim, 2 uvicorn workers
├── requirements.txt
├── alembic.ini
│
├── alembic/
│   └── versions/         ← Migration files (commit these)
│
└── app/
    ├── core/
    │   ├── config.py         ← settings object — reads .env
    │   ├── database.py       ← async engine, get_db(), AsyncSessionFactory
    │   ├── security.py       ← JWT + bcrypt
    │   ├── dependencies.py   ← get_current_user, require_role, require_approved
    │   ├── exceptions.py     ← AppException and subtypes
    │   └── websocket.py      ← ConnectionManager, ALERT_CHANNEL, start_redis_listener()
    │
    ├── models/               ← SQLAlchemy ORM models
    ├── schemas/              ← Pydantic request/response shapes
    │
    ├── modules/
    │   ├── auth/
    │   ├── users/
    │   ├── alerts/
    │   ├── recommendations/
    │   ├── admin/
    │   ├── webhook/          ← Receives alerts from TradingView/ChartInk
    │   └── websocket/        ← WebSocket endpoint
    │
    ├── services/
    │   └── option_chain/
    │       ├── constants.py      ← URLs, symbols, resolve_category()
    │       ├── fyers_client.py   ← Singleton Fyers API session
    │       ├── option_chain.py   ← CSV fetch, expiry, strike chain, quotes
    │       └── strategies.py     ← NSEBSEStrategy, MCXStrategy, StrategyFactory
    │
    └── utils/
        ├── response.py
        ├── logger.py
        └── pagination.py
```

---

## 13. Webhooks — receiving signals from trading platforms

A webhook is an HTTP POST that an external platform sends to your server when something happens.

TradingView/ChartInk sends a POST to your URL when a trading signal fires:
```
POST /api/v1/webhook/bullish?secret=abc123
{ "stocks": "NIFTY,RELIANCE", "trigger_prices": "22500,1400" }
```

**Security:** The secret in the URL query param acts as a password. If it doesn't match `WEBHOOK_SECRET` in your env, the request is rejected.

**Why query param instead of body?**
ChartInk doesn't allow editing the request body — so the secret goes in the URL instead:
```
https://api.chartflix.in/api/v1/webhook/bullish?secret=your_secret_here
```

**Important:** Never use special characters (`#`, `|`, `)`) in the secret — they break URL parsing. Use `secrets.token_hex(32)` to generate a safe one.

---

## 14. Background Tasks — non-blocking processing

When a webhook arrives, enriching it with option chain data takes 3-5 seconds (CSV fetch + Fyers API calls). If we made the webhook caller wait that long, TradingView/ChartInk would time out and mark the webhook as failed.

**Solution:** Background tasks — respond immediately, process in the background.

```python
@router.post("/bullish")
async def bullish_webhook(data: WebhookRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(webhook_service.process_bulk, stocks, prices, "BULLISH")
    return success(message="Alert queued")  # responds in <50ms
    # process_bulk runs after the response is sent
```

The caller gets a 200 response instantly. The heavy processing happens after.

**AsyncSessionFactory:** Background tasks can't use the request's DB session (it closes when the request ends). They create their own:

```python
async def process_bulk(self, stocks, prices, direction, category):
    async with AsyncSessionFactory() as db:   # own session
        for symbol, price in zip(stocks, prices):
            await self.process_alert(db, symbol, price, direction)
```

---

## 15. Design Patterns — Strategy, Factory, Singleton, Cache-Aside

### Strategy Pattern
Different algorithms that can be swapped at runtime.

NSE/BSE options → `NSEBSEStrategy` (pick ITM2 → ITM1 → ATM by spread)
MCX commodities → `MCXStrategy` (pick first instrument within spread threshold)

Both implement the same interface — the caller doesn't know which one runs.

### Factory Pattern
A function that decides which strategy to create:

```python
class StrategyFactory:
    @staticmethod
    def get(scrip: str):
        if scrip.upper() in MCX_SYMBOLS:
            return MCXStrategy()
        return NSEBSEStrategy()
```

Caller just does `StrategyFactory.get("GOLD")` — no if/else scattered across the code.

### Singleton Pattern
One instance shared across all requests:

```python
fyers_client = FyersClient()         # one login session
option_chain_service = OptionChainService()  # one service instance
```

If every request created a new FyersClient, you'd login to Fyers thousands of times per day.

### Cache-Aside Pattern
Check cache first. If miss, fetch from source and store in cache.

```python
cached = await redis.get(cache_key)
if cached:
    return pickle.loads(cached)        # cache hit — fast

data = fetch_from_fyers()              # cache miss — slow
await redis.set(cache_key, pickle.dumps(data), ex=21600)  # store for 6h
return data
```

The Fyers CSV is 20MB+ but we filter it per symbol before caching. Each symbol gets its own small Redis key.

---

## 16. Redis Pub/Sub — real-time WebSocket broadcasting

**The problem:** With 2 Uvicorn workers (processes), each has its own memory. If a webhook hits Worker 1 and users are connected to Worker 2's WebSocket, they'd never get the alert.

```
Worker 1 (gets webhook)     Worker 2 (has connected users)
───────────────────────     ──────────────────────────────
broadcasts to its own   ✗   users connected here get nothing
WebSocket clients
```

**Solution:** Redis Pub/Sub — a message channel all processes subscribe to.

```
Worker 1           Redis Channel         Worker 2
────────           ─────────────         ────────
PUBLISH msg   →   chartflix:alerts  →   SUBSCRIBE listener
                                           → broadcast to WS clients ✓
```

```python
# Publisher (webhook service)
await redis.publish("chartflix:alerts", json_message)

# Subscriber (runs on startup in all workers)
async def start_redis_listener():
    pubsub = redis.pubsub()
    await pubsub.subscribe("chartflix:alerts")
    while True:
        message = await pubsub.get_message(...)
        if message:
            await manager.broadcast(message["data"])
```

Pub/Sub is **fire-and-forget** — if no one is subscribed, the message is lost. That's fine here because alerts are stored in the DB anyway.

---

## 17. WebSocket — live alerts in the browser

WebSocket is a persistent two-way connection between browser and server. Unlike HTTP (request → response → done), WebSocket stays open and the server can push data any time.

**Connection:** `wss://api.chartflix.in/ws/alerts?token=<jwt>`

**Authentication:**
- JWT passed as query param (WebSockets can't send custom headers from the browser)
- On connect: decode token + check user exists + check `is_approved`
- If invalid → close with code 4001 (unauthorized) or 4003 (not approved)

**Why only on connect?**
Token is validated once when the WebSocket is established. If it expires while connected, the user stays connected until they disconnect. On reconnect, they'll get 4001 and need a fresh token.

```python
@router.websocket("/ws/alerts")
async def alerts_websocket(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return
    # check is_approved...
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()   # keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## 18. User approval flow

By default, new users have `is_approved = false`. They can log in but can't see alerts.

```
User registers → is_approved = false
    ↓
Tries GET /alerts → 403 "Access not approved. Please contact admin."
    ↓
Admin sees user in GET /admin/users
    ↓
Admin calls PATCH /admin/users/{id}/approve
    ↓
is_approved = true → user can now see alerts and connect to WebSocket
```

**Why skip this for admin?**
Admin always has `is_approved` bypass — they manage the platform and should never be locked out.

---

## Quick reference — what lives where?

| I want to... | Go to... |
|---|---|
| Add a new API endpoint | `modules/<feature>/router.py` |
| Add business logic | `modules/<feature>/service.py` |
| Add a SQL query | `modules/<feature>/repository.py` |
| Add a new DB table | `models/<name>.py` → alembic migration |
| Change request/response shape | `schemas/<feature>.py` |
| Change auth / approval logic | `core/dependencies.py` |
| Change WebSocket broadcast | `core/websocket.py` |
| Add a new trading symbol category | `services/option_chain/constants.py` |
| Change option selection logic | `services/option_chain/strategies.py` |

---

*When in doubt: keep logic in service.py, keep SQL in repository.py, keep HTTP stuff in router.py.*
