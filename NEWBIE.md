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

**Example: User hits POST /api/v1/auth/login**

1. `main.py` receives the request, routes it to `auth_router`
2. `router.py` matches `/login`, calls `controller.login(db, data)`
3. `controller.py` calls `auth_service.login(db, data)`
4. `service.py` checks email exists, verifies password, creates tokens
5. `repository.py` runs the actual SQL to fetch the user from DB
6. Result flows back up and `controller.py` wraps it in `APIResponse`
7. JSON response sent back to client

---

## 2. The 4-file module pattern

Every feature in this project has exactly 4 files:

```
app/modules/auth/
├── router.py       → Define URLs and HTTP methods
├── controller.py   → Receive request, call service, wrap response
├── service.py      → Business logic (the "brain")
└── repository.py   → Database queries only (no logic)
```

**Why split it this way?**

| File | Responsibility | What it should NOT do |
|------|---------------|----------------------|
| router.py | URL + HTTP method + dependencies | Any logic |
| controller.py | Call service, build response | Business decisions |
| service.py | All business logic | SQL queries |
| repository.py | SQL queries only | Business logic, HTTP stuff |

**Analogy:**
- `router.py` = address on a letter (just tells where to go)
- `controller.py` = receptionist (takes the message, passes it on, gives back a formatted reply)
- `service.py` = the actual employee doing the work
- `repository.py` = the filing cabinet (just store and retrieve)

---

## 3. FastAPI basics

### Defining a route

```python
@router.post("/login")           # HTTP method + URL path
async def login(                 # async because DB calls are async
    data: LoginRequest,          # request body — Pydantic validates it automatically
    db: AsyncSession = Depends(get_db)  # injected DB session
):
    return await controller.login(db, data)
```

### async / await

FastAPI is **async** — it can handle many requests at the same time without waiting.
Think of it like a waiter taking orders from multiple tables simultaneously, not finishing one table before moving to the next.

- `async def` = "this function can be paused while waiting"
- `await` = "pause here and wait for this slow operation (like a DB call) to finish"

Without async, your server would be frozen while waiting for the database — one request at a time.

### Depends()

`Depends(get_db)` tells FastAPI: *"Before calling this function, run `get_db()` and inject the result as `db`."*

It's like saying: *"Before I cook, make sure the kitchen is set up."*

FastAPI handles the setup and teardown automatically.

---

## 4. SQLAlchemy — talking to the database

SQLAlchemy is an ORM — **Object Relational Mapper**. It lets you write Python instead of raw SQL.

### Defining a table (Model)

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"          # actual table name in PostgreSQL

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(String, nullable=False)
```

- `Mapped[str]` = type hint telling SQLAlchemy and Python this column holds a string
- `mapped_column(...)` = defines the actual column constraints
- `primary_key=True` = this column uniquely identifies each row
- `nullable=False` = this column cannot be empty

### Querying the database

```python
# SELECT * FROM users WHERE email = 'x@x.com' LIMIT 1
result = await db.execute(select(User).where(User.email == email))
user = result.scalar_one_or_none()  # returns User or None
```

### Writing to the database

```python
user = User(email="x@x.com", password="hashed")
db.add(user)          # stage the insert
await db.commit()     # actually write to DB
await db.refresh(user) # reload from DB (to get auto-generated id, timestamps)
```

### Relationships

```python
# In User model:
analyst_profile: Mapped["Analyst"] = relationship("Analyst", back_populates="user")

