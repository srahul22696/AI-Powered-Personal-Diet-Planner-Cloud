# Local Simulation & Cloud Deployment

## Part 1 — Run everything locally first

```bash
# 1. Clone/create the project folder, then enter it
cd AI-Personal-Diet-Planner-Cloud

# 2. Create a Python virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env            # then edit .env if needed (defaults work locally)

# 5. Start the backend (Terminal 1)
python backend/app.py           # runs on http://localhost:5000

# 6. Install and start the frontend (Terminal 2)
cd frontend
npm install
npm run dev                     # runs on http://localhost:5173

# 7. Open http://localhost:5173 in your browser
# 8. Register a demo user, complete your profile, generate a plan,
#    save it, upload a sample file, log out, log back in, and verify
#    your data is still there.

# Run the automated test suite:
pytest tests/ -v
```

## Local Development vs Cloud Deployment

| | Local Development | Cloud Deployment |
|---|---|---|
| Database | SQLite file on disk | Managed cloud DB (Firestore / Cloud SQL / RDS) |
| File storage | Local `storage_data/` folder | Firebase Storage / AWS S3 / GCS bucket |
| Backend hosting | Your own machine (`python backend/app.py`) | Cloud Run / App Engine / Render / EC2 |
| Frontend hosting | Vite dev server | Firebase Hosting / Vercel / Netlify / S3+CloudFront |
| Secrets | Local `.env` file (gitignored) | Cloud secret manager / platform env-var settings |
| Access | Only you, on localhost | Anyone, via a public HTTPS URL |

---

## Approach A — Student-friendly / free-tier deployment (recommended first)

**Frontend → Firebase Hosting / Vercel / Netlify (free tier)**
```bash
cd frontend
npm run build
# Firebase Hosting:
npm i -g firebase-tools
firebase login
firebase init hosting     # point "public" directory to frontend/dist
firebase deploy
```

**Backend → Render / Railway / Fly.io (free tier) or Google Cloud Run**
```bash
# Example: Cloud Run (Docker-based, scale-to-zero, generous free tier)
gcloud builds submit --tag gcr.io/PROJECT_ID/diet-planner-backend
gcloud run deploy diet-planner-backend \
  --image gcr.io/PROJECT_ID/diet-planner-backend \
  --region asia-south1 --platform managed --allow-unauthenticated \
  --set-env-vars FLASK_SECRET_KEY=...,JWT_SECRET_KEY=...
```

**Database (upgrade from SQLite) → Firestore or Supabase (both free-tier)**
- Swap `cloud/database_service.py` internals to call Firestore/Supabase SDK
  instead of `sqlite3` — the function signatures (`create_user`,
  `get_user_by_email`, etc.) stay the same, so nothing else in the app
  changes.

**Object storage → Firebase Storage or Supabase Storage (free-tier)**
- Swap `cloud/storage_service.py`'s `save_file` / `read_file` / `delete_file`
  to call the Firebase Storage SDK instead of local disk I/O.

**Environment variables** are set in the hosting platform's dashboard
(Render "Environment", Cloud Run `--set-env-vars`, Firebase Functions config)
— never committed to Git.

---

## Approach B — AWS / Azure / GCP architecture (advanced)

```
Frontend  → S3 (static hosting) + CloudFront (CDN)         [or Firebase Hosting]
Backend   → API Gateway → Lambda (serverless) OR EC2/ECS behind an ALB
Database  → RDS (Postgres) OR DynamoDB
Storage   → S3 bucket (private, per-user prefix, signed URLs for downloads)
Auth      → Amazon Cognito OR self-managed JWT (as built here)
Secrets   → AWS Secrets Manager / Parameter Store
Monitoring→ CloudWatch Logs + Alarms
```

Deployment steps (conceptual):
1. Containerize the backend (`Dockerfile` below) and push to ECR.
2. Deploy via ECS Fargate or Lambda (with API Gateway in front).
3. Point RDS/DynamoDB to the same `database_service.py` interface.
4. Point an S3 bucket to the same `storage_service.py` interface.
5. Configure environment variables via Secrets Manager, injected at runtime.
6. Set up CloudWatch dashboards for logs/metrics.

**Sample Dockerfile for the backend:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV PORT=8080
CMD ["python", "backend/app.py"]
```

## Logs & Monitoring
- Local: Flask's built-in dev logger + the `diet_engine` logger (visible in
  your terminal — check it after triggering an AI-API failure to see the
  fallback message).
- Cloud: Cloud Run/App Engine/CloudWatch automatically capture stdout/stderr
  as searchable logs; set up basic alerts on 5xx error rate for
  "monitoring" in an interview-ready way.

## Suggested CI/CD (GitHub Actions, optional but strong for your portfolio)
```yaml
# .github/workflows/test.yml
name: Run Tests
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
```
