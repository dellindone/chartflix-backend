# Chartflix Backend

A REST API backend for **Chartflix** — a trading alert and stock recommendation platform.

Analysts publish stock alerts (option contracts) and stock recommendations. Regular users consume published content. Admins manage users and moderate content.

---

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.111.0 | Web framework |
| Uvicorn | 0.29.0 | ASGI server |
| SQLAlchemy | 2.0.30 | ORM (async mode) |
| asyncpg | 0.29.0 | PostgreSQL async driver |
| Alembic | 1.13.1 | Database migrations |
| Pydantic | 2.7.1 | Data validation |
| python-jose | 3.3.0 | JWT tokens |
| passlib | 1.7.4 | Password hashing (bcrypt) |
| Redis | 5.0.4 | Token blacklisting |
| httpx | 0.27.0 | Async HTTP client (tests) |
| pytest | 8.2.0 | Testing framework |

---

## Roles

There are exactly **3 roles** in the system:

| Role | How Assigned | Permissions |
|------|-------------|-------------|
| **USER** | Default on signup | Read published content, edit own profile |
| **ANALYST** | Admin promotes them | Create, edit, publish/unpublish own content. Cannot delete. |
| **ADMIN** | Seeded in DB manually | Everything. Promote/revoke analyst. Delete any content. |

### Authorization Rules

- Analyst can only touch **their own** content (`analyst_id == current_user.id`)
- Only **admin** can delete content
- Only **analyst** and **admin** can create content
- Frontend checks are UX only — **backend is the real gate**

---

## Content Lifecycle

```
DRAFT  →  (analyst publishes)  →  PUBLISHED  →  (analyst unpublishes)  →  DRAFT
                                      │
                               (admin deletes)
                                      │
                                gone from DB
```

- On create → always `status = DRAFT`
- Draft → invisible to USER role
- Published → visible to everyone
- Only analyst (own) or admin can toggle publish
- Only admin can delete — **permanent, no soft delete**

---

## Database Schema

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | String | |
| email | String | UNIQUE, NOT NULL |
| password | String | bcrypt hashed |
| phone | String | nullable |
| location | String | nullable |
| photo_url | String | nullable (S3 URL) |
| role | Enum | USER, ANALYST, ADMIN (default: USER) |
| created_at | DateTime | default: now |
| updated_at | DateTime | auto-update |

### analysts
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id, UNIQUE (1:1) |
| tag | String | e.g. "Technical Analyst - 8 yrs" |
| avatar_bg | String | hex color |
| avatar_color | String | hex color |
| created_at | DateTime | |

### alerts
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| analyst_id | UUID | FK → users.id |
| category | Enum | INDEX, STOCK, COMMODITY |
| direction | Enum | BULLISH, BEARISH |
| exchange | String | e.g. NSE, MCX |
| contract | String | e.g. BANKNIFTY26MAR50000CE |
| symbol | String | e.g. BANKNIFTY |
| ltp | Float | last traded price |
| strike | Float | |
| option_ltp | Float | |
| lot_size | Integer | |
| investment | Float | |
| status | Enum | DRAFT, PUBLISHED (default: DRAFT) |
| published_at | DateTime | nullable |
| created_at | DateTime | |
| updated_at | DateTime | |

### recommendations
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| analyst_id | UUID | FK → analysts.id |
| sym | String | e.g. RELIANCE |
| name | String | e.g. Reliance Industries |
| action | Enum | BUY, SELL, HOLD |
| sector | String | e.g. Energy, IT, Banking |
| cmp | Float | current market price |
| target | Float | |
| stop_loss | Float | |
| note | String | max 500 chars |
| status | Enum | DRAFT, PUBLISHED (default: DRAFT) |
| published_at | DateTime | nullable |
| created_at | DateTime | |
| updated_at | DateTime | |

### refresh_tokens
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users.id |
| token | String | stored hashed |
| expires_at | DateTime | |
| created_at | DateTime | |

---

## Authentication Flow

```
1. Login → validate email + bcrypt password
2. Issue access_token  (JWT, 15 min)  → returned in response body
3. Issue refresh_token (JWT, 7 days)  → set as httpOnly cookie
4. Protected requests  → Authorization: Bearer <access_token>
5. Token expired       → POST /auth/refresh → new access_token
6. Logout              → refresh token added to Redis blacklist
```

**JWT Payload:**
```json
{
  "sub": "user_id",
  "role": "analyst",
  "exp": 1234567890
}
```

- bcrypt cost factor: **12**
- Algorithm: **HS256**

---

## API Endpoints

Base prefix: `/api/v1`

