# pgAdmin Guide - Database Management UI

## Overview

pgAdmin is a web-based PostgreSQL database management tool that provides a user-friendly interface for managing your database.

## Access pgAdmin

**URL**: http://localhost:5050

**Default Credentials** (configured in `.env`):
- **Email**: admin@carparts.com
- **Password**: admin

## First Time Setup

### 1. Start Containers

```bash
docker-compose up -d
```

### 2. Access pgAdmin

Open your browser and go to: **http://localhost:5050**

### 3. Login

Use the credentials from your `.env` file:
- Email: `admin@carparts.com`
- Password: `admin`

### 4. Add PostgreSQL Server

Once logged in, add your PostgreSQL server:

**Step 1**: Right-click on "Servers" → "Register" → "Server"

**Step 2**: In the "General" tab:
- **Name**: CarParts Database (or any name you prefer)

**Step 3**: In the "Connection" tab:
- **Host name/address**: `db` (the container name)
- **Port**: `5432`
- **Maintenance database**: `carparts_db`
- **Username**: `postgres`
- **Password**: `postgres` (or your DB_PASSWORD from .env)

**Step 4**: Click "Save"

## Common Tasks

### View Tables

1. Expand: Servers → CarParts Database → Databases → carparts_db → Schemas → public → Tables
2. Right-click on any table → "View/Edit Data" → "All Rows"

### Run SQL Queries

1. Click on your database (carparts_db)
2. Click the "Query Tool" button (or Tools → Query Tool)
3. Write your SQL and click "Execute" (F5)

**Example queries:**

```sql
-- View all users
SELECT * FROM auth_user;

-- Count parts by supplier
SELECT supplier_id, COUNT(*) as part_count 
FROM marketplace_part 
GROUP BY supplier_id;

-- View orders with client info
SELECT o.id, o.total_price, o.status, u.username 
FROM marketplace_order o 
JOIN auth_user u ON o.client_id = u.id;
```

### Export Data

1. Right-click on a table
2. Select "Import/Export"
3. Toggle "Export" mode
4. Choose format (CSV, JSON, etc.)
5. Click "OK"

### Import Data

1. Right-click on a table
2. Select "Import/Export"
3. Toggle "Import" mode
4. Select your file
5. Configure column mappings
6. Click "OK"

### View Database Size

```sql
SELECT 
    pg_size_pretty(pg_database_size('carparts_db')) as database_size;
```

### View Table Sizes

```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Database Backup & Restore

### Backup via pgAdmin

1. Right-click on "carparts_db" → "Backup"
2. Choose filename and location
3. Select format (Custom, Tar, Plain)
4. Click "Backup"

### Restore via pgAdmin

1. Right-click on "carparts_db" → "Restore"
2. Select your backup file
3. Configure restore options
4. Click "Restore"

### Backup via Docker (Recommended)

```bash
# Backup
docker-compose exec db pg_dump -U postgres carparts_db > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20260401.sql | docker-compose exec -T db psql -U postgres carparts_db
```

## Useful Features

### 1. Dashboard

View real-time statistics:
- Server activity
- Database sessions
- Transaction statistics
- Lock statistics

### 2. ERD Tool

Generate Entity-Relationship Diagrams:
1. Right-click on database → "ERD For Database"
2. Visualize table relationships
3. Export diagram as image

### 3. Maintenance Tasks

Run maintenance operations:
- **VACUUM**: Reclaim storage
- **ANALYZE**: Update statistics
- **REINDEX**: Rebuild indexes

Right-click on table → "Maintenance"

### 4. User Management

Create and manage database users:
1. Expand Login/Group Roles
2. Right-click → "Create" → "Login/Group Role"
3. Configure permissions

## Security Best Practices

### Change Default Credentials

**Update `.env` file:**

```env
PGADMIN_EMAIL=your-email@company.com
PGADMIN_PASSWORD=strong-secure-password
```

Then rebuild:

```bash
docker-compose down
docker-compose up -d
```

### Production Considerations

For production:
1. **Don't expose pgAdmin publicly** (port 5050)
2. Use **strong passwords**
3. Enable **SSL/TLS**
4. Use **SSH tunneling** for remote access
5. Consider removing pgAdmin in production

## Troubleshooting

### Cannot Access pgAdmin

**Check if container is running:**

```bash
docker-compose ps pgadmin
```

**View logs:**

```bash
docker-compose logs pgadmin
```

**Restart container:**

```bash
docker-compose restart pgadmin
```

### Cannot Connect to Database

**Verify database connection:**

```bash
docker-compose exec db psql -U postgres -d carparts_db
```

**Check if db container is running:**

```bash
docker-compose ps db
```

**Important**: Use hostname `db` (container name), NOT `localhost`

### Forgot Password

Reset by recreating the container:

```bash
docker-compose down pgadmin
docker volume rm backend_pgadmin_data
docker-compose up -d pgadmin
```

### Port 5050 Already in Use

Change port in `docker-compose.yml`:

```yaml
ports:
  - "5051:80"  # Use different port
```

Then access at http://localhost:5051

## pgAdmin vs Command Line

| Task | pgAdmin | Command Line |
|------|---------|--------------|
| Visual Interface | ✅ Easy | ❌ Complex |
| Quick Queries | ✅ Great | ⚠️ Okay |
| Backup/Restore | ✅ User-friendly | ⚠️ More control |
| Automation | ❌ Limited | ✅ Scriptable |
| Learning Curve | ✅ Gentle | ⚠️ Steep |

**Recommendation**: Use pgAdmin for development and exploration, command line for automation and scripts.

## Docker Commands Reference

```bash
# Start pgAdmin
docker-compose up -d pgadmin

# Stop pgAdmin
docker-compose stop pgadmin

# View logs
docker-compose logs -f pgadmin

# Access pgAdmin container shell
docker-compose exec pgadmin sh

# Remove pgAdmin data (reset)
docker-compose down
docker volume rm backend_pgadmin_data
docker-compose up -d
```

## Alternative: DBeaver, DataGrip

If you prefer desktop applications:

**DBeaver (Free)**:
- Connection: localhost:5432
- Database: carparts_db
- User: postgres
- Password: postgres

**DataGrip (JetBrains)**:
- Same connection details as above

## Resources

- [pgAdmin Documentation](https://www.pgadmin.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)

---

**You now have full visual access to your PostgreSQL database! 🎉**
