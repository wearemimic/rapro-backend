# RetirementAdvisorPro Backend

Django REST API backend for RetirementAdvisorPro.

## Development

```bash
python manage.py migrate
python manage.py runserver
```

## Docker Build

```bash
docker build -f docker/Dockerfile.backend -t rapro-backend .
```

## Celery

```bash
celery -A retirementadvisorpro worker --loglevel=info
```
