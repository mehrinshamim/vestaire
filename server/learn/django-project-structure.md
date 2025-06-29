# Django Project Structure and App Modularization

## 🎯 What You'll Learn

In this module, you'll understand how Django projects are organized, why we use the concept of "apps," and how to structure your code for maintainability and scalability.

## 📁 Understanding Django Project Structure

### What is a Django Project?

A Django project is like a container that holds your entire web application. Think of it as a house that contains multiple rooms (apps), each serving a specific purpose.

### Our Project Structure

Let's look at the structure of this project:

```
server/
├── manage.py                 # Django's command-line utility
├── vestaire/                 # Main project directory
│   ├── __init__.py
│   ├── settings/             # Settings for different environments
│   │   └── base.py          # Base settings shared by all environments
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration for deployment
│   └── celery.py            # Celery configuration for background tasks
├── apps/                     # All Django apps live here
│   ├── authentication/       # Handles user login, registration, profiles
│   ├── core/                 # Shared utilities and common functionality
│   └── wardrobe/             # Main business logic for clothing management
├── requirements/             # Python dependencies
│   ├── base.txt             # Common dependencies
│   ├── development.txt      # Development-specific dependencies
│   └── production.txt       # Production-specific dependencies
└── docs/                     # Project documentation
```

## 🏗️ The Apps Directory Pattern

### Why Use the `apps/` Directory?

Instead of putting apps directly in the project root, we organize them in an `apps/` directory. This provides several benefits:

1. **Clear Separation**: All your custom apps are in one place
2. **Better Organization**: Easier to find and manage apps
3. **Scalability**: As your project grows, you can easily add more apps
4. **Import Clarity**: Clear distinction between Django's built-in apps and your custom apps

### How It Works

In `vestaire/settings/base.py`, you'll see:

```python
INSTALLED_APPS = [
    'django.contrib.admin',        # Django's built-in admin
    'django.contrib.auth',         # Django's authentication system
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',              # Third-party package
    'rest_framework_simplejwt',    # Third-party package
    'corsheaders',                 # Third-party package
    'drf_spectacular',            # Third-party package
    'apps.authentication',         # Our custom app
    'apps.wardrobe',              # Our custom app
    'apps.core',                  # Our custom app
]
```

Notice how our custom apps are prefixed with `apps.` - this tells Django where to find them.

## 🧩 Understanding Django Apps

### What is a Django App?

A Django app is a Python package that implements a specific functionality. Think of it as a module that handles a particular feature of your website.

### Our Apps Explained

#### 1. `apps.authentication` - User Management

**Purpose**: Handles everything related to users

**What it contains**:

- User registration and login
- User profiles
- Password management
- JWT token handling

**Key files**:

```
apps/authentication/
├── models.py          # UserProfile model
├── views.py           # Login, registration, profile views
├── serializers.py     # Data validation for API
├── urls.py           # URL routing for this app
└── admin.py          # Django admin configuration
```

#### 2. `apps.wardrobe` - Main Business Logic

**Purpose**: Handles clothing item management and AI analysis

**What it contains**:

- Clothing item models
- Image processing
- AI analysis with Gemini
- Background task processing

**Key files**:

```
apps/wardrobe/
├── models.py          # ClothingItem, ClothingImage, AIAnalysis models
├── views.py           # API endpoints for clothing management
├── serializers.py     # Data validation
├── services/          # Business logic services
│   ├── ai_service.py      # AI analysis logic
│   ├── image_service.py   # Image processing
│   └── storage_service.py # Cloud storage handling
├── tasks.py           # Background tasks (Celery)
└── urls.py           # URL routing
```

#### 3. `apps.core` - Shared Utilities

**Purpose**: Contains code that's used across multiple apps

**What it contains**:

- Common exceptions
- Shared permissions
- Utility functions
- Base models

## 🔧 Settings Management

### Why Multiple Settings Files?

In `vestaire/settings/`, we have different settings files for different environments:

- **`base.py`**: Common settings shared by all environments
- **`development.py`**: Settings specific to development (debugging, local database)
- **`production.py`**: Settings specific to production (optimized, secure)

This follows the **12-Factor App** methodology (we'll learn more about this later).

### Key Settings Explained

From `vestaire/settings/base.py`:

```python
# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # SQLite for development
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Celery Configuration (for background tasks)
CELERY_BROKER_URL = config('REDIS_URL')
CELERY_RESULT_BACKEND = config('REDIS_URL')
```

## 🎯 Best Practices Demonstrated

### 1. Separation of Concerns

Each app has a single responsibility:

- `authentication` handles users
- `wardrobe` handles clothing
- `core` handles shared utilities

### 2. Modular Design

Apps can be developed and tested independently. You could even reuse them in other projects!

### 3. Clear Naming

App names clearly indicate their purpose:

- `authentication` - obvious what it does
- `wardrobe` - handles clothing items
- `core` - shared functionality

### 4. Environment-Specific Settings

Different settings for different environments ensure your app behaves correctly in development, testing, and production.

## 🚀 Real-World Benefits

### Scalability

As your project grows, you can easily add new apps:

```
apps/
├── authentication/
├── wardrobe/
├── core/
├── notifications/     # New app for notifications
├── analytics/         # New app for analytics
└── payments/          # New app for payment processing
```

### Team Development

Different developers can work on different apps without conflicts.

### Testing

You can test each app independently, making debugging easier.

### Deployment

You can deploy apps separately if needed (microservices architecture).

## 📝 Practice Exercise

Try to identify the purpose of each file in the project:

1. Look at `apps/authentication/models.py` - what does it define?
2. Check `apps/wardrobe/views.py` - what endpoints does it provide?
3. Examine `vestaire/urls.py` - how does it route requests to different apps?

## 🔗 Next Steps

Now that you understand Django project structure, you're ready to learn about:

- [Backend Optimization](./backend-optimization.md) - Making your app fast
- [Caching in Django](./caching-in-django.md) - Improving performance
- [Async and Task Queues](./async-and-task-queues.md) - Handling background tasks

## 📚 Additional Resources

- [Django Apps Documentation](https://docs.djangoproject.com/en/stable/intro/tutorial01/#creating-the-polls-app)
- [Django Settings Documentation](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Django Project Structure Best Practices](https://docs.djangoproject.com/en/stable/intro/reusable-apps/)

---

**Ready for the next challenge?** Learn how to optimize your Django application in [Backend Optimization](./backend-optimization.md).
