# Caching in Django

## 🎯 What You'll Learn

In this module, you'll learn how to use caching to dramatically improve your Django application's performance. Caching is like having a super-fast memory that stores frequently accessed data, so you don't have to recalculate or re-fetch it every time.

## 🚀 Why Caching Matters

Imagine your clothing app has 10,000 users, and each user visits their wardrobe page. Without caching:

- **Database queries**: 10,000 × 5 queries = 50,000 database hits
- **AI analysis**: Recalculating the same data repeatedly
- **Response time**: 2-3 seconds per page load
- **Server load**: High CPU and memory usage

With caching:

- **Database queries**: Much fewer (only when data changes)
- **Response time**: 200-500ms per page load
- **Server load**: Significantly reduced
- **User experience**: Much better!

## 🧠 What is Caching?

Caching is storing frequently accessed data in a fast storage location (like memory) so it can be retrieved quickly without expensive operations.

### Types of Caching

1. **View Caching**: Cache entire web pages
2. **Template Caching**: Cache rendered HTML templates
3. **Database Query Caching**: Cache query results
4. **Low-Level Caching**: Cache any Python object
5. **Session Caching**: Cache user session data

## 🔧 Setting Up Caching in Django

### 1. Redis as Cache Backend

In our project, we use **Redis** as the caching backend. Redis is an in-memory data store that's extremely fast.

**Why Redis?**

- **Speed**: In-memory storage (much faster than disk)
- **Persistence**: Can save data to disk
- **Data Types**: Supports strings, lists, sets, hashes
- **Expiration**: Automatic key expiration
- **Scalability**: Can be clustered

**Configuration in `vestaire/settings/base.py`**:

```python
# Redis Configuration
CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = config('REDIS_URL')

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'vestaire',
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}

# Use Redis for sessions too
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 2. Environment Variables

In your `.env` file:

```
REDIS_URL=redis://localhost:6379/0
```

## 🎯 Caching Strategies

### 1. View-Level Caching

Cache entire views or specific parts of views.

#### Using `@cache_page` Decorator

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View

# Cache a function-based view for 5 minutes
@cache_page(60 * 5)  # 5 minutes
def clothing_list_view(request):
    items = ClothingItem.objects.select_related('user').all()
    return render(request, 'wardrobe/list.html', {'items': items})

# Cache a class-based view
@method_decorator(cache_page(60 * 5), name='dispatch')
class ClothingListView(View):
    def get(self, request):
        items = ClothingItem.objects.select_related('user').all()
        return render(request, 'wardrobe/list.html', {'items': items})
```

#### Cache by User

```python
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

def cache_by_user(timeout):
    """Cache decorator that includes user ID in the cache key"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Include user ID in cache key
            cache_key = f"user_{request.user.id}_{request.path}"
            return cache_page(timeout, key_prefix=cache_key)(view_func)(request, *args, **kwargs)
        return wrapper
    return decorator

@cache_by_user(60 * 10)  # 10 minutes per user
def user_wardrobe_view(request):
    items = request.user.clothing_items.all()
    return render(request, 'wardrobe/user_wardrobe.html', {'items': items})
```

### 2. Template Fragment Caching

Cache specific parts of templates.

**In your template**:

```html
{% load cache %}

<!-- Cache this section for 10 minutes -->
{% cache 600 "clothing_categories" %}
<div class="categories">
  {% for category in categories %}
  <div class="category">{{ category.name }}</div>
  {% endfor %}
</div>
{% endcache %}

<!-- Cache with user-specific key -->
{% cache 300 "user_clothing_list" request.user.id %}
<div class="clothing-list">
  {% for item in user_items %}
  <div class="item">{{ item.name }}</div>
  {% endfor %}
</div>
{% endcache %}
```

### 3. Low-Level Caching

Cache any Python object using Django's cache framework.

#### Basic Caching Operations

```python
from django.core.cache import cache

# Set a value
cache.set('my_key', 'my_value', timeout=300)  # 5 minutes

# Get a value
value = cache.get('my_key')
if value is None:
    # Value not in cache, compute it
    value = expensive_calculation()
    cache.set('my_key', value, timeout=300)

# Delete a value
cache.delete('my_key')

# Check if key exists
if cache.get('my_key') is not None:
    print("Key exists in cache")
```

#### Real Example: Caching AI Analysis Results