# In Analyst model:
user: Mapped["User"] = relationship("User", back_populates="analyst_profile")
```

This lets you do `user.analyst_profile` in Python and SQLAlchemy handles the SQL JOIN automatically.

### TimestampMixin

A mixin is a **reusable chunk of code** you attach to a class.
`TimestampMixin` automatically adds `created_at` and `updated_at` to any model that inherits it.

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

`server_default=func.now()` = PostgreSQL itself sets the timestamp — not Python.

---

## 5. Pydantic — validating data

Pydantic validates incoming request data before it reaches your code.
If a user sends wrong data, Pydantic rejects it with a 422 error automatically.

### Request schema

```python
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr        # validates it's a proper email format
    password: str
    phone: str | None = None  # optional field

    @field_validator("password")
    @classmethod
    def password_length(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
```

### `model_dump()`

Converts a Pydantic object to a plain Python dict:

```python
token_data = TokenResponse(access_token="abc", refresh_token="xyz")
token_data.model_dump()
# → {"access_token": "abc", "refresh_token": "xyz"}
```

---

## 6. Authentication — JWT + bcrypt

### bcrypt — password hashing

**Never store plain passwords.** bcrypt converts a password into a scrambled string that cannot be reversed.

```
"mypassword123"  →  bcrypt  →  "$2b$12$4skx...bqW"
```

- Cost factor 12 = bcrypt runs 2^12 = 4096 rounds. Slow by design — makes brute force attacks expensive.
- SHA256 pre-hash = if password > 72 bytes, we hash it first (bcrypt has a 72-byte limit).

Verification:

```python
verify_password("mypassword123", "$2b$12$4skx...bqW")  # → True
verify_password("wrongpassword", "$2b$12$4skx...bqW")  # → False
```

### JWT — access tokens

JWT = **JSON Web Token**. It's a signed string that proves who you are.

Structure: `header.payload.signature`

```json
// Payload (decoded)
{
  "sub": "user-uuid-here",   // subject = user id
  "role": "analyst",
  "exp": 1234567890          // expiry timestamp
}
```

- **Access token** — short lived (15 min). Sent in every request header: `Authorization: Bearer <token>`
- **Refresh token** — long lived (7 days). Used only to get a new access token when the old one expires.

Why two tokens?
- If someone steals your access token, it expires in 15 min — minimal damage.
- Refresh token is stored in DB as a hash — we can invalidate it on logout.

### Authentication flow

```
1. Register/Login → server creates access_token + refresh_token → returns both in response body
2. Client stores them
3. Every API call → client sends: Authorization: Bearer <access_token>
4. Access token expires → client sends refresh_token → server gives new access_token
5. Logout → server deletes refresh_token from DB → it can never be used again
```

---

## 7. The standard API response shape

Every single response from this API looks the same:

```json
// Success
{
  "success": true,
  "data": { ... },
  "message": "Login successful"
}

// Success with pagination
{
  "success": true,
  "data": [ ... ],
  "message": "OK",
  "meta": { "page": 1, "limit": 20, "total": 84 }
}

// Error
{
  "success": false,
  "data": null,
  "message": "Invalid email or password"
}
```

**Why?** Frontend developers know exactly what shape to expect. No surprises.

The `success()` helper in `app/utils/response.py` builds this shape automatically.

---

## 8. Alembic — database migrations

Alembic is version control for your database schema.

### Why not just edit the DB directly?

If you add a column directly in Supabase but your teammate doesn't know, their local DB is out of sync. Migrations solve this — everyone runs the same migration files to stay in sync.

### Key commands

```bash
# Generate a migration by comparing your models to the current DB
alembic revision --autogenerate -m "add phone column to users"

# Apply all pending migrations
alembic upgrade head

# Rollback the last migration
alembic downgrade -1

# See what version the DB is at
alembic current
```

### What autogenerate does

Alembic looks at your Python models (`app/models/`) and compares them to the actual DB. If you added a column in Python but it doesn't exist in the DB, Alembic generates a migration to add it.

### Important rule

**Always review the generated migration file before running `upgrade head` on production.**
Alembic is smart but not perfect — especially with column renames (it sees it as delete + add, which loses data).

---

## 9. pydantic-settings — config and .env

`pydantic-settings` reads environment variables and validates them just like Pydantic validates request data.

```python
class Settings(BaseSettings):
    SECRET_KEY: str          # required — app crashes if missing
    DATABASE_URL: str        # required
    DEBUG: bool = False      # optional — defaults to False
    REDIS_URL: str = "redis://localhost:6379"  # optional with default

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()  # reads .env automatically
```

**Why not use `os.getenv()`?**

- `os.getenv("SECRET_KEY")` returns `None` silently if missing — your app crashes somewhere random later.
- `BaseSettings` crashes immediately at startup with a clear error if a required variable is missing.
- You get type validation for free — `DEBUG: bool` converts the string `"true"` to Python `True`.

**Never commit `.env`** — it contains secrets. Use `.env.example` with placeholder values as a template.

---

## 10. Dependency Injection — Depends()

`Depends()` is FastAPI's way of sharing reusable setup code across routes.

### DB session injection

```python
async def get_db():
    async with AsyncSessionFactory() as session:
        yield session   # give the session to the route
        # after the route finishes, session is automatically closed

# In router:
async def login(db: AsyncSession = Depends(get_db)):
    # db is ready to use — no setup needed here
```

### Auth injection

```python
async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    payload = decode_token(token)
    user = await get_user_by_id(db, payload["sub"])
    return user

# In router — protected route:
async def get_my_profile(current_user: User = Depends(get_current_user)):
    # current_user is automatically fetched and verified
```

### Role checking

```python
def require_role(*roles):
    async def check(current_user = Depends(get_current_user)):
        if current_user.role not in roles:
            raise ForbiddenException()
        return current_user
    return check

# In router:
@router.post("/alerts")
async def create_alert(current_user = Depends(require_role("analyst", "admin"))):
    ...
```

---

## 11. Exceptions — clean error handling

Instead of returning different error formats across the app, we use custom exceptions that always produce the same JSON shape.

```python
# Raise this anywhere in service or repository:
raise NotFoundException("Alert not found")
raise UnauthorizedException("Invalid token")
raise ForbiddenException("You cannot edit this")
raise ConflictException("Email already registered")

# They all produce:
{
  "success": false,
  "data": null,
  "message": "Email already registered"
}
```

The `app_exception_handler` in `main.py` catches all `AppException` subclasses and formats them.

**Why not use `HTTPException`?**

FastAPI's built-in `HTTPException` produces `{"detail": "..."}` — a different shape than our standard response. Custom exceptions keep everything consistent.

---

## 12. Folder structure explained

```
chartflix-backend/
│
├── main.py               ← App entry point. Creates FastAPI app, registers routers,
│                           sets up middleware (CORS), registers exception handlers.
│
├── requirements.txt      ← All Python packages needed. Run: pip install -r requirements.txt
│
├── alembic.ini           ← Alembic config file. Points to alembic/ folder.
│
├── .env                  ← Your secrets. NEVER commit this.
├── .env.example          ← Template showing what variables are needed. Safe to commit.
│
├── alembic/
│   ├── env.py            ← Tells Alembic how to connect to DB and which models to track.
│   └── versions/         ← Auto-generated migration files. Commit these.
│
└── app/
    ├── core/             ← Shared infrastructure used by all modules.
    │   ├── config.py     ← Reads .env, exposes `settings` object.
    │   ├── database.py   ← Creates DB engine, session factory, get_db() function.
    │   ├── security.py   ← hash_password(), verify_password(), create_access_token(), decode_token()
    │   ├── dependencies.py ← get_current_user(), require_role() — used in routers via Depends()
    │   └── exceptions.py ← AppException base class + NotFoundException, UnauthorizedException, etc.
    │
    ├── models/           ← SQLAlchemy models = Python representation of DB tables.
    │   ├── base.py       ← Base class all models inherit from. TimestampMixin lives here.
    │   ├── user.py       ← users table
    │   ├── analyst.py    ← analysts table (1:1 with users)
    │   ├── alert.py      ← alerts table
    │   ├── recommendation.py ← recommendations table
    │   ├── refresh_token.py  ← refresh_tokens table
    │   └── __init__.py   ← Imports all models so Alembic can detect them.
    │
    ├── schemas/          ← Pydantic schemas = shape of request/response data.
    │   ├── common.py     ← APIResponse[T] generic wrapper. PaginationMeta.
    │   ├── auth.py       ← RegisterRequest, LoginRequest, TokenResponse
    │   └── ...           ← One file per module
    │
    ├── modules/          ← One folder per feature. Each has the 4-file pattern.
    │   ├── auth/
    │   │   ├── router.py      ← @router.post("/login") etc.
    │   │   ├── controller.py  ← Calls service, wraps in success()
    │   │   ├── service.py     ← register(), login(), logout(), refresh()
    │   │   └── repository.py  ← get_user_by_email(), save_refresh_token(), etc.
    │   ├── users/
    │   ├── alerts/
    │   ├── recommendations/
    │   └── admin/
    │
    └── utils/
        ├── response.py    ← success() and error() helper functions
        ├── logger.py      ← get_logger() — structured logging
        └── pagination.py  ← Pagination helpers for list endpoints
```

---

## Quick reference — what lives where?

| I want to... | Go to... |
|---|---|
| Add a new API endpoint | `modules/<feature>/router.py` |
| Add business logic | `modules/<feature>/service.py` |
| Add a SQL query | `modules/<feature>/repository.py` |
| Add a new DB table | `models/<name>.py` then run Alembic |
| Change request/response shape | `schemas/<feature>.py` |
| Change auth logic | `core/security.py` or `core/dependencies.py` |
| Change app settings | `core/config.py` + `.env` |
| Add a new error type | `core/exceptions.py` |

---

*When in doubt: keep logic in service.py, keep SQL in repository.py, keep HTTP stuff in router.py.*
