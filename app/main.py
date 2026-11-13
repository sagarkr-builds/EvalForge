from pathlib import Path
import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR.parent / "evalforge.db"

app = FastAPI(title="EvalForge", description="AI Response Evaluation Platform", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                response_a TEXT NOT NULL,
                response_b TEXT NOT NULL,
                score_a INTEGER NOT NULL CHECK(score_a BETWEEN 1 AND 5),
                score_b INTEGER NOT NULL CHECK(score_b BETWEEN 1 AND 5),
                winner TEXT NOT NULL CHECK(winner IN ('A', 'B', 'Tie')),
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)

        new_columns = [
            "accuracy_a INTEGER NOT NULL DEFAULT 3",
            "relevance_a INTEGER NOT NULL DEFAULT 3",
            "clarity_a INTEGER NOT NULL DEFAULT 3",
            "completeness_a INTEGER NOT NULL DEFAULT 3",
            "accuracy_b INTEGER NOT NULL DEFAULT 3",
            "relevance_b INTEGER NOT NULL DEFAULT 3",
            "clarity_b INTEGER NOT NULL DEFAULT 3",
            "completeness_b INTEGER NOT NULL DEFAULT 3"
        ]

        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(evaluations)"
            ).fetchall()
        }

        for column in new_columns:
            column_name = column.split()[0]

            if column_name not in existing_columns:
                connection.execute(
                    f"ALTER TABLE evaluations ADD COLUMN {column}"
                )

        connection.commit()


@app.on_event("startup")
def on_startup():
    initialize_database()


class EvaluationCreate(BaseModel):
    prompt: str
    response_a: str
    response_b: str

    score_a: int
    score_b: int
    winner: str
    notes: str = ""

    accuracy_a: int = 3
    relevance_a: int = 3
    clarity_a: int = 3
    completeness_a: int = 3

    accuracy_b: int = 3
    relevance_b: int = 3
    clarity_b: int = 3
    completeness_b: int = 3

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/health")
def health():
    return {"status": "healthy", "application": "EvalForge"}


@app.get("/api/evaluations")
def list_evaluations():
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM evaluations ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/evaluations", status_code=201)
def create_evaluation(item: EvaluationCreate):
    if item.winner not in ["A", "B", "Tie"]:
        raise HTTPException(
            status_code=422,
            detail="Winner must be A, B, or Tie."
        )

    criteria = [
        item.accuracy_a,
        item.relevance_a,
        item.clarity_a,
        item.completeness_a,
        item.accuracy_b,
        item.relevance_b,
        item.clarity_b,
        item.completeness_b,
    ]

    if any(score < 1 or score > 5 for score in criteria):
        raise HTTPException(
            status_code=422,
            detail="All criterion scores must be between 1 and 5."
        )

    created_at = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO evaluations (
                prompt, response_a, response_b,
                score_a, score_b, winner, notes, created_at,
                accuracy_a, relevance_a, clarity_a, completeness_a,
                accuracy_b, relevance_b, clarity_b, completeness_b
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.prompt.strip(),
                item.response_a.strip(),
                item.response_b.strip(),
                item.score_a,
                item.score_b,
                item.winner,
                item.notes.strip(),
                created_at,
                item.accuracy_a,
                item.relevance_a,
                item.clarity_a,
                item.completeness_a,
                item.accuracy_b,
                item.relevance_b,
                item.clarity_b,
                item.completeness_b,
            )
        )

        connection.commit()
        evaluation_id = cursor.lastrowid

    return {
        "id": evaluation_id,
        "message": "Evaluation saved successfully."
    }


@app.get("/api/stats")
def stats():
    with get_connection() as connection:
        total = connection.execute(
            "SELECT COUNT(*) AS count FROM evaluations"
        ).fetchone()["count"]

        average = connection.execute("""
            SELECT AVG((score_a + score_b) / 2.0) AS average
            FROM evaluations
        """).fetchone()["average"]

        winners = connection.execute("""
            SELECT winner, COUNT(*) AS count
            FROM evaluations
            GROUP BY winner
        """).fetchall()

        criteria = connection.execute("""
            SELECT
                AVG(accuracy_a) AS accuracy_a,
                AVG(relevance_a) AS relevance_a,
                AVG(clarity_a) AS clarity_a,
                AVG(completeness_a) AS completeness_a,
                AVG(accuracy_b) AS accuracy_b,
                AVG(relevance_b) AS relevance_b,
                AVG(clarity_b) AS clarity_b,
                AVG(completeness_b) AS completeness_b
            FROM evaluations
        """).fetchone()

        score_distribution = connection.execute("""
            SELECT score, COUNT(*) AS count
            FROM (
                SELECT score_a AS score FROM evaluations
                UNION ALL
                SELECT score_b AS score FROM evaluations
            )
            GROUP BY score
            ORDER BY score
        """).fetchall()

    return {
        "total_evaluations": total,
        "average_score": round(average, 2) if average is not None else 0,
        "winner_counts": {
            row["winner"]: row["count"] for row in winners
        },
        "criteria_averages": {
            key: round(criteria[key], 2) if criteria[key] is not None else 0
            for key in criteria.keys()
        },
        "score_distribution": [
            dict(row) for row in score_distribution
        ]
    }


@app.delete("/api/evaluations/{evaluation_id}")
def delete_evaluation(evaluation_id: int):
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM evaluations WHERE id = ?", (evaluation_id,))
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    return {"message": "Evaluation deleted."}

# python -m uvicorn app.main:app --reload
