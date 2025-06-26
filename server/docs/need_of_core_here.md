# 1
The `core/models.py` file in a Django project is typically used for **shared, reusable base models** that can be inherited by other models throughout your project.

---

## **Why have a `core/models.py`?**

- **Centralizes common model logic:**  
  If you have fields or behaviors that are common to many models (like timestamps, soft delete, etc.), you define them once in `core/models.py` and inherit them everywhere else.
- **Promotes DRY (Don’t Repeat Yourself):**  
  Avoids duplicating the same code in multiple apps.

---

**In summary:**  
`core/models.py` is for defining base models and shared model logic that you want to reuse throughout your Django project, making your codebase cleaner and more maintainable.


# 2
Absolutely! Here are some **practical use cases** for a `core` app in your digital wardrobe Django project:

---

## **1. Abstract Base Models**
**Use case:**  
You want all your models (e.g., `ClothingItem`, `ClothingImage`, `AIAnalysis`) to have `created_at` and `updated_at` fields.

**How:**  
Define a `TimeStampedModel` in `core/models.py` and inherit it in other models.

```python
# core/models.py
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# apps/wardrobe/models.py
from apps.core.models import TimeStampedModel

class ClothingItem(TimeStampedModel):
    # ... your fields ...
    pass
```

---

## **2. Custom Permissions**
**Use case:**  
You want to restrict certain API endpoints (e.g., only allow users to edit their own clothing items).

**How:**  
Define a custom permission in `core/permissions.py`:

```python
# core/permissions.py
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
```

Then use it in your viewsets:

```python
from apps.core.permissions import IsOwner

class ClothingItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner]
    # ...
```

---

## **3. Custom Validators**
**Use case:**  
You want to validate that a clothing item's name is unique per user.

**How:**  
Define a validator in `core/validators.py`:

```python
# core/validators.py
from rest_framework import serializers

def unique_name_per_user(value, user):
    if ClothingItem.objects.filter(name=value, user=user).exists():
        raise serializers.ValidationError("You already have an item with this name.")
```

Use it in your serializer:

```python
from apps.core.validators import unique_name_per_user

class ClothingItemSerializer(serializers.ModelSerializer):
    def validate_name(self, value):
        unique_name_per_user(value, self.context['request'].user)
        return value
```

---

## **4. Utility Functions**
**Use case:**  
You want to generate a unique slug for each clothing category.

**How:**  
Define a utility in `core/utils.py`:

```python
# core/utils.py
from django.utils.text import slugify

def unique_slugify(instance, value, slug_field_name='slug'):
    slug = slugify(value)
    ModelClass = instance.__class__
    unique_slug = slug
    num = 1
    while ModelClass.objects.filter(**{slug_field_name: unique_slug}).exists():
        unique_slug = f"{slug}-{num}"
        num += 1
    return unique_slug
```

Use it in your model’s `save()` method:

```python
from apps.core.utils import unique_slugify

class ClothingCategory(models.Model):
    # ...
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)
```

---

## **5. Custom Exceptions**
**Use case:**  
You want to raise a custom exception for a specific business rule.

**How:**  
Define in `core/exceptions.py`:

```python
# core/exceptions.py
class WardrobeLimitExceeded(Exception):
    pass
```

Use it in your business logic:

```python
from apps.core.exceptions import WardrobeLimitExceeded

def add_clothing_item(user, ...):
    if user.clothing_items.count() > 100:
        raise WardrobeLimitExceeded("You can't have more than 100 items.")
```

---

## **Summary Table**

| File                  | Example Use Case                                  |
|-----------------------|---------------------------------------------------|
| `core/models.py`      | Abstract base models (timestamps, soft delete)    |
| `core/permissions.py` | Custom DRF permissions (e.g., IsOwner)            |
| `core/validators.py`  | Custom field/model validators                     |
| `core/utils.py`       | Utility functions (e.g., slugify, file handling)  |
| `core/exceptions.py`  | Custom exception classes                          |

---

**In summary:**  
A `core` app is a great place for any code that is shared, reusable, or cross-cutting across your Django project. It helps keep your code DRY, organized, and maintainable!