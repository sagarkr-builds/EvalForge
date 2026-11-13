# EvalForge

EvalForge is a local AI response evaluation platform. Compare two responses, score each one, record a preference and reasoning, and review evaluation history.

## MVP features
- Side-by-side response comparison
- 1–5 quality scores for each response
- A/B/Tie preference recording
- Optional evaluator notes
- SQLite persistence
- Dashboard metrics and evaluation history
- Delete saved evaluations
- FastAPI JSON API and interactive API docs

## Run on Windows PowerShell

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs  
Health check: http://127.0.0.1:8000/health

## Structure

```text
evalforge/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── templates/index.html
│   └── static/
│       ├── app.js
│       └── styles.css
├── .gitignore
├── README.md
└── requirements.txt
```

## Limitations
This is an initial local MVP. Scores and preferences are entered by a human. It does not call external AI models or authenticate users. The database is stored locally in `evalforge.db`.
