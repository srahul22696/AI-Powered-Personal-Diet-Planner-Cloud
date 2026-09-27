# AI-Powered Personal Diet Planner with Cloud Storage

A cloud-architected, full-stack diet-planning application built as an
industry-oriented Cloud Computing course project. Users register, complete
a demo profile, generate a personalized meal plan (AI API with automatic
rule-based fallback), save plans, and upload files — all backed by
swappable cloud database and cloud object storage service layers.

> **Disclaimer:** This project uses only synthetic/demo user data.
> Generated diet plans are educational/general-wellness examples and are
> **not** medical or clinical nutrition advice.

---

## Overview
Built to demonstrate core cloud-computing concepts (authentication, cloud
database, cloud object storage, REST APIs, AI integration with fallback,
scalability, and security) through a genuinely working, testable
application — not just a slide deck.

## Problem Statement
People struggle to plan meals, track macros/calories, and stay consistent
without personalized guidance that's accessible from any device.

## Objectives
- Demonstrate a full cloud application stack: auth, database, storage, API, AI.
- Keep the project runnable end-to-end without any paid service.
- Make the codebase modular enough that swapping SQLite → Firestore or
  local disk → Firebase Storage requires touching only two files.

## Features
- Register / Login / Logout (JWT-based, stateless auth)
- Demo profile: age, height, weight, activity level, dietary preference, goal
- AI-powered diet plan generation (breakfast, lunch, snack, dinner +
  nutrition summary + hydration reminder), with automatic fallback to a
  rule-based engine if no AI API is configured
- Save, view, and delete generated plans
- Upload, list, download, and delete personal files (cloud object storage)
- Export a saved plan as a downloadable text file
- Dashboard summarizing goal, preference, latest plan, saved plans, and files
- Strict per-user data isolation (verified by automated tests)

## Cloud Computing Concepts Demonstrated
See [`docs/architecture.md`](docs/architecture.md) for a full concept-by-concept
mapping (Cloud Computing, SaaS/PaaS/IaaS, Cloud Storage vs Cloud Database,
REST API, Serverless, Scalability, Elasticity, Load Balancing, API Gateway,
Environment Variables, Secrets Management, Logging, Monitoring, CI/CD).

## Architecture
```
User → Frontend (React) → Auth (JWT) → REST API (Flask)
                                              ↓
                          ┌────────────────┬────────────────┐
                          ↓                ↓                ↓
                      AI Engine        Cloud DB        Cloud Storage
                          └────────────────┼────────────────┘
                                           ↓
                                      Diet Plan → Dashboard
```
Full data-flow diagram and layer breakdown: [`docs/architecture.md`](docs/architecture.md).

## Technology Stack
- **Frontend:** React + Vite
- **Backend:** Python Flask, REST API, Flask-JWT-Extended
- **Database:** SQLite locally (swappable to Firestore/Cloud SQL) — `cloud/database_service.py`
- **Cloud Storage:** Local disk locally (swappable to Firebase Storage/S3) — `cloud/storage_service.py`
- **AI Engine:** Rule-based recommender with optional external AI API + automatic fallback — `ai_engine/`
- **Testing:** pytest (18 automated tests)

## AI Recommendation Engine
`ai_engine/diet_engine.py` computes BMR (Mifflin-St Jeor) and TDEE from the
user's profile, then either calls a configured external AI API or — if
that's unavailable/unconfigured/fails — generates a plan from a local food
dataset filtered by dietary preference and allergies. See
[`docs/architecture.md`](docs/architecture.md) and
[`docs/interview_prep.md`](docs/interview_prep.md) for details on the
fallback logic.

## Authentication
JWT-based register/login/logout. Passwords are hashed with salted PBKDF2.
Every protected endpoint requires a valid token, and every query is scoped
to the token's user id — see [`docs/security.md`](docs/security.md).

## Database
See [`docs/architecture.md`](docs/architecture.md) for the full schema:
`USERS`, `DIET_PLANS`, `USER_FILES`, with primary/foreign keys and
per-user access rules.

## Cloud Storage
Files are namespaced per user (`storage_data/users/{uid}/files/...`
locally; `users/{uid}/files/...` in a real bucket). See
[`docs/architecture.md`](docs/architecture.md) for the Cloud DB vs Cloud
Storage distinction.

## REST APIs
| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Create a new account |
| POST | `/login` | Authenticate, receive a JWT |
| POST | `/logout` | Client-side token discard |
| GET | `/profile` | Get the current user's profile |
| PUT | `/profile` | Update profile fields |
| POST | `/generate-plan` | Generate a new diet plan |
| GET | `/plans` | List the current user's saved plans |
| GET | `/plans/{id}` | Get one plan |
| DELETE | `/plans/{id}` | Delete a plan |
| GET | `/plans/{id}/export` | Download a plan as a text file |
| POST | `/upload` | Upload a file |
| GET | `/files` | List the current user's files |
| GET | `/files/{id}/download` | Download a file |
| DELETE | `/files/{id}` | Delete a file |

## Folder Structure
```
AI-Personal-Diet-Planner-Cloud/
├── frontend/            React app (pages, components, API service)
├── backend/              Flask app, routes, config, security utils
├── ai_engine/           Rule-based + AI-API diet recommendation logic
├── cloud/               Database & storage service abstractions
├── tests/               Automated pytest test suite
├── docs/                Architecture, deployment, security, scalability, interview prep
├── sample_data/         Synthetic demo users
├── screenshots/         Place your captured screenshots here
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation & Local Setup
Full step-by-step commands: [`docs/deployment.md`](docs/deployment.md).

Quick start:
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python backend/app.py            # backend on :5000

cd frontend && npm install && npm run dev   # frontend on :5173
```

## Environment Variables
See [`.env.example`](.env.example) — never commit a real `.env` file.

## Running Tests
```bash
pytest tests/ -v
```
See [`docs/testing.md`](docs/testing.md) for the full test-case table.

## Cloud Deployment
Two approaches (free-tier and AWS/Azure/GCP) with exact commands:
[`docs/deployment.md`](docs/deployment.md).

## Security
[`docs/security.md`](docs/security.md)

## Scalability
[`docs/scalability.md`](docs/scalability.md)

## Screenshots
See [`docs/github_strategy.md`](docs/github_strategy.md) for the full
checklist and filenames; store captured images in `screenshots/`.

## Results
A fully working local demo: registration → profile → plan generation
(with verified AI-fallback behavior) → saving/retrieving plans → file
upload/download → dashboard summary, all covered by 18 passing automated
tests.

## Limitations
- Local demo uses SQLite and local disk rather than a live managed cloud
  database/storage (by design, so the project runs without a paid account —
  the service-layer abstractions make upgrading straightforward).
- The rule-based engine is intentionally simple (educational scope).
- Not a medical or clinical nutrition tool.

## Future Improvements
Meal substitutions, shopping-list generation, cost-per-day estimates,
scheduled weekly macro adjustments, push notifications, CI/CD pipeline,
infrastructure as code, richer analytics.

## Learning Outcomes
Cloud service-layer design, REST API architecture, JWT authentication,
fallback/error-handling patterns, automated testing discipline, and
cloud deployment planning across free-tier and enterprise-cloud options.

## Disclaimer
Synthetic/demo data only. Generated diet plans are general
educational/wellness examples, not medical or clinical nutrition advice.

## Author
Rahul — Computer Engineering student, built as a Cloud Computing course project.
