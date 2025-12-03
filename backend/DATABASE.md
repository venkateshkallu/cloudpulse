# CloudPulse Monitor Database Setup

This document describes the database setup and management for CloudPulse Monitor.

## Database Schema

The application uses PostgreSQL with the following tables:

### Tables

1. **logs** - Application and system log entries
   - `id` (Primary Key) - Auto-incrementing log ID
   - `timestamp` - When the log entry was created
   - `level` - Log level (info, warning, error)
   - `message` - Log message content
   - `service_name` - Name of the service that generated the log
   - `created_at` - Record creation timestamp

2. **services** - Monitored services and their status
   - `id` (Primary Key) - Unique service identifier
   - `name` - Human-readable service name
   - `status` - Current status (online, degraded, offline)
   - `uptime` - Service uptime percentage
   - `last_checked` - Last health check timestamp
   - `created_at` - Record creation timestamp
   - `updated_at` - Last update timestamp

3. **metrics** - Historical performance metrics
   - `id` (Primary Key) - Auto-incrementing metric ID
   - `metric_name` - Name of the metric (cpu_usage, memory_usage, etc.)
   - `value` - Metric value
   - `unit` - Unit of measurement (%, MB, etc.)
   - `timestamp` - When the metric was recorded

### Indexes

The schema includes optimized indexes for:
- Time-based queries (logs and metrics by timestamp)
- Service-based filtering (logs by service and level)
- Metric name lookups
- Service status queries

## Environment Configuration

Configure the following environment variables in your `.env` file:

```bash
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=cloudpulse
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password_here
```

## Database Management

Use the `manage_db.py` script for database operations:

### Check Connection
```bash
python manage_db.py check
```

### Initialize Database (tables only)
```bash
python manage_db.py init
```

### Initialize Database with Sample Data
```bash
python manage_db.py init-with-data
```

### Reset Database (WARNING: Deletes all data)
```bash
python manage_db.py reset
```

### Create Tables Only
```bash
python manage_db.py create-tables
```

### Drop All Tables (WARNING: Deletes all data)
```bash
python manage_db.py drop-tables
```

## Migrations

The application uses Alembic for database migrations:

### Generate Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic history
```

## Development Setup

1. Install PostgreSQL locally or use Docker:
   ```bash
   docker run --name cloudpulse-postgres \
     -e POSTGRES_DB=cloudpulse \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=password \
     -p 5432:5432 \
     -d postgres:16
   ```

2. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your database credentials

4. Initialize the database:
   ```bash
   python manage_db.py init-with-data
   ```

5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Production Considerations

- Use connection pooling (already configured in `database.py`)
- Set up proper database backups
- Monitor database performance and query optimization
- Use environment variables for all sensitive configuration
- Consider read replicas for high-traffic scenarios
- Implement proper logging and monitoring for database operations

## Troubleshooting

### Connection Issues
- Verify PostgreSQL is running
- Check firewall settings
- Confirm database credentials
- Test connection with `python manage_db.py check`

### Migration Issues
- Ensure all models are imported in `alembic/env.py`
- Check for conflicting schema changes
- Review migration files before applying

### Performance Issues
- Monitor slow queries in PostgreSQL logs
- Check index usage with `EXPLAIN ANALYZE`
- Consider adding additional indexes for frequent queries
- Monitor connection pool usage