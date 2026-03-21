import os
import subprocess
import sys

# Get port from environment, default to 8000
port = os.environ.get("PORT", "8000")

print(f"Starting Chartflix API on port {port}")
print(f"Running: uvicorn app.main:app --host 0.0.0.0 --port {port}")

# Start uvicorn
result = subprocess.run(
    ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port],
    cwd="/app"
)

sys.exit(result.returncode)
