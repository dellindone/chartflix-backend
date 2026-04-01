# Chartflix Backend

A REST API backend for **Chartflix** — a trading alert and stock recommendation platform.

Analysts publish stock alerts (option contracts) and stock recommendations. Regular users consume published content. Admins manage users and moderate content. Trading platforms (TradingView, ChartInk) push alerts via webhook which are enriched with live option chain data and broadcast in real-time via WebSocket.

---

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10 | Runtime |
| FastAPI | 0.111.0 | Web framework |
| Uvicorn | 0.29.0 | ASGI server (2 workers) |
| SQLAlchemy | 2.0.30 | ORM (async mode) |
| asyncpg | 0.29.0 | PostgreSQL async driver |
| Alembic | 1.13.1 | Database migrations |
| Pydantic | 2.7.1 | Data validation |
| pydantic-settings | - | Config from .env |
| python-jose | 3.3.0 | JWT tokens |
| passlib | 1.7.4 | Password hashing (bcrypt) |
| Redis (aioredis) | 5.0.4 | Pub/Sub for WebSocket + CSV caching |
| fyers-apiv3 | 3.1.11 | Option chain data |
| pandas | 2.1.4 | CSV processing |
| numpy | 1.26.4 | Numerical operations |
| pyotp | - | Fyers TOTP login |
| requests | - | Sync HTTP (CSV fetch) |

---

## Roles

| Role | How Assigned | Permissions |
|------|-------------|-------------|
| **USER** | Default on signup | Read approved content (requires `is_approved=true`) |
| **ANALYST** | Admin promotes | Create, edit, publish/unpublish own alerts & recommendations |
| **ADMIN** | Seeded in DB manually | Everything. Promote/revoke analyst. Approve/reject users. Delete any content. |

### Access Approval

New users have `is_approved = false` by default. They cannot see alerts until an admin approves them.

```
User registers → is_approved = false
     ↓
Admin approves via PATCH /admin/users/{id}/approve
     ↓
is_approved = true → user can now see alerts and connect via WebSocket
```

---

## Content Lifecycle

```
DRAFT  →  (analyst publishes)  →  ACTIVE  →  (analyst unpublishes)  →  INACTIVE
                                     │
                              (admin deletes)
                                     │
                                gone from DB
```

- On create → always `status = INACTIVE` (draft)
- INACTIVE → invisible to USER role
- ACTIVE → visible to approved users
- WebSocket broadcast fires only when toggled to ACTIVE

---

## Database Schema

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| name | String | |
| email | String | UNIQUE |
| password | String | bcrypt hashed |
| phone | String | nullable |
| location | String | nullable |
| photo_url | String | nullable |
| role | Enum | USER, ANALYST, ADMIN (default: USER) |
| is_approved | Boolean | default: false |
| created_at | DateTime | |
| updated_at | DateTime | |

### analysts
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| user_id | UUID | FK → users.id (UNIQUE) |
| tag | String | e.g. "Technical Analyst" |
| avatar_bg | String | hex color |

### alerts
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| analyst_id | UUID | FK → users.id |
| category | Enum | INDEX, STOCK, COMMODITY |
| direction | Enum | BULLISH, BEARISH |
| exchange | String | NSE, BSE, MCX |
| contract | String | e.g. NIFTY2640722400PE |
| symbol | String | e.g. NIFTY |
| ltp | Float | underlying last traded price |
| strike | Float | |
| option_ltp | Float | option contract price |
| lot_size | Integer | from Fyers CSV |
| investment | Float | lot_size × option_ltp |
| status | Enum | ACTIVE, INACTIVE |
| published_at | DateTime | nullable |

### recommendations, refresh_tokens
_(unchanged from v1)_

---

## Authentication Flow

```
1. Login → access_token (JWT, 15 min) + refresh_token (JWT, 7 days)
2. Protected routes → Authorization: Bearer <access_token>
3. Token expired → POST /auth/refresh → new tokens
4. Logout → refresh token deleted from DB
```

JWT Payload:
```json
{ "sub": "user_id", "role": "analyst", "exp": 1234567890 }
```

---

## API Endpoints

Base prefix: `/api/v1`

### Auth
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Create account (role=USER, is_approved=false) |
| POST | `/auth/login` | Public | Returns access_token + refresh_token |
| POST | `/auth/logout` | Authenticated | Delete refresh token |
| POST | `/auth/refresh` | Public | Returns new tokens |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/users/me` | Authenticated | Get own profile (includes is_approved) |
| PATCH | `/users/me` | Authenticated | Update profile |

### Alerts
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/alerts` | Approved users | Paginated active alerts |
| GET | `/alerts/my` | Analyst, Admin | Own alerts including drafts |
| GET | `/alerts/{id}` | Approved users | Single alert |
| POST | `/alerts` | Analyst, Admin | Create alert (status=INACTIVE) |
| PATCH | `/alerts/{id}` | Analyst (own), Admin | Edit alert |
| PATCH | `/alerts/{id}/publish` | Analyst (own), Admin | Toggle ACTIVE/INACTIVE + broadcast |
| DELETE | `/alerts/{id}` | Admin | Permanent delete |

### Recommendations
_(same pattern as alerts)_

