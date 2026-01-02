#!/bin/bash
# Start script for Render deployment
# Bind to 0.0.0.0 and use PORT environment variable

PORT=${PORT:-8000}
uvicorn app:app --host 0.0.0.0 --port $PORT