```python
from django.core.cache import cache
from .models import ClothingItem

def get_ai_analysis(clothing_item_id):
    """Get AI analysis, using cache if available"""
    cache_key = f"ai_analysis_{clothing_item_id}"

    # Try to get from cache first
    analysis = cache.get(cache_key)

    if analysis is None:
        # Not in cache, compute it
        item = ClothingItem.objects.get(id=clothing_item_id)
        analysis = perform_ai_analysis(item)

        # Store in cache for 1 hour
        cache.set(cache_key, analysis, timeout=3600)

    return analysis

def perform_ai_analysis(item):
    """Expensive AI analysis operation"""
    # This is the expensive operation we want to cache
    # In real code, this would call the Gemini API
    return {
        'brand': 'Nike',
        'color': 'Blue',
        'material': 'Cotton',
        'confidence': 0.95
    }
```

#### Cache with Versioning

```python
from django.core.cache import cache

def get_user_clothing_count(user_id):
    """Get user's clothing count with cache versioning"""
    cache_key = f"user_clothing_count_{user_id}"
    version_key = f"user_clothing_count_version_{user_id}"

    # Get current version
    version = cache.get(version_key, 1)

    # Try to get cached data
    cached_data = cache.get(f"{cache_key}_v{version}")

    if cached_data is None:
        # Compute new data
        count = ClothingItem.objects.filter(user_id=user_id).count()
        cached_data = {'count': count, 'timestamp': time.time()}

        # Store with current version
        cache.set(f"{cache_key}_v{version}", cached_data, timeout=3600)

    return cached_data

def invalidate_user_clothing_cache(user_id):
    """Invalidate cache by incrementing version"""
    version_key = f"user_clothing_count_version_{user_id}"
    current_version = cache.get(version_key, 1)
    cache.set(version_key, current_version + 1, timeout=86400)  # 24 hours
```

### 4. Query Caching

Cache database query results.

```python
from django.core.cache import cache
from django.db.models import Q

def get_popular_clothing_items():
    """Get popular clothing items with caching"""
    cache_key = "popular_clothing_items"

    items = cache.get(cache_key)
    if items is None:
        # Expensive query
        items = list(ClothingItem.objects.filter(
            wear_count__gte=5
        ).select_related('user', 'category').order_by('-wear_count')[:20])

        # Cache for 30 minutes
        cache.set(cache_key, items, timeout=1800)

    return items

def get_user_recommendations(user_id):
    """Get personalized recommendations for user"""
    cache_key = f"user_recommendations_{user_id}"

    recommendations = cache.get(cache_key)
    if recommendations is None:
        # Complex recommendation algorithm
        user_items = ClothingItem.objects.filter(user_id=user_id)
        recommendations = calculate_recommendations(user_items)

        # Cache for 1 hour
        cache.set(cache_key, recommendations, timeout=3600)

    return recommendations
```

## 🎯 Real-World Examples from Our Project

### Example 1: Caching User Profile Data

```python
from django.core.cache import cache
from apps.authentication.models import UserProfile

def get_user_profile(user_id):
    """Get user profile with caching"""
    cache_key = f"user_profile_{user_id}"

    profile_data = cache.get(cache_key)
    if profile_data is None:
        profile, created = UserProfile.objects.get_or_create(user_id=user_id)
        profile_data = {
            'id': profile.id,
            'user_id': user_id,
            'bio': profile.bio,
            'preferences': profile.preferences,
            'last_updated': profile.updated_at.isoformat()
        }

        # Cache for 15 minutes
        cache.set(cache_key, profile_data, timeout=900)

    return profile_data

def update_user_profile(user_id, data):
    """Update user profile and invalidate cache"""
    profile = UserProfile.objects.get(user_id=user_id)

    # Update profile
    for field, value in data.items():
        setattr(profile, field, value)
    profile.save()

    # Invalidate cache
    cache.delete(f"user_profile_{user_id}")
```

### Example 2: Caching AI Analysis Results

```python
from django.core.cache import cache
from apps.wardrobe.models import AIAnalysis

def get_cached_ai_analysis(clothing_item_id):
    """Get AI analysis with intelligent caching"""
    cache_key = f"ai_analysis_{clothing_item_id}"

    analysis = cache.get(cache_key)
    if analysis is None:
        try:
            # Get from database
            ai_analysis = AIAnalysis.objects.get(clothing_item_id=clothing_item_id)
            analysis = {
                'extracted_data': ai_analysis.extracted_data,
                'confidence_scores': ai_analysis.confidence_scores,
                'processing_time': ai_analysis.processing_time.total_seconds(),
                'created_at': ai_analysis.created_at.isoformat()
            }

            # Cache for 2 hours (AI analysis doesn't change often)
            cache.set(cache_key, analysis, timeout=7200)

        except AIAnalysis.DoesNotExist:
            analysis = None

    return analysis
```

