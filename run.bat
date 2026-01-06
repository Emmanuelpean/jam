start cmd /k "cd frontend && npm start"
start cmd /k ".\.venv\Scripts\activate && cd backend && uvicorn app.main:app --reload --port 8000"
start cmd /k ".\.venv\Scripts\activate && cd backend && SET SCHEDULER=true && uvicorn app.main:app --reload --port 8001"