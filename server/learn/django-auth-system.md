# Django Authentication System

## 🎯 What You'll Learn

- How Django's built-in authentication system works
- The User model and how to extend it
- Permissions and groups
- How our project builds on Django's auth system

---

## Django's Built-in Authentication

Django comes with a complete authentication system that handles:
- User accounts and passwords
- Permissions and groups
- Session management
- Password hashing and validation

---

## The User Model

### Default User Model

Django provides a built-in User model with these fields:
- `username` - Unique username
- `email` - Email address
- `first_name`, `last_name` - User's name
- `password` - Hashed password
- `is_active` - Whether the account is active
- `is_staff` - Whether the user can access admin
- `is_superuser` - Whether the user has all permissions
- `date_joined` - When the account was created
- `last_login` - When the user last logged in

### Creating Users

```python
from django.contrib.auth.models import User

# Method 1: Using create_user (recommended)
user = User.objects.create_user(
    username='john_doe',
    email='john@example.com',
    password='secure_password123'
)

# Method 2: Using create (not recommended for users)
user = User.objects.create(
    username='jane_doe',
    email='jane@example.com'
)
user.set_password('secure_password123')
user.save()
```

---

## Extending the User Model

### Method 1: OneToOneField (Recommended)

Create a separate model linked to User:

```python
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
```

**Usage:**
```python
# Access profile from user
user = User.objects.get(username='john_doe')
profile = user.profile  # Thanks to related_name='profile'

# Access user from profile
profile = UserProfile.objects.get(id=1)
user = profile.user
```

### Method 2: Custom User Model

Create a completely custom User model:

```python
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Add custom fields here
```

**Settings configuration:**
```python
# settings.py
AUTH_USER_MODEL = 'your_app.CustomUser'
```

---

## Permissions and Groups

### Django's Permission System

Django has a built-in permission system with three types:
- **Model permissions**: add, change, delete, view
- **Object permissions**: permissions on specific instances
- **Custom permissions**: user-defined permissions

### Checking Permissions

```python
# Check if user has permission
if user.has_perm('wardrobe.add_clothingitem'):
    # User can add clothing items
    pass

# Check if user has permission on specific object
if user.has_perm('wardrobe.change_clothingitem', clothing_item):
    # User can change this specific clothing item
    pass
```

### Groups

Groups are collections of permissions:

```python
from django.contrib.auth.models import Group, Permission

# Create a group
moderators = Group.objects.create(name='Moderators')

# Add permissions to group
add_permission = Permission.objects.get(codename='add_clothingitem')
moderators.permissions.add(add_permission)

# Add user to group
user.groups.add(moderators)
```

---

## Real Examples from Our Project

### User Profile Model

```python
# apps/authentication/models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
```

### User Registration

```python
# apps/authentication/serializers.py
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user
```

### User Profile View

```python
# apps/authentication/views.py
@extend_schema(tags=['Authentication'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Get the current user's profile, create if doesn't exist."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
```

---

## Authentication in Views

### Function-Based Views

```python
from django.contrib.auth.decorators import login_required

@login_required
def my_view(request):
    # This view requires authentication
    return HttpResponse("Hello, authenticated user!")
```

### Class-Based Views

```python
from django.contrib.auth.mixins import LoginRequiredMixin

class MyView(LoginRequiredMixin, View):
    # This view requires authentication
    def get(self, request):
        return HttpResponse("Hello, authenticated user!")
```

### DRF Views

```python
from rest_framework.permissions import IsAuthenticated

class ClothingItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClothingItemSerializer
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)
```

---

## Password Management

### Password Validation

Django has built-in password validation:

```python
# settings.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

### Password Change

```python
# apps/authentication/views.py
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    if not user.check_password(old_password):
        return Response({'error': 'Current password is incorrect'}, status=400)
    
    if new_password != confirm_password:
        return Response({'error': 'New passwords do not match'}, status=400)
    
    user.set_password(new_password)
    user.save()
    
    return Response({'message': 'Password changed successfully'})
```

---

## Session Management

### Session Configuration

```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_SECURE = True  # Use HTTPS only
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
```

### Session Usage

```python
# Store data in session
request.session['user_preference'] = 'dark_mode'

# Retrieve data from session
preference = request.session.get('user_preference', 'light_mode')

# Delete session data
del request.session['user_preference']
```

---

## Best Practices

1. **Use create_user()** - Always use `create_user()` instead of `create()` for users
2. **Hash passwords** - Never store plain text passwords
3. **Use OneToOneField** - Extend User model with OneToOneField for most cases
4. **Check permissions** - Always check permissions before allowing actions
5. **Use groups** - Organize permissions using groups
6. **Secure sessions** - Use secure session settings in production

---

## Practice Exercise

1. Look at the UserProfile model in `apps/authentication/models.py`
2. Create a new user and profile through the Django shell
3. Test the authentication views in the API
4. Try changing a user's password

---

## Next Steps

- [JWT Authentication](./jwt-authentication.md) - Token-based authentication
- [Swagger Documentation](./swagger-drf-spectacular.md) - API documentation

---