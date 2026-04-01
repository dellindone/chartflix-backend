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

**Q: How do you restrict a route to specific roles?**
> Using a `require_role()` factory function that returns a dependency. `Depends(require_role("admin"))` checks the current user's role and raises `ForbiddenException` if they don't have permission.

**Q: What are BackgroundTasks in FastAPI and why did you use them for webhooks?**
> BackgroundTasks let you run a function after the HTTP response is sent. For webhooks, enriching an alert with option chain data takes 3-5 seconds (CSV fetch + Fyers API calls). If the webhook caller waited that long, it would time out and retry. With BackgroundTasks, we respond immediately with 200 and process in the background.

---

## SQLAlchemy & Database

**Q: What is an ORM and why use it?**
> ORM = Object Relational Mapper. It lets you write Python classes instead of raw SQL. It also prevents SQL injection by default since parameters are always escaped.

**Q: What is a migration and why do you need Alembic?**
> A migration is a script that changes the database schema. Alembic tracks these as versioned files — like git for your DB. Without it, you'd manually edit the DB and teammates would be out of sync.

**Q: Why did your migration fail when adding `is_approved`?**
> The column was `nullable=False` but the table had existing rows with no value. PostgreSQL can't add a NOT NULL column without a default for existing rows. Fixed by adding `server_default='false'` to the migration — PostgreSQL fills all existing rows with false before applying the constraint.

**Q: What is `passive_deletes=True` on a relationship?**
> It tells SQLAlchemy not to nullify or delete child records itself — instead let the database's `ondelete="CASCADE"` handle it. Without it, SQLAlchemy tries to SET NULL on the child FK before deletion, which fails if the column is NOT NULL.

---

## Authentication & Authorization

**Q: Why do you hash passwords? Why not encrypt them?**
> Hashing is one-way — cannot be reversed. Encryption is two-way — if someone gets the key, they can decrypt all passwords. With hashing, even if the DB is stolen, passwords cannot be recovered.

**Q: Why two tokens — access token and refresh token?**
> Access token is short-lived (15 min) — if stolen, it expires quickly. Refresh token is long-lived (7 days) — used only to get a new access token. You don't ask users to log in every 15 minutes, but stolen access tokens have minimal damage window.

**Q: How does your user approval system work?**
> New users have `is_approved = false` by default. A `require_approved` dependency checks this before allowing access to alerts. Admin users bypass this check. Admin can approve/reject via `PATCH /admin/users/{id}/approve`. The frontend reads `is_approved` from the profile endpoint to decide whether to show a "waiting for approval" screen.

**Q: Why does admin bypass the `is_approved` check?**
> Admin manages the platform. If admin had `is_approved = false` they'd be locked out of alerts permanently. Admin approval is controlled by the `role = admin` field which is only set via direct DB access — never through the API.

---

## Webhooks

**Q: How do you secure the webhook endpoint if TradingView can't send custom headers?**
> The secret key is passed as a URL query parameter: `/webhook/bullish?secret=abc123`. Both TradingView and ChartInk support this URL format. The server compares the secret against `settings.WEBHOOK_SECRET` and rejects requests that don't match.

**Q: Why must the webhook secret be alphanumeric only?**
> Special characters like `#`, `|`, `)` break URL parsing. `#` is interpreted as a URL fragment — everything after it is ignored by the browser. We generate the secret with `secrets.token_hex(32)` which produces only hex characters (0-9, a-f).

**Q: Why does ChartInk use query param instead of request body for the secret?**
> ChartInk doesn't allow editing the request body — it's a fixed format. The only thing you control is the URL. So the secret goes in the URL query string.

---

## Option Chain & Fyers

**Q: What is an option chain?**
> An option chain is a list of all available option contracts for a stock or index — different strike prices and expiry dates. When we get a signal for "NIFTY BEARISH", we look up the option chain to find the best PUT contract to trade.

**Q: How do you select the best option contract?**
> We use the Strategy pattern. For NSE/BSE indices: try ITM2 (2 strikes in-the-money) first, then ITM1, then ATM — pick the first one with a spread below the threshold (bid-ask spread < 2%). For MCX commodities: pick the first instrument by volume that passes the spread check. If no spread data (market closed or illiquid), fall back to the first ITM candidate.

