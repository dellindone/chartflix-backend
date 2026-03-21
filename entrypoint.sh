#!/bin/sh
# Get PORT from environment, default to 8000
PORT=${PORT:-8000}
echo "Starting Chartflix API on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
