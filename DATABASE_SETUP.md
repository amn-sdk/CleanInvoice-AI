# CleanInvoice Database Setup

## Prerequisites

1. **Docker** must be running on your machine
2. **PostgreSQL** via Docker Compose

## Setup Instructions

### 1. Start PostgreSQL Database

```bash
cd infra/docker
docker-compose up -d
```

This will start PostgreSQL on `localhost:5432` with:
- User: `postgres`
- Password: `postgrespassword`
- Database: `cleaninvoice`

### 2. Run Migrations

```bash
cd apps/core-api
./venv/bin/alembic upgrade head
```

This will create all the tables in the database.

### 3. Verify

Connect to PostgreSQL to verify:

```bash
psql postgresql://postgres:postgrespassword@localhost:5432/cleaninvoice
```

Then run:
```sql
\dt
```

You should see all the tables: companies, users, customers, suppliers, invoices, etc.

## Troubleshooting

If Docker is not running, you'll see:
```
Cannot connect to the Docker daemon
```

Solution: Start Docker Desktop or Docker service.

If you have a local PostgreSQL instance conflicting with port 5432, either:
- Stop the local instance
- Change the port in `docker-compose.yml` (e.g., `"5433:5432"`)