**Q: Why do you cache the Fyers CSV in Redis?**
> The NSE options CSV is large (~20MB). Fetching it on every alert would be slow and hammer Fyers' servers. We cache it in Redis for 6 hours. Since it changes only when new contracts are listed or expire, 6 hours is a safe TTL.

**Q: Why do you filter the CSV before caching, not after?**
> If we cached the full CSV, it would exceed Upstash's 10MB limit. By filtering to only the rows for a specific symbol (e.g., just NIFTY rows) before caching, each Redis entry is small (a few hundred KB).

**Q: What was the StringDtype pickle error and how did you fix it?**
> The CSV was cached as a pickle (serialized pandas DataFrame) with one version of pandas. When the pandas version changed, the StringDtype constructor signature changed, so unpickling failed. Fixed by catching the exception on `pickle.loads`, deleting the stale cache key, and re-fetching fresh data.

**Q: Why use `dtype=object` when reading the CSV?**
> Pandas 2.1.x tries to use its new StringDtype for string columns, which caused constructor errors. `dtype=object` forces all columns to be read as plain Python strings, bypassing StringDtype entirely. Explicit type conversions (`int()`, `float()`) downstream handle the types we actually need.

---

## Redis Pub/Sub & WebSocket

**Q: Why did WebSocket alerts work on local but not Railway?**
> The `ConnectionManager` is in-memory. Each process has its own list of connected clients. When the local app publishes an alert, it broadcasts to its own clients — Railway's process has no idea. Fixed with Redis Pub/Sub: any process publishes to a shared Redis channel, all processes subscribe and broadcast to their own clients.

**Q: What is the difference between Redis cache and Redis Pub/Sub?**
> Cache (GET/SET) — stores data that can be retrieved later. Good for CSV data, session tokens. Pub/Sub — fire-and-forget messaging. Publisher sends a message, all current subscribers receive it. Messages are not stored — if no one is subscribed, the message is lost.

**Q: Why use `get_message()` polling instead of `async for message in pubsub.listen()`?**
> The async generator `pubsub.listen()` can't be cleanly cancelled. When the server shuts down and the task is cancelled, Python tries to close the generator while it's waiting, causing `RuntimeError: aclose(): asynchronous generator is already running`. The polling approach with `get_message(timeout=1.0)` avoids this — on cancellation, the loop exits cleanly at the next iteration.

**Q: How do you authenticate a WebSocket connection?**
> WebSockets can't send custom headers from the browser, so the JWT is passed as a query parameter: `wss://api.chartflix.in/ws/alerts?token=<jwt>`. On connect, we decode the token, fetch the user from DB, and check `is_approved`. If any check fails, we close the WebSocket with a specific code (4001 = unauthorized, 4003 = not approved).

**Q: Why store the Redis listener task in `app.state`?**
> `asyncio.create_task()` returns a task object. If nothing holds a reference to it, Python's garbage collector can destroy it — cancelling the listener silently. Storing it in `app.state.redis_listener` keeps a reference alive for the entire app lifetime.

**Q: With 2 Uvicorn workers, won't each worker subscribe to Redis separately?**
> Yes — and that's exactly what we want. Each worker has its own connected WebSocket clients. Each worker subscribes to the Redis channel and broadcasts to its own clients. Together, all connected clients across both workers receive every alert.

---

## Architecture & Patterns

**Q: Explain the 4-file module pattern.**
> Each feature has: `router.py` (URL definitions), `controller.py` (thin wrapper, builds response), `service.py` (all business logic), `repository.py` (SQL queries only). Each file has one job — easier to test, debug, and maintain.

**Q: What design patterns did you use in the option chain service?**
> Strategy (NSEBSEStrategy vs MCXStrategy — same interface, different algorithm), Factory (StrategyFactory.get() picks which strategy based on symbol), Singleton (FyersClient — one login session shared app-wide), Cache-Aside (check Redis first, fetch if miss, store result).

**Q: What is the Cache-Aside pattern?**
> Check cache first. If data is there (cache hit), return it — fast. If not (cache miss), fetch from the real source (Fyers CSV), store it in cache for next time, return it. The application manages the cache — it "sets aside" data for future use.

