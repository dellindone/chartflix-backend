# Chartflix — Interview Questions & Answers

Questions based on real concepts used in this project.
Updated after each module is completed.

---

## FastAPI & Python

**Q: Why did you choose FastAPI over Flask or Django?**
> FastAPI is async-first, which means it can handle many concurrent requests without blocking. It also has automatic request validation via Pydantic and auto-generates Swagger docs. Flask is sync by default and Django is heavier — FastAPI is the right fit for a lightweight async API.

**Q: What does `async/await` mean and why does it matter?**
> `async` marks a function that can be paused. `await` is the pause point — "wait for this slow operation, but let others run in the meantime." Without async, a DB query would freeze the entire server until it completes. With async, while one request waits for the DB, another request is being processed.

**Q: What is `Depends()` in FastAPI?**
> It's dependency injection. `Depends(get_db)` tells FastAPI to run `get_db()` before calling the route function and inject the result. It's used for DB sessions, authentication, and role checks — so you don't repeat that setup code in every route.

**Q: How do you protect a route so only logged-in users can access it?**
> Using `Depends(get_current_user)`. FastAPI calls `get_current_user()` which extracts the JWT from the Authorization header, decodes it, fetches the user from DB, and returns them. If the token is invalid or missing, it raises `UnauthorizedException` before the route function even runs.

**Q: How do you restrict a route to specific roles (e.g. admin only)?**
> Using a `require_role()` factory function that returns a dependency. `Depends(require_role("admin"))` checks the current user's role and raises `ForbiddenException` if they don't have permission.

---

## SQLAlchemy & Database

**Q: What is an ORM and why use it?**
> ORM = Object Relational Mapper. It lets you write Python classes instead of raw SQL. `User.email == email` instead of `WHERE email = 'x'`. It also prevents SQL injection by default since parameters are always escaped.

**Q: What is SQLAlchemy 2.0 style and how is it different from 1.x?**
> SQLAlchemy 2.0 uses `Mapped[str]` type annotations and `mapped_column()` instead of the older `Column(String)`. It's more explicit, type-safe, and works better with IDEs and type checkers.

**Q: What is a migration and why do you need Alembic?**
> A migration is a script that changes the database schema (add table, add column, etc.). Alembic tracks these as versioned files — like git for your DB. Without it, you'd manually edit the DB and teammates would be out of sync.

**Q: What does `alembic revision --autogenerate` do?**
> It compares your Python models to the current DB schema and generates a migration file for the differences. If you added a column in Python, Alembic generates `ALTER TABLE ... ADD COLUMN`.

**Q: What is a foreign key and what does `ondelete="CASCADE"` mean?**
> A foreign key links one table to another. `ondelete="CASCADE"` means if the parent row is deleted, all child rows are automatically deleted too. For example, if a user is deleted, all their refresh tokens are deleted automatically.

**Q: What is a relationship in SQLAlchemy?**
> It's a Python-level link between two models. `user.analyst_profile` lets you access the related Analyst object without writing a JOIN query — SQLAlchemy handles that behind the scenes.

**Q: What is `TimestampMixin`?**
> A reusable mixin that adds `created_at` and `updated_at` columns to any model. `server_default=func.now()` means PostgreSQL itself sets the timestamp — not Python — so it's always accurate regardless of timezone differences between app server and DB.

**Q: What is `nullable=False` vs `nullable=True`?**
> `nullable=False` means the column cannot be empty (NOT NULL constraint in DB). `nullable=True` means it can be empty (NULL allowed). If you try to insert a row without a required `nullable=False` column, PostgreSQL throws an error.

---

## Authentication

**Q: Why do you hash passwords? Why not encrypt them?**
> Hashing is one-way — you cannot reverse it. Encryption is two-way — if someone gets the key, they can decrypt all passwords. With hashing, even if the DB is stolen, passwords cannot be recovered. We verify by hashing the input and comparing to the stored hash.

**Q: Why bcrypt specifically?**
> bcrypt is designed to be slow (cost factor 12 = 4096 rounds). This makes brute force attacks expensive — an attacker would need years to guess passwords even with the hash. Fast hashing algorithms like MD5 or SHA256 are wrong for passwords because they're too fast to brute force.

**Q: What is a JWT and what's in it?**
> JWT = JSON Web Token. It's a signed string with three parts: header, payload, signature. The payload contains `sub` (user id), `role`, and `exp` (expiry time). The server signs it with a secret key — so it can verify it hasn't been tampered with.

**Q: Why two tokens — access token and refresh token?**
> Access token is short-lived (15 min) — if stolen, it expires quickly. Refresh token is long-lived (7 days) — used only to get a new access token. This way you don't ask users to log in every 15 minutes, but stolen access tokens have minimal damage window.

