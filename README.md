# EvalForge — AI Response Evaluation Platform

EvalForge is a full-stack web application for comparing and evaluating two AI-generated responses using structured quality criteria.

It helps evaluators assess response quality, calculate scores, identify the better response, and maintain a searchable evaluation history.

**Live Demo:** https://evalforge-u62c.onrender.com  
**GitHub Repository:** https://github.com/sagarkr-builds/EvalForge

## Features

- **Side-by-side comparison:** Compare two responses against the same prompt.
- **Multi-criteria evaluation:** Score accuracy, relevance, clarity, and completeness from 1 to 5.
- **Automatic scoring:** Calculate average scores with decimal precision.
- **Winner determination:** Identify Response A, Response B, or a tie.
- **Evaluation history:** Save, view, refresh, and delete evaluations.
- **Analytics dashboard:** View evaluation statistics and average scores.
- **CSV export:** Export evaluation records for further analysis.
- **REST API:** Manage evaluation data through FastAPI endpoints.
- **Database persistence:** SQLite for local development and Neon PostgreSQL for production.

## Technology Stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite, PostgreSQL (Neon) |
| Database Driver | psycopg 3 |
| Data Validation | Pydantic |
| Testing | pytest, FastAPI TestClient |
| Deployment | Render |
| Version Control | Git, GitHub |
| API Documentation | Swagger UI |

## Application Architecture

- FastAPI handles application routes, validation, and database operations.
- JavaScript manages form submission, score calculations, and dashboard interactions.
- SQLite is used for local development.
- Neon PostgreSQL provides persistent cloud database storage in production.
- Render hosts the deployed application.

## Evaluation Criteria

Each response is scored from 1 to 5 across four dimensions:

| Criterion | Description |
|---|---|
| Accuracy | Factual correctness |
| Relevance | Alignment with the original prompt |
| Clarity | Readability and communication |
| Completeness | Coverage of requested information |

The overall score is the average of the four criteria, rounded to two decimal places.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Application dashboard |
| GET | `/health` | Health check |
| GET | `/api/evaluations` | Retrieve evaluation history |
| POST | `/api/evaluations` | Create an evaluation |
| GET | `/api/stats` | Retrieve dashboard statistics |
| DELETE | `/api/evaluations/{evaluation_id}` | Delete an evaluation |

Interactive API documentation is available at `/docs`.

## Project Structure

```text
EvalForge/
├── app/
│   ├── main.py
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   └── templates/
│       └── index.html
├── screenshots/
├── tests/
│   └── test_main.py
├── .gitignore
├── README.md
├── render.yaml
└── requirements.txt
```

## Local Setup

### Prerequisites
- Python 3.10+
- Git

### Installation

```bash
git clone https://github.com/sagarkr-builds/EvalForge.git
cd EvalForge

py -m venv venv
venv\Scripts\activate

python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open the application at:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

Health check:

`http://127.0.0.1:8000/health`

## Database Configuration

EvalForge automatically uses the database configured through the `DATABASE_URL` environment variable.

- Without `DATABASE_URL`, the application uses local SQLite.
- With `DATABASE_URL`, the application connects to PostgreSQL, such as Neon.

Keep database credentials in environment variables and never commit them to GitHub.

## Testing

Run the automated test suite:

```bash
python -m pytest -v
```

The project has 11 automated tests covering:
- Homepage and health endpoint
- Input validation
- Evaluation creation
- Winner calculation
- Evaluation history
- Dashboard statistics
- Evaluation deletion

The test suite has passed locally.

## Deployment

The application is deployed on Render and uses Neon PostgreSQL for production persistence.

**Live Application:** https://evalforge-u62c.onrender.com

## Current Scope and Limitations

- Evaluations are performed manually by the evaluator.
- The application compares responses but does not directly generate responses using external AI models.
- User authentication and multi-user access are not currently implemented.

## Future Improvements

- AI-assisted evaluation
- Evaluator authentication and user accounts
- Advanced analytics and reporting
- Additional evaluation criteria and configurable scoring

## Author

**Sagar Kumar**

GitHub: https://github.com/sagarkr-builds

EvalForge is an independent project exploring AI response evaluation, backend development, database integration, and full-stack application development.