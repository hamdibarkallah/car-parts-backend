# Docker Deployment Guide

## Container Architecture

Your Car Parts Marketplace uses the following Docker containers:

### 1. **PostgreSQL Database** (`db`)
- **Image**: `postgres:15-alpine`
- **Port**: 5432
- **Purpose**: Production-grade relational database
- **Volume**: `postgres_data` (persistent storage)

### 2. **Django Backend** (`web`)
- **Build**: Custom Dockerfile
- **Port**: 8000
- **Purpose**: REST API server
- **Volumes**: Code, static files, media files

### 3. **pgAdmin** (`pgadmin`)
- **Image**: `dpage/pgadmin4:latest`
- **Port**: 5050
- **Purpose**: Web-based database management UI
- **Volume**: `pgadmin_data`
- **Access**: http://localhost:5050

### 4. **Redis** (`redis`) - Optional
- **Image**: `redis:7-alpine`
- **Port**: 6379
- **Purpose**: Caching and Celery task queue
- **Volume**: `redis_data`

### 5. **Nginx** (Commented out - for production)
- **Image**: `nginx:alpine`
- **Port**: 80
- **Purpose**: Reverse proxy and static file serving

## Quick Start

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### 1. Initial Setup

**Create environment file:**
```bash
cp .env.example .env
```

**Edit `.env` file** with your settings:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=carparts_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=db
```

### 2. Build and Run

**Build containers:**
```bash
docker-compose build
```

**Start all services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

### 3. Database Setup

**Run migrations:**
```bash
docker-compose exec web python manage.py migrate
```

**Create superuser:**
```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Access the Application

- **Django Admin**: http://localhost:8000/admin/
- **API**: http://localhost:8000/api/
- **pgAdmin** (Database UI): http://localhost:5050
- **PostgreSQL**: localhost:5432

**pgAdmin Login** (from `.env`):
- Email: admin@carparts.com
- Password: admin

📖 See **[PGADMIN_GUIDE.md](PGADMIN_GUIDE.md)** for complete pgAdmin setup and usage.

## Common Commands

### Container Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v

# Restart a specific service
docker-compose restart web

# View running containers
docker-compose ps

# View logs
docker-compose logs -f web
docker-compose logs -f db
```

### Django Management

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create migrations
docker-compose exec web python manage.py makemigrations

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Django shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic

# Run tests
docker-compose exec web python manage.py test
```

### Database Management

```bash
# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d carparts_db

# Backup database
docker-compose exec db pg_dump -U postgres carparts_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U postgres carparts_db

# View database logs
docker-compose logs -f db
```

### Development Workflow

```bash
# Rebuild after changing requirements.txt
docker-compose build web
docker-compose up -d

# View real-time logs during development
docker-compose logs -f web

# Execute bash in container
docker-compose exec web bash

# Install new package
docker-compose exec web pip install package-name
# Don't forget to update requirements.txt!
```

## Environment Variables

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SECRET_KEY` | Django secret key | Generated | `django-insecure-...` |
| `DEBUG` | Debug mode | `True` | `False` (production) |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` | `example.com,www.example.com` |
| `DB_ENGINE` | Database engine | `postgresql` | `django.db.backends.postgresql` |
| `DB_NAME` | Database name | `carparts_db` | `carparts_db` |
| `DB_USER` | Database user | `postgres` | `carparts_user` |
| `DB_PASSWORD` | Database password | `postgres` | Strong password |
| `DB_HOST` | Database host | `db` | `db` (container name) |
| `DB_PORT` | Database port | `5432` | `5432` |

## Volumes

Persistent data is stored in Docker volumes:

- **postgres_data**: PostgreSQL database files
- **static_volume**: Django static files (CSS, JS)
- **media_volume**: User uploaded content (images)
- **redis_data**: Redis cache data

### Backup Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect backend_postgres_data

# Backup volume
docker run --rm -v backend_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

## Production Deployment

### 1. Enable Nginx

Uncomment the nginx service in `docker-compose.yml`:

```yaml
nginx:
  image: nginx:alpine
  container_name: carparts_nginx
  restart: unless-stopped
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - static_volume:/app/staticfiles
    - media_volume:/app/media
  depends_on:
    - web
```

### 2. Update Environment Variables

```env
DEBUG=False
SECRET_KEY=generate-a-strong-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 3. Use Production Server

Replace `runserver` in docker-compose.yml:

```yaml
command: gunicorn carparts.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

Install gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### 4. SSL/TLS Configuration

Use Let's Encrypt with Certbot:
```bash
docker-compose run --rm certbot certonly --webroot --webroot-path=/app/staticfiles -d yourdomain.com
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check PostgreSQL logs
docker-compose logs db

# Verify database connection
docker-compose exec db psql -U postgres -c "\l"
```

### Permission Issues

```bash
# Fix media/static file permissions
docker-compose exec web chown -R www-data:www-data /app/media
docker-compose exec web chown -R www-data:www-data /app/staticfiles
```

### Container Won't Start

```bash
# Check container logs
docker-compose logs web

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Stop the process or change port in docker-compose.yml
ports:
  - "8080:8000"
```

## Health Checks

### Database Health

```bash
docker-compose exec db pg_isready -U postgres
```

### Redis Health

```bash
docker-compose exec redis redis-cli ping
```

### Application Health

```bash
curl http://localhost:8000/admin/
```

## Monitoring

### Resource Usage

```bash
# View resource usage
docker stats

# View specific container
docker stats carparts_backend
```

### Logs

```bash
# Follow all logs
docker-compose logs -f

# Follow specific service
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web
```

## Development vs Production

### Development (Current Setup)

- DEBUG=True
- SQLite option available
- Django development server
- Hot reload enabled
- Detailed error pages

### Production (Recommended Changes)

- DEBUG=False
- PostgreSQL required
- Gunicorn/uWSGI server
- Nginx reverse proxy
- Static/Media served by Nginx
- SSL/TLS enabled
- Environment-based secrets
- Automated backups
- Monitoring (Prometheus/Grafana)

## Next Steps

1. **Add Celery** for background tasks (order processing, email notifications)
2. **Add Elasticsearch** for advanced search capabilities
3. **Add Monitoring** (Prometheus + Grafana)
4. **Configure CI/CD** for automated deployments
5. **Add Load Balancing** for horizontal scaling

## Useful Links

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