### Auth
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Create account (role=USER) |
| POST | `/auth/login` | Public | Returns access_token, sets refresh cookie |
| POST | `/auth/logout` | Authenticated | Blacklist refresh token in Redis |
| POST | `/auth/refresh` | Public | Uses httpOnly cookie, returns new access_token |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/users/me` | Authenticated | Get own profile |
| PATCH | `/users/me` | Authenticated | Update name, email, phone, location |
| POST | `/users/me/photo` | Authenticated | Upload photo to S3, save URL |

### Alerts
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/alerts` | Public | Published only. Filters: category, direction, date_from, date_to, page, limit |
| GET | `/alerts/my` | Analyst, Admin | Own alerts including drafts |
| GET | `/alerts/{id}` | Public (published), Analyst (own), Admin | Single alert |
| POST | `/alerts` | Analyst, Admin | Create alert (status=DRAFT) |
| PATCH | `/alerts/{id}` | Analyst (own), Admin | Edit alert fields |
| PATCH | `/alerts/{id}/publish` | Analyst (own), Admin | Toggle DRAFT / PUBLISHED |
| DELETE | `/alerts/{id}` | Admin only | Permanent delete |

### Recommendations
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/recommendations` | Public | All published, grouped by analyst |
| GET | `/recommendations/analysts` | Public | List analysts with their published recos |
| GET | `/recommendations/analysts/{id}` | Public | Single analyst + published recos |
| GET | `/recommendations/common` | Public | `?analyst_ids=id1,id2` — overlapping stock picks |
| GET | `/recommendations/my` | Analyst, Admin | Own recos including drafts |
| POST | `/recommendations` | Analyst, Admin | Create reco (status=DRAFT) |
| PATCH | `/recommendations/{id}` | Analyst (own), Admin | Edit reco fields |
| PATCH | `/recommendations/{id}/publish` | Analyst (own), Admin | Toggle DRAFT / PUBLISHED |
| DELETE | `/recommendations/{id}` | Admin only | Permanent delete |

### Admin
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/admin/users` | Admin | List all users with roles |
| PATCH | `/admin/users/{id}/role` | Admin | Set role to ANALYST or USER |
| DELETE | `/admin/content/{id}` | Admin | Delete any alert or recommendation |

---

## Standard API Response

Every response follows this shape:

```json
// Success
{
  "success": true,
  "data": {},
  "message": "Done",
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 84
  }
}

// Error
{
  "success": false,
  "data": null,
  "message": "Unauthorized",
  "error_code": "UNAUTHORIZED"
}
```

---

## Project Structure

```
chartflix-backend/
├── main.py                      # FastAPI app, includes all routers
├── requirements.txt
├── alembic.ini
├── .env                         # never commit
├── .env.example
├── Dockerfile
├── docker-compose.yml
│
└── app/
    ├── core/                    # shared infra — no business logic
    │   ├── config.py            # pydantic BaseSettings, reads .env
    │   ├── database.py          # async engine, AsyncSession, get_db()
    │   ├── security.py          # JWT + password utilities
    │   ├── dependencies.py      # get_current_user(), require_role()
    │   └── exceptions.py        # AppException, HTTP exception handlers
    │
    ├── models/                  # SQLAlchemy ORM (1 file per table)
    │   ├── base.py              # DeclarativeBase, TimestampMixin
    │   ├── user.py
    │   ├── analyst.py
    │   ├── alert.py
    │   ├── recommendation.py
    │   └── refresh_token.py
    │
    ├── schemas/                 # Pydantic v2 (request + response shapes)
    │   ├── common.py            # APIResponse[T], PaginationMeta
    │   ├── auth.py
    │   ├── user.py
    │   ├── alert.py
    │   ├── analyst.py
    │   └── recommendation.py
    │
    ├── modules/                 # one folder per feature domain
    │   ├── auth/
    │   │   ├── router.py        # URL definitions
    │   │   ├── controller.py    # thin wrapper, returns APIResponse
    │   │   ├── service.py       # business logic
    │   │   └── repository.py    # SQL queries only
    │   ├── users/
    │   ├── alerts/
    │   ├── recommendations/
    │   └── admin/
    │
    └── utils/
        ├── response.py          # success() and error() helpers
        ├── logger.py            # structured logging
        └── pagination.py        # paginate() helper
```

---

## Design Patterns

| Pattern | File | Responsibility |
|---------|------|---------------|
| **Repository** | `repository.py` | SQL only. No role checks. No business logic. |
| **Strategy** | `service.py` | All business logic. Calls repository. Raises exceptions. |
| **Facade** | `controller.py` | Thin wrapper. Calls service. Returns standard response. |
| **Dependency Injection** | FastAPI `Depends()` | Inject DB sessions, current user, role checks. |
| **Chain of Responsibility** | Middleware | JWT verify → role check → validation → business logic |

---

## Environment Variables

```env
APP_NAME=Chartflix
DEBUG=false
SECRET_KEY=minimum-32-character-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chartflix

REDIS_URL=redis://localhost:6379

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=chartflix-uploads
AWS_REGION=ap-south-1

ALLOWED_ORIGINS=http://localhost:5173
```

---

## Getting Started

```bash
# 1. Clone the repo
git clone <repo-url>
cd chartflix-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

---

## Out of Scope (v1)

- Email / SMS notifications
- WebSocket real-time alerts
- TradingView webhook integration
- Payments / subscriptions
- Two-factor authentication
- Soft delete
- Approval queue (analyst publishes directly)

---

*Project: Chartflix Backend | Stack: FastAPI + PostgreSQL + Redis | Version: 1.0*
