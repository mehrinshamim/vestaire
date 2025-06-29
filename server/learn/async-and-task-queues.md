# Async and Task Queues

## 🎯 What You'll Learn

- Why async/background tasks matter in web apps
- How Django integrates with Celery for task queues
- Real-world examples from this project
- Best practices for async processing

---

## Why Use Async and Task Queues?

Some operations (like image processing, AI analysis, sending emails) take too long to run during a normal web request. If you do them synchronously, users wait and your server can get overloaded.

**With async tasks:**
- Users get instant responses
- Heavy work happens in the background
- Your app stays fast and responsive

---

## Celery: Django’s Task Queue

Celery is the most popular way to run background jobs in Django.

**How it works:**
- You write “tasks” (Python functions) and decorate them with `@shared_task`
- When you call `.delay()`, Celery puts the task in a queue (like Redis)
- Worker processes pick up tasks and run them in the background

---

## Example: AI Analysis as a Background Task

```python
# apps/wardrobe/tasks.py
from celery import shared_task

@shared_task
def analyze_clothing_item(clothing_item_id):
    # 1. Fetch the item from the DB
    # 2. Run AI analysis (can take seconds or minutes)
    # 3. Save results back to the DB
    pass
```

**In your view:**

```python
def upload_view(request):
    # ...save item...
    analyze_clothing_item.delay(item.id)  # Runs in background!
    return Response({'status': 'processing'})
```

---

## How to Set Up Celery (Summary)

1. Install Celery and Redis (`pip install celery redis`)
2. Create a `celery.py` in your Django project (see this repo’s `vestaire/celery.py`)
3. Add Celery config to your settings
4. Start a Redis server
5. Start a Celery worker:  
   `celery -A vestaire worker --loglevel=info`

---

## Real-World Patterns

- **Chaining tasks:** Run tasks in sequence (e.g., process images, then analyze)
- **Retries:** Tasks can auto-retry on failure
- **Scheduled tasks:** Use Celery Beat to run tasks on a schedule (e.g., nightly cleanup)
- **Monitoring:** Use [Flower](https://flower.readthedocs.io/) to see running tasks

---

## Best Practices

- Pass IDs, not objects, to tasks (keeps messages small)
- Make tasks idempotent (safe to run more than once)
- Handle errors and use retries
- Monitor your queues and workers

---

## Further Reading

- [Celery with Django (official docs)](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html)
- [Flower monitoring tool](https://flower.readthedocs.io/)
- [Async in Django (docs)](https://docs.djangoproject.com/en/stable/topics/async/)

---