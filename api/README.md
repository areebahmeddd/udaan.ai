# Udaan.ai College API

## Setup & Execution


# structure 


```bash
app/
 ├── main.py          # Entry point for FastAPI
 ├── routes.py        # API endpoints
 ├── services/        # Service layer for JSON fetch & filter
 │    └── college_api.py
 ├── requirements.txt # Dependencies
 └── ...


# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
.venv\Scripts\activate   # On Windows
# OR
source .venv/bin/activate   # On Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Access API docs in browser
http://127.0.0.1:8000/docs

# 6. Stop the server
Ctrl c


