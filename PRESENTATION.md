---
pdf_options:
  format: A4
  margin: 30mm 25mm
  printBackground: true
css: |
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Inter', sans-serif;
    color: #1a1a2e;
    background: #ffffff;
    font-size: 13px;
    line-height: 1.6;
  }

  h1 {
    font-size: 32px;
    font-weight: 800;
    color: #0f3460;
    margin-bottom: 6px;
  }

  h2 {
    font-size: 18px;
    font-weight: 700;
    color: #0f3460;
    margin: 32px 0 12px 0;
    padding-bottom: 6px;
    border-bottom: 2px solid #e94560;
  }

  h3 {
    font-size: 14px;
    font-weight: 600;
    color: #16213e;
    margin: 16px 0 8px 0;
  }

  p {
    margin-bottom: 10px;
    color: #444;
  }

  .hero {
    background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    color: white;
    padding: 40px 36px;
    border-radius: 12px;
    margin-bottom: 32px;
  }

  .hero h1 { color: white; font-size: 36px; margin-bottom: 8px; }
  .hero p { color: #a8c0d6; font-size: 15px; margin: 0; }
  .hero .tagline { color: #e94560; font-weight: 600; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; }

  .badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 20px;
  }

  .badge {
    background: rgba(255,255,255,0.12);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid rgba(255,255,255,0.2);
  }

  .card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;
    margin: 16px 0;
  }

  .card {
    background: #f8f9ff;
    border: 1px solid #e0e4f0;
    border-radius: 10px;
    padding: 18px;
  }

  .card .icon { font-size: 24px; margin-bottom: 8px; }
  .card h3 { margin: 0 0 6px 0; font-size: 14px; color: #0f3460; }
  .card p { margin: 0; font-size: 12px; color: #666; line-height: 1.5; }

  .flow-box {
    background: #f0f4ff;
    border-left: 4px solid #e94560;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    margin: 12px 0;
    font-size: 12.5px;
  }

  .flow-step {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin: 10px 0;
  }

  .step-num {
    background: #0f3460;
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    flex-shrink: 0;
  }

  .step-text { font-size: 13px; color: #333; padding-top: 2px; }
  .step-text strong { color: #0f3460; }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    font-size: 12.5px;
  }

  th {
    background: #0f3460;
    color: white;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    font-size: 12px;
  }

  td {
    padding: 9px 14px;
    border-bottom: 1px solid #eef0f8;
    color: #444;
  }

  tr:nth-child(even) td { background: #f8f9ff; }
  tr:last-child td { border-bottom: none; }

  .highlight { color: #e94560; font-weight: 700; }
  .tag { background: #e8f0fe; color: #0f3460; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
  .tag-red { background: #fdecea; color: #c0392b; }
  .tag-green { background: #e8f5e9; color: #1b5e20; }

  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 12px 0;
  }

  .section-intro {
    color: #555;
    font-size: 13px;
    margin-bottom: 16px;
  }

  .divider {
    border: none;
    border-top: 1px solid #eef0f8;
    margin: 28px 0;
  }

  .footer {
    margin-top: 40px;
    text-align: center;
    color: #999;
    font-size: 11px;
    border-top: 1px solid #eee;
    padding-top: 16px;
  }

  code {
    background: #f0f4ff;
    color: #0f3460;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 11.5px;
    font-family: monospace;
  }

  ul { padding-left: 18px; margin: 8px 0; }
  li { margin: 4px 0; color: #444; font-size: 12.5px; }
---

<div class="hero">
  <div class="tagline">Platform Overview</div>
  <h1>Chartflix</h1>
  <p>An intelligent trading alert platform that receives signals from TradingView & ChartInk, enriches them with live option chain data, and delivers real-time alerts to subscribers — all automated, end to end.</p>
  <div class="badge-row">
    <span class="badge">FastAPI</span>
    <span class="badge">PostgreSQL</span>
    <span class="badge">Redis Pub/Sub</span>
    <span class="badge">Fyers API</span>
    <span class="badge">WebSocket</span>
    <span class="badge">Railway · Supabase · Upstash</span>
  </div>
</div>

## The Problem We Solve

<p class="section-intro">Retail traders get raw signals from screeners — a stock name and a price. They still have to manually find the right option contract, check strike prices, calculate lot sizes, and estimate investment. This takes time and introduces errors at the most critical moment.</p>

<div class="card-grid">
  <div class="card">
    <div class="icon">⚡</div>
    <h3>Instant Enrichment</h3>
    <p>Raw signals are automatically enriched with the best option contract, strike price, lot size, and investment amount.</p>
  </div>
  <div class="card">
    <div class="icon">📡</div>
    <h3>Real-Time Delivery</h3>
    <p>Alerts are pushed to users the moment they're processed — no page refresh, no delay.</p>
  </div>
  <div class="card">
    <div class="icon">🔐</div>
    <h3>Controlled Access</h3>
    <p>Admin approves each user before they can see alerts. Full role-based access control.</p>
  </div>
</div>

## How It Works — End to End

<div class="flow-box">
  <div class="flow-step">
    <div class="step-num">1</div>
    <div class="step-text"><strong>Signal arrives</strong> — TradingView or ChartInk fires a webhook to Chartflix with the stock symbol and trigger price.</div>
  </div>
  <div class="flow-step">
    <div class="step-num">2</div>
    <div class="step-text"><strong>Option chain lookup</strong> — Chartflix fetches live Fyers option chain data (cached in Redis for 6 hours), finds the next expiry, and builds a strike chain around the current price.</div>
  </div>
  <div class="flow-step">
    <div class="step-num">3</div>
    <div class="step-text"><strong>Smart contract selection</strong> — An intelligent strategy picks the best contract based on exchange type (NSE/BSE uses ITM-first selection; MCX uses volume + spread). Falls back gracefully when market is closed.</div>
  </div>
  <div class="flow-step">
    <div class="step-num">4</div>
    <div class="step-text"><strong>Alert saved</strong> — The enriched alert (symbol, contract, strike, lot size, investment) is saved to the database under the system analyst account.</div>
  </div>
  <div class="flow-step">
    <div class="step-num">5</div>
    <div class="step-text"><strong>Live broadcast</strong> — The alert is published to a Redis channel. All server instances subscribed to that channel instantly push it to connected users via WebSocket.</div>
  </div>
</div>

## User Roles

<table>
  <tr>
    <th>Role</th>
    <th>How Assigned</th>
    <th>What They Can Do</th>
  </tr>
  <tr>
    <td><span class="tag">User</span></td>
    <td>Default on sign up</td>
    <td>View live alerts and recommendations after admin approval</td>
  </tr>
  <tr>
    <td><span class="tag">Analyst</span></td>
    <td>Admin promotes</td>
    <td>Create, edit, and publish their own alerts & stock recommendations</td>
  </tr>
  <tr>
    <td><span class="tag tag-red">Admin</span></td>
    <td>Set in database</td>
    <td>Full control — approve users, manage roles, delete content</td>
  </tr>
</table>

## User Access Flow

<div class="two-col">
  <div>
    <h3>New User Journey</h3>
    <div class="flow-box">
      <div class="flow-step">
        <div class="step-num">1</div>
        <div class="step-text">User registers → <code>is_approved = false</code></div>
      </div>
      <div class="flow-step">
        <div class="step-num">2</div>
        <div class="step-text">Tries to view alerts → gets <strong>Access Pending</strong> screen</div>
      </div>
      <div class="flow-step">
        <div class="step-num">3</div>
        <div class="step-text">Admin reviews and approves from dashboard</div>
      </div>
      <div class="flow-step">
        <div class="step-num">4</div>
        <div class="step-text">User now sees live alerts in real-time</div>
      </div>
    </div>
  </div>
  <div>
    <h3>Why Approval Matters</h3>
    <p style="margin-top:8px">This gives the platform complete control over who sees the alerts. Useful for:</p>
    <ul>
      <li>Subscription-based access</li>
      <li>Vetting users before giving access</li>
      <li>Revoking access at any time</li>
      <li>Future payment gate integration</li>
    </ul>
  </div>
</div>

<hr class="divider">

## Option Chain Intelligence

<p class="section-intro">The platform auto-detects the category of every incoming symbol and applies the right selection strategy — no manual input required from the signal source.</p>

<div class="two-col">
  <div>
    <h3>Auto Category Detection</h3>
    <table>
      <tr><th>Symbol</th><th>Detected As</th></tr>
      <tr><td>NIFTY, BANKNIFTY, SENSEX</td><td><span class="tag">INDEX</span></td></tr>
      <tr><td>RELIANCE, TCS, INFY</td><td><span class="tag">STOCK</span></td></tr>
      <tr><td>GOLD, SILVER, CRUDEOIL</td><td><span class="tag">COMMODITY</span></td></tr>
    </table>
  </div>
  <div>
    <h3>Contract Selection Strategy</h3>
    <table>
      <tr><th>Exchange</th><th>Logic</th></tr>
      <tr><td>NSE / BSE</td><td>ITM2 → ITM1 → ATM, tightest spread wins</td></tr>
      <tr><td>MCX</td><td>Best spread below 2% threshold</td></tr>
      <tr><td>Market closed</td><td>Falls back to ITM order, skips spread</td></tr>
    </table>
  </div>
</div>

## API Surface

<table>
  <tr>
    <th>Area</th>
    <th>Endpoint</th>
    <th>Access</th>
  </tr>
  <tr><td>Auth</td><td><code>POST /auth/register</code> · <code>POST /auth/login</code> · <code>POST /auth/refresh</code></td><td>Public</td></tr>
  <tr><td>Alerts</td><td><code>GET /alerts</code> · <code>GET /alerts/{id}</code></td><td>Approved users</td></tr>
  <tr><td>Publish</td><td><code>PATCH /alerts/{id}/publish</code></td><td>Analyst / Admin</td></tr>
  <tr><td>Admin</td><td><code>GET /admin/users</code> · <code>PATCH /admin/users/{id}/approve</code></td><td>Admin only</td></tr>
  <tr><td>Webhook</td><td><code>POST /webhook/bullish</code> · <code>POST /webhook/bearish</code></td><td>Secret key</td></tr>
  <tr><td>Live Feed</td><td><code>WS /ws/alerts?token=</code></td><td>Approved users</td></tr>
</table>

## Infrastructure

<div class="card-grid">
  <div class="card">
    <div class="icon">🚂</div>
    <h3>Railway</h3>
    <p>Hosts the FastAPI backend with 2 workers. Auto-deploys on push. Handles PORT binding automatically.</p>
  </div>
  <div class="card">
    <div class="icon">🐘</div>
    <h3>Supabase</h3>
    <p>Managed PostgreSQL in Hyderabad region. Stores users, alerts, recommendations, and sessions.</p>
  </div>
  <div class="card">
    <div class="icon">⚡</div>
    <h3>Upstash Redis</h3>
    <p>US West region (matches Railway). Powers CSV caching (6h TTL) and cross-worker Pub/Sub.</p>
  </div>
</div>

## Security

<div class="two-col">
  <div>
    <table>
      <tr><th>Layer</th><th>Implementation</th></tr>
      <tr><td>Passwords</td><td>bcrypt, cost factor 12</td></tr>
      <tr><td>API auth</td><td>JWT HS256 — 15 min access + 7 day refresh</td></tr>
      <tr><td>Webhooks</td><td>Secret key in URL, alphanumeric only</td></tr>
      <tr><td>CORS</td><td>Whitelist — chartflix.in + localhost only</td></tr>
    </table>
  </div>
  <div>
    <table>
      <tr><th>Layer</th><th>Implementation</th></tr>
      <tr><td>User gate</td><td><code>is_approved</code> flag per user</td></tr>
      <tr><td>Role guard</td><td><code>require_role()</code> on every route</td></tr>
      <tr><td>WebSocket</td><td>JWT on connect + approval check</td></tr>
      <tr><td>Fyers token</td><td>Auto re-login after 20 hours</td></tr>
    </table>
  </div>
</div>

<div class="footer">
  Chartflix Backend v2.0 &nbsp;·&nbsp; FastAPI + PostgreSQL + Redis + Fyers API &nbsp;·&nbsp; Deployed on Railway
</div>
