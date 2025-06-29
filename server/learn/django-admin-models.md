# Django Models and Admin Panel

## 🎯 What You'll Learn

In this module, you'll learn how Django models work, how to create them, and how to use Django's powerful admin interface to manage your data. This is fundamental to understanding how Django stores and retrieves data.

## 🧠 What are Django Models?

Think of Django models as the blueprint for your database tables. They define:

- What data you want to store
- What type each piece of data is (text, number, date, etc.)
- How different pieces of data relate to each other

### Real Example from Our Project

Let's look at a model from `apps/wardrobe/models.py`:

```python
class ClothingItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Analysis Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clothing_items')
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ClothingCategory, on_delete=models.SET_NULL, null=True)
    brand = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=20, blank=True)
    material = models.CharField(max_length=100, blank=True)
    pattern = models.CharField(max_length=50, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    ai_analysis_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    wear_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
```

## 📊 Understanding Model Fields

### Common Field Types

| Field Type      | Purpose                       | Example                                                        |
| --------------- | ----------------------------- | -------------------------------------------------------------- |
| `CharField`     | Short text                    | `name = models.CharField(max_length=200)`                      |
| `TextField`     | Long text                     | `description = models.TextField()`                             |
| `IntegerField`  | Whole numbers                 | `wear_count = models.PositiveIntegerField()`                   |
| `DecimalField`  | Decimal numbers               | `price = models.DecimalField(max_digits=10, decimal_places=2)` |
| `BooleanField`  | True/False                    | `is_active = models.BooleanField(default=True)`                |
| `DateField`     | Date only                     | `purchase_date = models.DateField()`                           |
| `DateTimeField` | Date and time                 | `created_at = models.DateTimeField(auto_now_add=True)`         |
| `ForeignKey`    | Relationship to another model | `user = models.ForeignKey(User, on_delete=models.CASCADE)`     |
| `UUIDField`     | Unique identifier             | `id = models.UUIDField(primary_key=True, default=uuid.uuid4)`  |

### Field Options

```python
# Common field options
name = models.CharField(
    max_length=200,        # Maximum length
    blank=True,            # Can be empty in forms
    null=True,             # Can be NULL in database
    default='',            # Default value
    unique=True,           # Must be unique
    help_text='Enter the item name'  # Help text for forms
)
```

## 🔗 Model Relationships

### ForeignKey (Many-to-One)

```python
class ClothingItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clothing_items')
    category = models.ForeignKey(ClothingCategory, on_delete=models.SET_NULL, null=True)
```

**What this means:**

- Each clothing item belongs to one user
- Each clothing item can have one category
- `related_name='clothing_items'` lets you do `user.clothing_items.all()`

### One-to-Many (Reverse ForeignKey)

```python
# From the User side
user = User.objects.get(id=1)
user_items = user.clothing_items.all()  # All items belonging to this user
```

### Many-to-Many

```python
class ClothingItem(models.Model):
    tags = models.ManyToManyField('Tag', blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=50)
```

## 🏗️ Creating and Using Models

### Creating Objects

```python
# Method 1: Using create()
clothing_item = ClothingItem.objects.create(
    user=request.user,
    name="Blue T-Shirt",
    brand="Nike",
    color="Blue"
)

# Method 2: Create and save
clothing_item = ClothingItem(
    user=request.user,
    name="Red Jeans",
    brand="Levi's",
    color="Red"
)
clothing_item.save()
```

### Querying Objects

```python
# Get all items
all_items = ClothingItem.objects.all()

# Get items for a specific user
user_items = ClothingItem.objects.filter(user=request.user)

# Get a specific item
item = ClothingItem.objects.get(id=item_id)

# Get items with conditions
blue_items = ClothingItem.objects.filter(color='Blue')
expensive_items = ClothingItem.objects.filter(price__gte=100)  # Greater than or equal
recent_items = ClothingItem.objects.filter(created_at__gte=datetime.now() - timedelta(days=7))
```

### Updating Objects

```python
# Method 1: Update specific fields
clothing_item.name = "Updated Name"
clothing_item.save()

# Method 2: Update multiple objects
ClothingItem.objects.filter(color='Blue').update(color='Navy Blue')
```

### Deleting Objects

```python
# Delete a specific item
clothing_item.delete()

# Delete multiple items
ClothingItem.objects.filter(color='Red').delete()
```

## 🎛️ Django Admin Panel

The Django admin panel is a powerful built-in interface for managing your data. It's automatically generated from your models.

### Registering Models

In `apps/wardrobe/admin.py`:

