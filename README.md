
# SLA Breach Warning System

## Quickstart

1. Copy `.env.example` to `.env` and adjust if needed.
2. Start the stack:

```
make up
```

This starts Postgres, Redis, the backend (applies migrations and seeds), Celery worker/beat, and the frontend dev server.

- API: http://localhost:8000
- Metrics: http://localhost:8000/api/metrics
- Health: http://localhost:8000/api/health
- Frontend: http://localhost:5173

Default admin login: `admin@demo.dev` / `Admin!234`

## Scripts

- `make migrate` - apply migrations
- `make seed` - reseed demo data
- `make test` - run backend tests
- `make down` - stop and remove containers

## Notes

- All times are UTC. Seed includes events to demonstrate at-risk/breached states.
- Notifications default to local SMTP (MailHog) and Slack webhook if provided.
