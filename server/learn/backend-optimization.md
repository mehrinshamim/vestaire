# Backend Optimization Techniques

## 🎯 What You'll Learn

In this module, you'll discover how to make your Django application fast and efficient. We'll focus on database query optimization, which is often the biggest performance bottleneck in web applications.

## 🐌 Why Optimization Matters

Imagine you're building a clothing management app (like this project). As your user base grows, you might have:

- 10,000 users
- 100,000 clothing items
- 500,000 images

Without optimization, your app could become painfully slow. Users might wait 10+ seconds for a page to load, and your server costs could skyrocket.

## 🔍 Understanding Database Queries

### What Happens When You Make a Query?

When you write code like this:

```python
# In a view
clothing_items = ClothingItem.objects.all()
for item in clothing_items:
    print(f"Item: {item.name}, User: {item.user.username}")
```

Django translates this into SQL queries. But there's a problem...

### The N+1 Query Problem

The code above creates an **N+1 query problem**:

1. **1 query** to get all clothing items
2. **N queries** (one for each item) to get the user information

If you have 100 clothing items, that's 101 database queries! This is extremely inefficient.

## 🚀 Query Optimization Techniques

### 1. Using `select_related()` for Foreign Keys

**Problem**: When you access a foreign key, Django makes an additional query.

```python
# ❌ BAD: N+1 queries
clothing_items = ClothingItem.objects.all()
for item in clothing_items:
    print(item.user.username)  # Additional query for each item
```

**Solution**: Use `select_related()` to fetch related data in a single query.

```python
# ✅ GOOD: 1 query
clothing_items = ClothingItem.objects.select_related('user').all()
for item in clothing_items:
    print(item.user.username)  # No additional queries
```

**Real Example from Our Project**:

In `apps/wardrobe/models.py`, we have:

```python
class ClothingItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clothing_items')
    category = models.ForeignKey(ClothingCategory, on_delete=models.SET_NULL, null=True)
    # ... other fields
```

To optimize queries that need user and category information:

```python
# Optimized query
items = ClothingItem.objects.select_related('user', 'category').all()
```

### 2. Using `prefetch_related()` for Many-to-Many and Reverse Foreign Keys

**Problem**: When you access related objects in the opposite direction, Django makes additional queries.

```python
# ❌ BAD: N+1 queries
user = User.objects.get(id=1)
for item in user.clothing_items.all():  # Additional query
    print(item.name)
```

**Solution**: Use `prefetch_related()` to fetch related data efficiently.

```python
# ✅ GOOD: 2 queries total
user = User.objects.prefetch_related('clothing_items').get(id=1)
for item in user.clothing_items.all():  # No additional queries
    print(item.name)
```

**Real Example from Our Project**:

```python
# Get user with all their clothing items and images
user = User.objects.prefetch_related(
    'clothing_items',
    'clothing_items__images'
).get(id=1)

# Now accessing user.clothing_items.all() and item.images.all()
# won't create additional queries
```

### 3. Using `only()` and `defer()` for Field Selection

**Problem**: Sometimes you only need specific fields, but Django fetches all fields.

```python
# ❌ BAD: Fetches all fields
items = ClothingItem.objects.all()
for item in items:
    print(item.name)  # Only using the name field
```

**Solution**: Use `only()` to fetch only the fields you need.

```python
# ✅ GOOD: Fetches only name field
items = ClothingItem.objects.only('name').all()
for item in items:
    print(item.name)
```

**Real Example**:

```python
# Only fetch essential fields for a list view
clothing_items = ClothingItem.objects.only(
    'id', 'name', 'brand', 'color', 'ai_analysis_status'
).select_related('category').all()
```

### 4. Database Indexing

**What are Indexes?**
Indexes are like a book's index - they help the database find data quickly without scanning every row.

**When to Add Indexes**:

- Fields used in `WHERE` clauses
- Fields used in `ORDER BY`
- Foreign key fields
- Fields used for searching

**Example from Our Project**:

```python
class ClothingItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clothing_items')
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    ai_analysis_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),  # For user's items sorted by date
            models.Index(fields=['brand']),               # For brand searches
            models.Index(fields=['color']),               # For color filtering
            models.Index(fields=['ai_analysis_status']),  # For status filtering
        ]
```