**Q: How does logout work if JWT is stateless?**
> JWTs can't be "cancelled" since the server doesn't store them. So we store the refresh token hash in DB. On logout, we delete it. The access token still works until it expires (15 min) — that's acceptable. If stricter logout is needed, a Redis blacklist would be added.

**Q: What is the SHA256 pre-hash in `hash_password()`?**
> bcrypt has a 72-byte input limit. If a password is longer than 72 bytes, bcrypt silently truncates it — meaning two different long passwords could hash to the same value. We SHA256-hash it first to always get a 64-byte hex string, then bcrypt that.

**Q: Where do you store the refresh token — cookie or body?**
> Response body. httpOnly cookies are more secure (JS can't access them) but harder to implement for mobile apps. Response body works for both web and mobile. The tradeoff is the frontend must store it securely (e.g. secure storage, not localStorage).

---

## Architecture & Patterns

**Q: Explain the 4-file module pattern you used.**
> Each feature has: `router.py` (URL definitions), `controller.py` (thin wrapper, builds response), `service.py` (all business logic), `repository.py` (SQL queries only). This separation means each file has one job — easier to test, debug, and maintain.

**Q: Why separate service and repository?**
> Service has business logic — "if user exists, raise conflict." Repository has SQL — "SELECT * FROM users WHERE email = x." If you mix them, a function doing both is hard to test and reuse. Testing service logic doesn't need a real DB if repository is mocked.

**Q: What is the standard API response shape and why use it?**
> Every response has `success`, `data`, `message`, and optionally `meta` for pagination. Consistent shape means the frontend always knows what to expect — no guessing if error is in `detail`, `error`, or `message`.

**Q: What is `pydantic-settings` and why use it over `os.getenv()`?**
> `pydantic-settings` reads env vars and validates them. `os.getenv("SECRET_KEY")` returns `None` silently if the variable is missing — your app crashes somewhere random. `BaseSettings` crashes immediately at startup with a clear message. Also gives type conversion for free.

**Q: How do you handle errors consistently across the app?**
> Custom exception classes (`NotFoundException`, `UnauthorizedException`, etc.) that inherit from `AppException`. A global `app_exception_handler` in `main.py` catches them all and formats them into the standard response shape. Routes never return error dicts manually.

**Q: What is connection pooling?**
> Instead of opening a new DB connection for every request (expensive), a pool keeps N connections open and reuses them. `pool_size=5, max_overflow=10` means up to 15 concurrent DB connections. Requests wait if all connections are busy.

---

## Scaling & Performance

**Q: Can this app handle 1 million requests per second?**
> No. The main bottleneck is bcrypt — at cost factor 12, one CPU core can verify ~3 passwords/second. For 1M RPS you'd need ~20,000 servers just for bcrypt. For typical startup scale (hundreds of RPS), the current setup is fine.

**Q: What happens if 1000 users try to login simultaneously?**
> FastAPI's asyncio event loop queues them. But bcrypt is CPU-bound, so it blocks the event loop while running. With 1 core doing 3 logins/sec, the 1000th user waits ~333 seconds. The fix is running bcrypt in a thread pool (`run_in_executor`) or adding more workers.

**Q: What is async good for then, if bcrypt blocks it?**
> Async is excellent for I/O-bound work — DB queries, HTTP calls, file reads. While waiting for PostgreSQL to return results, async handles other requests. bcrypt is an exception because it's CPU-bound. Most of the app (DB queries, JWT decode) benefits from async.

**Q: When would you add Redis to this project?**
> When you need to cache frequently read data (e.g. published alerts list) to reduce DB load, or for rate limiting login attempts, or for a refresh token blacklist on logout. Not needed at low traffic.

---

## Supabase & Deployment

**Q: Why Supabase instead of a self-hosted PostgreSQL?**
> Supabase provides managed PostgreSQL with automatic backups, connection pooling via PgBouncer, and a dashboard for viewing data. No ops overhead — perfect for solo developers or small teams.

**Q: What is PgBouncer and what problem did it cause?**
> PgBouncer is a connection pooler that sits in front of PostgreSQL. Supabase uses it on port 6543 in transaction mode. The problem: transaction mode doesn't support prepared statements, which asyncpg uses by default. Fix: use the direct connection (port 5432) or set `statement_cache_size=0`.

**Q: How do you manage environment variables in production on Railway?**
> Set them directly in the Railway dashboard — no `.env` file needed on the server. `pydantic-settings` reads from the environment automatically, so the same code works locally (reads `.env`) and in production (reads Railway env vars).

---

*Updated after: Auth module completion (March 2026)*
