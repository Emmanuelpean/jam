#!/bin/bash

# Absolute paths to frontend and backend
FRONTEND_DIR="$PWD/frontend"
BACKEND_DIR="$PWD/backend"

# Open frontend in new Terminal tab
osascript -e "tell application \"Terminal\" to do script \"cd '$FRONTEND_DIR' && npm start\""

# Small delay to ensure first tab launches properly
sleep 1

# Open backend in a new Terminal tab with environment activation
osascript -e "tell application \"Terminal\" to do script \"cd '$BACKEND_DIR' && source /Users/emmanuel/PycharmProjects/jam/.venv/bin/activate && python3 -m uvicorn app.main:app --workers 4 --reload\""
