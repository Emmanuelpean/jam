#!/bin/bash

# Absolute paths to frontend and backend
FRONTEND_DIR="$PWD/frontend"
BACKEND_DIR="$PWD/backend"

# Open frontend in new Terminal tab
osascript -e "tell application \"Terminal\" to do script \"cd '$FRONTEND_DIR' && npm start\""

# Small delay to ensure first tab launches properly
sleep 1

# Open backend in a new Terminal tab
osascript -e "tell application \"Terminal\" to do script \"cd '$BACKEND_DIR' && python3 -m uvicorn app.main:app --reload\""