```python
from django.contrib import admin
from .models import ClothingItem, ClothingCategory, ClothingImage, AIAnalysis

@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'brand', 'color', 'ai_analysis_status', 'created_at']
    list_filter = ['ai_analysis_status', 'category', 'brand', 'color', 'created_at']
    search_fields = ['name', 'brand', 'description']
    list_editable = ['ai_analysis_status']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'category', 'description')
        }),
        ('Details', {
            'fields': ('brand', 'color', 'size', 'material', 'pattern')
        }),
        ('Purchase Information', {
            'fields': ('price', 'purchase_date', 'purchase_location')
        }),
        ('Status', {
            'fields': ('ai_analysis_status', 'wear_count', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ClothingCategory)
class ClothingCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(ClothingImage)
class ClothingImageAdmin(admin.ModelAdmin):
    list_display = ['clothing_item', 'image_type', 'upload_order', 'file_size']
    list_filter = ['image_type', 'created_at']
    search_fields = ['clothing_item__name']
```

### Admin Configuration Options

#### `list_display`

Shows which fields appear in the list view:

```python
list_display = ['name', 'user', 'brand', 'color', 'ai_analysis_status']
```

#### `list_filter`

Adds filters to the right sidebar:

```python
list_filter = ['ai_analysis_status', 'category', 'brand', 'color']
```

#### `search_fields`

Enables search functionality:

```python
search_fields = ['name', 'brand', 'description']
```

#### `list_editable`

Allows editing fields directly in the list view:

```python
list_editable = ['ai_analysis_status', 'wear_count']
```

#### `fieldsets`

Organizes fields into groups:

```python
fieldsets = (
    ('Basic Info', {'fields': ('name', 'user')}),
    ('Details', {'fields': ('brand', 'color', 'size')}),
    ('Advanced', {
        'fields': ('ai_analysis_status',),
        'classes': ('collapse',)  # Makes section collapsible
    }),
)
```

#### `readonly_fields`

Makes fields read-only:

```python
readonly_fields = ['created_at', 'updated_at']
```

#### `prepopulated_fields`

Auto-generates fields from other fields:

```python
prepopulated_fields = {'slug': ('name',)}
```

### Custom Admin Actions

```python
@admin.register(ClothingItem)
class ClothingItemAdmin(admin.ModelAdmin):
    # ... other configurations ...

    actions = ['mark_as_completed', 'reset_analysis']

    def mark_as_completed(self, request, queryset):
        """Mark selected items as completed"""
        updated = queryset.update(ai_analysis_status='completed')
        self.message_user(request, f'{updated} items marked as completed.')
    mark_as_completed.short_description = "Mark selected items as completed"

    def reset_analysis(self, request, queryset):
        """Reset AI analysis status"""
        updated = queryset.update(ai_analysis_status='pending')
        self.message_user(request, f'{updated} items reset to pending.')
    reset_analysis.short_description = "Reset AI analysis status"
```

## 🎯 Real-World Examples from Our Project

### User Profile Model

From `apps/authentication/models.py`:

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
```

### AI Analysis Model

```python
class AIAnalysis(models.Model):
    clothing_item = models.OneToOneField(ClothingItem, on_delete=models.CASCADE, related_name='ai_analysis')
    gemini_raw_response = models.JSONField()
    extracted_data = models.JSONField()
    confidence_scores = models.JSONField()
    processing_time = models.DurationField(null=True, blank=True)
    api_cost = models.DecimalField(max_digits=8, decimal_places=4, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Analysis for {self.clothing_item.name}"
```

## 📝 Practice Exercise

1. Look at the models in `apps/wardrobe/models.py`
2. Try creating a new clothing item through the Django shell:

   ```bash
   python manage.py shell
   ```

   ```python
   from apps.wardrobe.models import ClothingItem
   from django.contrib.auth.models import User

   user = User.objects.first()
   item = ClothingItem.objects.create(
       user=user,
       name="Test Item",
       brand="Test Brand",
       color="Red"
   )
   print(item)
   ```

3. Visit the Django admin panel and explore the interface

## 🔗 Next Steps

Now that you understand models and admin, learn about:

- [Django URLs and Views](./django-urls-views.md) - How to create web pages
- [Django Serializers](./django-serializers.md) - Converting models to JSON

## 📚 Additional Resources

- [Django Models Documentation](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Admin Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [Django ORM Documentation](https://docs.djangoproject.com/en/stable/topics/db/queries/)

---

**Ready to create web pages?** Learn about URLs and views in [Django URLs and Views](./django-urls-views.md).