### Admin
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/admin/users` | Admin | List all users with approval status |
| PATCH | `/admin/users/{id}/role` | Admin | Set role to ANALYST or USER |
| PATCH | `/admin/users/{id}/approve` | Admin | Set is_approved = true |
| PATCH | `/admin/users/{id}/reject` | Admin | Set is_approved = false |
| DELETE | `/admin/content/{id}` | Admin | Delete any alert or recommendation |

### Webhook
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/webhook/bullish?secret=<key>` | Secret key | Receive bullish alerts from TradingView/ChartInk |
| POST | `/webhook/bearish?secret=<key>` | Secret key | Receive bearish alerts |

### WebSocket
| Endpoint | Access | Description |
|----------|--------|-------------|
| `GET /ws/alerts?token=<jwt>` | Approved users | Real-time alert stream |

---

## Webhook Flow

```
TradingView / ChartInk
        │
        │  POST /webhook/bullish?secret=xxx
        │  { stocks: "NIFTY,RELIANCE", trigger_prices: "22500,1400" }
        ▼
   FastAPI Webhook Router
        │
        │  BackgroundTask (async, non-blocking)
        ▼
   WebhookService.process_bulk()
        │
        ├─ resolve_category(symbol)  → INDEX / STOCK / COMMODITY
        ├─ OptionChainService.get_best_instrument()
        │     ├─ Fetch Fyers CSV (or Redis cache, 6h TTL)
        │     ├─ Find next expiry
        │     ├─ Build ATM strike chain
        │     ├─ Fetch live quotes from Fyers API
        │     └─ Strategy (NSEBSEStrategy / MCXStrategy) → best contract
        ├─ Save Alert to DB (analyst = system@chartflix.com)
        └─ Publish to Redis channel "chartflix:alerts"
                │
                ▼
        Redis Pub/Sub (Upstash)
                │
                ▼
        All Railway instances subscribed
                │
                ▼
        WebSocket broadcast to all connected approved users
```

---

## WebSocket + Redis Pub/Sub

The WebSocket broadcaster uses Redis Pub/Sub so multiple server instances (workers) stay in sync.

```
Worker 1 (webhook hit)     Redis Channel          Worker 2 (users connected)
────────────────────        ──────────────          ────────────────────────
PUBLISH alert message  →   chartflix:alerts  →     SUBSCRIBE listener
                                                      → broadcast to WS clients
```

Each Railway instance subscribes to `chartflix:alerts` on startup. Any publish from any instance reaches all connected clients across all workers.

---

## Option Chain Service

Enriches raw webhook signals with live option contract data from Fyers API.

| Component | Pattern | Responsibility |
|-----------|---------|---------------|
| `FyersClient` | Singleton | One login session shared across requests |
| `OptionChainService` | Service | CSV fetch, expiry selection, strike chain, quotes |
| `NSEBSEStrategy` | Strategy | Pick ITM2 → ITM1 → ATM, filter by spread |
| `MCXStrategy` | Strategy | Pick first instrument within spread threshold |
| `StrategyFactory` | Factory | Returns correct strategy based on symbol |
| Redis CSV Cache | Cache-Aside | CSV cached per symbol for 6 hours |

---

## Design Patterns

| Pattern | Where Used | Purpose |
|---------|-----------|---------|
| Repository | `repository.py` | SQL only, no logic |
| Service | `service.py` | All business logic |
| Facade | `controller.py` | Thin wrapper, standard response |
| Strategy | `strategies.py` | NSE/BSE vs MCX option selection |
| Factory | `StrategyFactory` | Pick strategy based on symbol |
| Singleton | `FyersClient`, `OptionChainService` | One instance shared app-wide |
| Cache-Aside | `_fetch_csv()` | Check Redis first, fetch if miss, store result |
| Pub/Sub | `websocket.py` + `service.py` | Decouple alert creation from WS delivery |
| Background Tasks | `webhook/router.py` | Non-blocking webhook processing |
| Dependency Injection | FastAPI `Depends()` | DB sessions, auth, role + approval checks |

---

## Environment Variables

```env
APP_NAME=Chartflix
DEBUG=false
SECRET_KEY=<32+ char secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

DATABASE_URL=postgresql+asyncpg://...supabase.co:5432/postgres?ssl=require
REDIS_URL=rediss://...:password@...upstash.io:6379

WEBHOOK_SECRET=<alphanumeric only, no special chars>
ALLOWED_ORIGINS=https://chartflix.in,https://www.chartflix.in,http://localhost:5173

FYERS_CLIENT_ID=
FYERS_SECRET_KEY=
FYERS_REDIRECT_URI=
FYERS_ID=
FYERS_PIN=
FYERS_TOTP_SECRET=
```

> Generate WEBHOOK_SECRET with: `python3 -c "import secrets; print(secrets.token_hex(32))"`

---

## Getting Started

```bash
# 1. Clone and setup
git clone <repo-url> && cd chartflix-backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Fill in DATABASE_URL, REDIS_URL, SECRET_KEY, WEBHOOK_SECRET

# 3. Migrate DB
alembic upgrade head

# 4. Approve admin in DB
# UPDATE users SET is_approved = true WHERE role = 'admin';

# 5. Run
uvicorn main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

---

## Common Commands

```bash
uvicorn main:app --reload
alembic revision --autogenerate -m "describe change"
alembic upgrade head
alembic downgrade -1
alembic current
alembic history
```

---

*Project: Chartflix Backend | Stack: FastAPI + PostgreSQL + Redis + Fyers | Version: 2.0*