## 📊 Performance Monitoring

### Using Django Debug Toolbar

In development, you can use Django Debug Toolbar to see:

- Number of database queries
- Query execution time
- SQL statements generated

### Using `django.db.connection.queries`

```python
from django.db import connection

# Your code here
clothing_items = ClothingItem.objects.select_related('user').all()

# Check how many queries were executed
print(f"Number of queries: {len(connection.queries)}")
for query in connection.queries:
    print(f"Query: {query['sql']}")
    print(f"Time: {query['time']}")
```

## 🎯 Real-World Optimization Examples

### Example 1: User Profile with Clothing Items

**Before Optimization**:

```python
# This could generate 100+ queries for a user with 100 items
def get_user_profile(user_id):
    user = User.objects.get(id=user_id)
    items = user.clothing_items.all()
    return {
        'user': user,
        'items': items,
        'total_items': items.count(),  # Additional query!
    }
```

**After Optimization**:

```python
def get_user_profile(user_id):
    user = User.objects.prefetch_related('clothing_items').get(id=user_id)
    items = list(user.clothing_items.all())  # Convert to list to avoid additional queries
    return {
        'user': user,
        'items': items,
        'total_items': len(items),  # No additional query
    }
```

### Example 2: Clothing Item List with Images

**Before Optimization**:

```python
# This could generate 1000+ queries for 100 items with 10 images each
items = ClothingItem.objects.all()
for item in items:
    images = item.images.all()  # Additional query for each item
    print(f"{item.name}: {images.count()} images")
```

**After Optimization**:

```python
# This generates only 2 queries total
items = ClothingItem.objects.prefetch_related('images').all()
for item in items:
    images = list(item.images.all())  # No additional queries
    print(f"{item.name}: {len(images)} images")
```

## 🚨 Common Performance Pitfalls

### 1. Calling `.count()` in Loops

```python
# ❌ BAD: Additional query for each item
for item in ClothingItem.objects.all():
    print(f"Item has {item.images.count()} images")
```

### 2. Using `.all()` Multiple Times

```python
# ❌ BAD: Multiple queries
items = ClothingItem.objects.all()
if items.exists():  # Query 1
    for item in items:  # Query 2
        print(item.name)
```

### 3. Not Using `select_related` for Foreign Keys

```python
# ❌ BAD: Additional query for each item
for item in ClothingItem.objects.all():
    print(item.user.username)  # Additional query
```

## 📈 Performance Metrics

### What to Measure

- **Response Time**: How long does the page take to load?
- **Database Queries**: How many queries are executed?
- **Memory Usage**: How much memory does your app use?
- **CPU Usage**: How much processing power is needed?

### Tools for Monitoring

- **Django Debug Toolbar** (development)
- **Django Silk** (profiling)
- **New Relic** (production monitoring)
- **Django Extensions** (management commands)

## 🎯 Best Practices Summary

1. **Always use `select_related()`** for foreign key relationships
2. **Always use `prefetch_related()`** for reverse foreign keys and many-to-many
3. **Use `only()` and `defer()`** to fetch only needed fields
4. **Add database indexes** for frequently queried fields
5. **Monitor query performance** in development
6. **Test with realistic data** (not just a few records)
7. **Use pagination** for large datasets

## 📝 Practice Exercise

Look at the `apps/wardrobe/views.py` file and identify potential optimization opportunities:

1. Are there any N+1 query problems?
2. Could `select_related()` or `prefetch_related()` be used?
3. Are there any unnecessary database queries?

## 🔗 Next Steps

Now that you understand backend optimization, learn about:

- [Caching in Django](./caching-in-django.md) - Further performance improvements
- [Async and Task Queues](./async-and-task-queues.md) - Handling time-consuming operations

## 📚 Additional Resources

- [Django Database Optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [Django ORM Best Practices](https://docs.djangoproject.com/en/stable/topics/db/queries/)
- [Database Indexing Guide](https://use-the-index-luke.com/)

---

**Ready to make your app even faster?** Learn about caching in [Caching in Django](./caching-in-django.md).
