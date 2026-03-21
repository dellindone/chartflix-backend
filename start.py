import os
import subprocess
import sys

# Set working directory to /app (where Docker CMD will run from)
os.chdir("/app")

# Get port from environment, default to 8000
port = os.environ.get("PORT", "8000")

print(f"[STARTUP] Working directory: {os.getcwd()}")
print(f"[STARTUP] Starting Chartflix API on port {port}")
print(f"[STARTUP] Running: uvicorn app.main:app --host 0.0.0.0 --port {port}")
print(f"[STARTUP] Environment variables set: {bool(os.environ.get('DATABASE_URL') or os.environ.get('HOST'))}")

try:
    # Start uvicorn
    result = subprocess.run(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port]
    )
    sys.exit(result.returncode)
except Exception as e:
    print(f"[ERROR] Failed to start server: {e}", file=sys.stderr)
    sys.exit(1)