**Q: What is the Singleton pattern and why use it for FyersClient?**
> Singleton ensures only one instance of a class exists. FyersClient logs into Fyers using TOTP + PIN — a slow multi-step process. If every webhook created a new FyersClient, you'd hit Fyers' rate limits immediately. One shared instance logs in once and reuses the session.

**Q: What is the Strategy pattern?**
> Define a family of algorithms (strategies), put each in its own class, make them interchangeable. The caller doesn't know which one runs. In Chartflix: NSE/BSE index options use ITM-first selection; MCX commodities use volume-first selection. The `StrategyFactory` picks the right one — the webhook service just calls `strategy.select(processed)`.

**Q: What is `resolve_category()` and why did you add it?**
> Webhooks receive multiple symbols in one call (e.g. NIFTY, RELIANCE, GOLD). They all get the same category field from the request — but NIFTY should be INDEX, RELIANCE should be STOCK, GOLD should be COMMODITY. `resolve_category(symbol)` auto-detects the correct category per symbol by checking it against known symbol sets.

---

## Performance & Scaling

**Q: Why use 2 Uvicorn workers?**
> One worker = one process = one CPU core. With 2 workers, the app uses 2 cores — doubles throughput for CPU-bound work and provides redundancy (if one worker crashes, the other keeps serving). More than 2 workers would need more RAM — Railway's free tier is limited.

**Q: Why does WebSocket need Redis Pub/Sub with multiple workers?**
> Each worker has its own in-memory `ConnectionManager`. A webhook hitting Worker 1 only knows about Worker 1's connected clients. Redis Pub/Sub is a shared message bus — all workers publish and subscribe to the same channel, so all clients across all workers receive alerts.

**Q: What happens if the Redis connection drops in the listener?**
> The `start_redis_listener()` has a `while True` loop with try/except. If any error occurs (connection drop, timeout), it logs the error, waits 3 seconds, and reconnects. The `asyncio.CancelledError` case is handled separately — it breaks the loop cleanly on app shutdown.

---

## Supabase & Deployment

**Q: How do you manage environment variables on Railway?**
> Set them in the Railway dashboard — no `.env` file on the server. `pydantic-settings` reads from the environment automatically. Same code works locally (reads `.env`) and in production (reads Railway env vars).

**Q: What is CORS and why do you need it?**
> CORS (Cross-Origin Resource Sharing) is a browser security mechanism. Without it, browsers block requests from one domain to another. Our Vercel frontend (`chartflix.in`) calling the Railway API (`api.chartflix.in`) are different domains — CORS middleware adds `Access-Control-Allow-Origin` headers so the browser allows it. Since auth is JWT-based (not cookies), `allow_origins` can be specific domains — restricting who can call the API from browsers.

**Q: Why did WebSocket connections get 403 on Railway?**
> The CORS middleware was checking the `Origin` header on WebSocket upgrade requests. The frontend domain wasn't in the `ALLOWED_ORIGINS` list. Fixed by adding the exact frontend URL to the list in Railway env vars.

---

## Users Module

**Q: What is `exclude_unset=True` in `model_dump()` and why is it important for PATCH endpoints?**
> It returns only the fields the client actually sent. Without it, `PATCH /users/me` with `{"name": "Aditya"}` would also send `phone=None` — wiping the phone field. With `exclude_unset=True`, only `name` is updated.

**Q: Why does `UserProfileResponse` need `is_approved`?**
> The frontend needs to know whether to show the main app or a "waiting for approval" screen. It reads `is_approved` from `GET /users/me` on login. If false, show the waiting screen. If true, proceed normally.

---

## Admin Module

**Q: What happens when an admin promotes a user to analyst?**
> Two things happen: the user's `role` is changed to `analyst`, and a new row is created in the `analysts` table. Both must happen — role alone isn't enough because recommendations require an analyst profile.

**Q: Why can't an admin create another admin through the API?**
> Admin is a privileged role that should only be set via direct DB access. Allowing API-based admin creation means one compromised admin account could escalate privileges. The API blocks `role=admin` updates.

---

*Updated after: Webhook + Option Chain + WebSocket + Redis Pub/Sub + Approval System (April 2026)*
