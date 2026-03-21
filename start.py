import os
import subprocess
import sys

os.chdir("/app")
port = os.environ.get("PORT", "8000")

try:
    subprocess.run(
        ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", port]
    )
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
