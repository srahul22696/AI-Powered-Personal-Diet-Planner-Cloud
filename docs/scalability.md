# Scalability

## What happens at different scales

**10 users**
The current architecture (single backend instance + SQLite/local storage)
handles this easily. No changes needed for a demo.

**1,000 users**
- SQLite becomes a bottleneck (file-level locking under concurrent writes)
  → migrate to a managed database (Firestore, Cloud SQL/Postgres).
- Local disk storage doesn't survive a server restart/redeploy or scale
  across multiple instances → migrate to real object storage (Firebase
  Storage / S3).
- A single backend process may start queueing requests under load →
  run 2-3 backend instances behind a load balancer.

**100,000 users**
- Fully managed, horizontally-scalable database (Firestore/DynamoDB or a
  properly sharded/read-replica'd Postgres).
- Object storage with a CDN in front of frequently-downloaded files
  (exported plans, images).
- Stateless backend (already true here, thanks to JWT) deployed as
  serverless functions or containers with **autoscaling** — instances are
  added/removed automatically based on traffic.
- **API Gateway** in front of the backend for rate limiting, request
  validation, and routing.
- **Caching** (Redis/Memcached) for frequently-read, rarely-changed data
  like the food catalog.
- **Queues** (e.g. Cloud Tasks/SQS) for any slow background work — for
  example, if the AI-plan generation were made asynchronous, or for
  sending scheduled weekly-adjustment notifications.

## Concepts demonstrated (interview-ready)

| Concept | How it applies here |
|---|---|
| Autoscaling | Serverless/container platforms add instances as `/generate-plan` traffic spikes, scale to zero when idle |
| Load Balancer | Distributes incoming requests across multiple backend instances so no single instance is overwhelmed |
| Serverless Functions | The backend can be deployed as Cloud Functions/Lambda — no server management, pay only per invocation |
| Managed Databases | Firestore/RDS handle replication, backups, and scaling so the team doesn't manage database servers |
| CDN | Serves the React frontend's static assets from edge locations close to each user, reducing latency |
| Caching | Reduces repeated reads of the static food catalog / frequently accessed profile data |
| Object Storage | S3/Firebase Storage scale to effectively unlimited files without any capacity planning |
| Queues | Decouple slow or bursty work (e.g. batch weekly recalculation) from the user-facing request path |

## Why this project's design already supports scaling
- **Stateless auth (JWT)**: any backend instance can serve any request —
  no "sticky sessions" needed.
- **Service abstraction layers** (`cloud/database_service.py`,
  `cloud/storage_service.py`): swapping SQLite → Firestore or local disk →
  S3 requires changing only these two files, not the routes or frontend.
- **Clear separation of concerns** (routes / AI engine / cloud services):
  each layer can be scaled or replaced independently.
