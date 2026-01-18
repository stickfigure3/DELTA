#!/bin/bash
# DELTA Platform startup script
# Handles PORT environment variable for Railway and local Docker

PORT="${PORT:-8000}"
echo "Starting DELTA Platform on port $PORT"
exec uvicorn delta.api.main:app --host 0.0.0.0 --port "$PORT"