### Example 3: Caching Category Data

```python
from django.core.cache import cache
from apps.wardrobe.models import ClothingCategory

def get_clothing_categories():
    """Get all clothing categories with caching"""
    cache_key = "clothing_categories"

    categories = cache.get(cache_key)
    if categories is None:
        categories = list(ClothingCategory.objects.all().values(
            'id', 'name', 'slug', 'parent_id'
        ))

        # Cache for 1 hour (categories don't change often)
        cache.set(cache_key, categories, timeout=3600)

    return categories

def get_category_hierarchy():
    """Get category hierarchy with caching"""
    cache_key = "category_hierarchy"

    hierarchy = cache.get(cache_key)
    if hierarchy is None:
        # Build hierarchy
        categories = ClothingCategory.objects.all()
        hierarchy = build_category_tree(categories)

        # Cache for 2 hours
        cache.set(cache_key, hierarchy, timeout=7200)

    return hierarchy
```

## 🚨 Cache Invalidation Strategies

### 1. Time-Based Expiration

```python
# Cache expires after 1 hour
cache.set('key', 'value', timeout=3600)
```

### 2. Manual Invalidation

```python
# Delete specific cache key
cache.delete('user_profile_123')

# Delete multiple related keys
cache.delete_pattern('user_profile_*')
```

### 3. Version-Based Invalidation

```python
def invalidate_user_data(user_id):
    """Invalidate all user-related cache"""
    version_key = f"user_data_version_{user_id}"
    current_version = cache.get(version_key, 1)
    cache.set(version_key, current_version + 1)
```

### 4. Signal-Based Invalidation

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

@receiver(post_save, sender=ClothingItem)
def invalidate_clothing_cache(sender, instance, **kwargs):
    """Invalidate cache when clothing item is saved"""
    # Invalidate user's clothing list cache
    cache.delete(f"user_clothing_list_{instance.user_id}")

    # Invalidate item-specific cache
    cache.delete(f"clothing_item_{instance.id}")
```

## 📊 Cache Performance Monitoring

### Using Django Debug Toolbar

Add to your settings:

```python
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

### Custom Cache Monitoring

```python
from django.core.cache import cache
import time

def cache_monitor(func):
    """Decorator to monitor cache performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@cache_monitor
def expensive_operation():
    # Your expensive operation here
    pass
```

## 🎯 Best Practices

### 1. Choose Appropriate Timeouts

- **Frequently changing data**: 5-15 minutes
- **Moderately changing data**: 1-2 hours
- **Rarely changing data**: 24 hours or more

### 2. Use Meaningful Cache Keys

```python
# ✅ GOOD: Descriptive keys
cache_key = f"user_profile_{user_id}_{profile_version}"

# ❌ BAD: Unclear keys
cache_key = f"data_{user_id}"
```

### 3. Handle Cache Misses Gracefully

```python
def get_data_with_fallback(key, fallback_func, timeout=300):
    """Get data from cache with fallback"""
    data = cache.get(key)
    if data is None:
        data = fallback_func()
        cache.set(key, data, timeout=timeout)
    return data
```

### 4. Monitor Cache Hit Rates

```python
def cache_hit_rate():
    """Calculate cache hit rate"""
    hits = cache.get('cache_hits', 0)
    misses = cache.get('cache_misses', 0)
    total = hits + misses

    if total > 0:
        return hits / total
    return 0
```

## 📝 Practice Exercise

1. Look at the `apps/wardrobe/views.py` file
2. Identify which views could benefit from caching
3. Implement caching for one of the views
4. Test the performance improvement

## 🔗 Next Steps

Now that you understand caching, learn about:

- [Async and Task Queues](./async-and-task-queues.md) - Handling background tasks
- [12-Factor Django Apps](./12-factor-django.md) - Production-ready practices

## 📚 Additional Resources

- [Django Caching Documentation](https://docs.djangoproject.com/en/stable/topics/cache/)
- [Redis Documentation](https://redis.io/documentation)
- [Django Redis Documentation](https://django-redis.readthedocs.io/)

---

**Ready to handle background tasks?** Learn about async processing in [Async and Task Queues](./async-and-task-queues.md).
