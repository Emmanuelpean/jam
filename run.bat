start cmd /k "cd frontend && npm start"
start cmd /k ".\.venv\Scripts\activate && cd backend && python -m uvicorn app.main:app --reload"