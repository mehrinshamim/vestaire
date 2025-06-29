# 12-Factor Django Apps

## 🎯 What You'll Learn

- What the 12-Factor App methodology is
- How to apply it to Django projects
- Why it matters for real-world, production-ready apps

---

## What is the 12-Factor App?

The [12-Factor App](https://12factor.net/) is a set of best practices for building modern, scalable, maintainable web applications. It was created by engineers at Heroku and is widely adopted in the industry.

---

## The 12 Factors (and Django Examples)

### 1. **Codebase**
- One codebase tracked in version control, many deploys.
- **Django:** Use git, one repo per project.

### 2. **Dependencies**
- Explicitly declare and isolate dependencies.
- **Django:** Use `requirements/base.txt`, `requirements/development.txt`, etc.

### 3. **Config**
- Store config in the environment, not in code.
- **Django:** Use `python-decouple` or `os.environ` for secrets, DB URLs, etc.

### 4. **Backing Services**
- Treat backing services (DB, cache, email) as attached resources.
- **Django:** Use environment variables for DB, Redis, S3, etc.

### 5. **Build, Release, Run**
- Separate build and run stages.
- **Django:** Use CI/CD pipelines, Docker, etc.

### 6. **Processes**
- Execute the app as one or more stateless processes.
- **Django:** Don’t store state on disk; use DB, cache, or cloud storage.

### 7. **Port Binding**
- Export services via port binding.
- **Django:** Run with `gunicorn` or `uvicorn` on a port.

### 8. **Concurrency**
- Scale out via the process model.
- **Django:** Use multiple Gunicorn workers, Celery workers, etc.

### 9. **Disposability**
- Fast startup and graceful shutdown.
- **Django:** Use proper signal handling, quick boot times.

### 10. **Dev/Prod Parity**
- Keep development, staging, and production as similar as possible.
- **Django:** Use similar settings, Docker, and environment configs.

### 11. **Logs**
- Treat logs as event streams.
- **Django:** Print logs to stdout/stderr, use logging config.

### 12. **Admin Processes**
- Run admin/management tasks as one-off processes.
- **Django:** Use `python manage.py` commands for migrations, shell, etc.

---

## How This Project Follows 12-Factor

- **Settings:** Split into `base.py`, `development.py`, `production.py`
- **Secrets:** Loaded from environment variables
- **Dependencies:** Managed in `requirements/`
- **Celery:** Used for background tasks (process model)
- **Logging:** Configurable, can be sent to stdout
- **Stateless:** No local file storage; uses cloud storage for images

---

## Why 12-Factor Matters

- Easier to deploy and scale
- More secure (no secrets in code)
- Portable across environments (dev, staging, prod)
- Simpler to maintain and debug

---

## Further Reading

- [The Twelve-Factor App](https://12factor.net/)
- [12-Factor Django](https://devcenter.heroku.com/articles/django-app-configuration)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)

---