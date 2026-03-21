#!/bin/sh
# Get PORT from environment, default to 8000
PORT=${PORT:-8000}
echo "Starting Chartflix API on port $PORT..."
exec python main.py
