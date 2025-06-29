# Swagger Documentation with drf-spectacular

## 🎯 What You'll Learn

- What Swagger/OpenAPI documentation is
- How to set up drf-spectacular in Django
- How to customize your API documentation
- Best practices for API documentation

---

## What is Swagger/OpenAPI?

Swagger (now OpenAPI) is a specification for documenting REST APIs. It provides:
- Interactive API documentation
- Automatic code generation
- API testing interface
- Standardized API descriptions

---

## Setting Up drf-spectacular

### Installation

```bash
pip install drf-spectacular
```

### Settings Configuration

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Vestaire API',
    'DESCRIPTION': 'API for clothing management with AI analysis',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

### URL Configuration

```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # ... other URLs ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## Basic Usage

### Automatic Schema Generation

drf-spectacular automatically generates schema from your views:

```python
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Authentication'])
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
```

### Adding Descriptions

```python
@extend_schema(
    tags=['Authentication'],
    description='Register a new user account',
    responses={201: UserRegistrationSerializer}
)
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
```

---

## Decorating Views

### Function-Based Views

```python
@extend_schema(
    tags=['Authentication'],
    request=LoginSerializer,
    responses={200: None}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # Your view logic here
    pass
```

### Class-Based Views

```python
@extend_schema(
    tags=['Wardrobe'],
    description='List and create clothing items',
    responses={200: ClothingItemSerializer(many=True)}
)
class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
```

---

## Customizing Documentation

### Adding Examples

```python
@extend_schema(
    tags=['Authentication'],
    request=LoginSerializer,
    responses={
        200: inline_serializer(
            name='LoginResponse',
            fields={
                'refresh': serializers.CharField(),
                'access': serializers.CharField(),
                'user': UserSerializer()
            }
        ),
        401: inline_serializer(
            name='LoginError',
            fields={'error': serializers.CharField()}
        )
    },
    examples=[
        OpenApiExample(
            'Successful Login',
            value={
                'username': 'john_doe',
                'password': 'secure_password123'
            },
            request_only=True
        ),
        OpenApiExample(
            'Login Response',
            value={
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': 1,
                    'username': 'john_doe',
                    'email': 'john@example.com'
                }
            },
            response_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # Your login logic here
    pass
```

### Custom Response Schemas

```python
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers

@extend_schema(
    tags=['Wardrobe'],
    responses={
        200: inline_serializer(
            name='ClothingItemListResponse',
            fields={
                'count': serializers.IntegerField(),
                'next': serializers.CharField(allow_null=True),
                'previous': serializers.CharField(allow_null=True),
                'results': ClothingItemSerializer(many=True)
            }
        )
    }
)
class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
```

---

## Real Examples from Our Project

### Authentication Views

```python
@extend_schema(tags=['Authentication'])
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

@extend_schema(
    tags=['Authentication'],
    request=LoginSerializer,
    responses={200: None}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    # Login logic here
    pass

@extend_schema(
    tags=['Authentication'],
    description='User logout endpoint that blacklists the refresh token.',
    request=inline_serializer(
        name='LogoutRequest',
        fields={'refresh': serializers.CharField()}
    ),
    responses={
        200: inline_serializer(
            name='LogoutResponse',
            fields={'message': serializers.CharField()}
        ),
        400: inline_serializer(
            name='LogoutError',
            fields={'error': serializers.CharField()}
        )
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Logout logic here
    pass
```

### Wardrobe Views

```python
@extend_schema(tags=['Wardrobe'])
class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        description='List all clothing items for the authenticated user',
        responses={200: ClothingItemSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        description='Create a new clothing item',
        request=ClothingItemSerializer,
        responses={201: ClothingItemSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
```

---

## Advanced Customization

### Custom Tags

```python
@extend_schema(
    tags=['User Management'],
    operation_id='create_user_profile',
    operation_summary='Create user profile',
    operation_description='Create a new user profile with additional information'
)
class UserProfileView(generics.CreateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
```

### Parameter Documentation

```python
@extend_schema(
    tags=['Wardrobe'],
    parameters=[
        OpenApiParameter(
            name='color',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter items by color'
        ),
        OpenApiParameter(
            name='brand',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Filter items by brand'
        )
    ]
)
class ClothingItemViewSet(viewsets.ModelViewSet):
    # Your view logic here
    pass
```

### Custom Response Headers

```python
@extend_schema(
    tags=['Wardrobe'],
    responses={
        200: ClothingItemSerializer,
        404: inline_serializer(
            name='NotFoundError',
            fields={'error': serializers.CharField()}
        )
    },
    response_headers={
        'X-Total-Count': OpenApiParameter(
            type=OpenApiTypes.INT,
            description='Total number of items'
        )
    }
)
class ClothingItemDetailView(generics.RetrieveAPIView):
    # Your view logic here
    pass
```

---

## Configuration Options

### Spectacular Settings

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Vestaire API',
    'DESCRIPTION': 'API for clothing management with AI analysis',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    
    # Customize the schema
    'SCHEMA_PATH_PREFIX': '/api/',
    'SCHEMA_PATH_PREFIX_TRIM': True,
    
    # Authentication
    'SECURITY': [
        {
            'Bearer': []
        }
    ],
    
    # Tags
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication endpoints'},
        {'name': 'Wardrobe', 'description': 'Clothing item management'},
        {'name': 'AI Analysis', 'description': 'AI-powered clothing analysis'},
    ],
    
    # Custom components
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': False,
}
```

---

## Best Practices

### 1. Use Descriptive Tags

```python
@extend_schema(tags=['User Management'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    # Your view logic here
    pass
```

### 2. Document Request/Response Examples

```python
@extend_schema(
    tags=['Wardrobe'],
    examples=[
        OpenApiExample(
            'Create Clothing Item',
            value={
                'name': 'Blue T-Shirt',
                'brand': 'Nike',
                'color': 'Blue',
                'size': 'M'
            },
            request_only=True
        )
    ]
)
```

### 3. Use Proper HTTP Status Codes

```python
@extend_schema(
    tags=['Authentication'],
    responses={
        200: UserSerializer,
        400: inline_serializer(
            name='ValidationError',
            fields={'error': serializers.CharField()}
        ),
        401: inline_serializer(
            name='UnauthorizedError',
            fields={'error': serializers.CharField()}
        )
    }
)
```

### 4. Group Related Endpoints

```python
# Use consistent tags for related endpoints
@extend_schema(tags=['Wardrobe'])
class ClothingItemViewSet(viewsets.ModelViewSet):
    pass

@extend_schema(tags=['Wardrobe'])
class ClothingCategoryViewSet(viewsets.ModelViewSet):
    pass
```

---

## Testing Your Documentation

### Generate Schema

```bash
python manage.py spectacular --file schema.yml
```

### View Documentation

1. Start your Django server
2. Visit `/api/docs/` for Swagger UI
3. Visit `/api/schema/` for raw OpenAPI schema

### Validate Schema

```bash
python manage.py spectacular --validate
```

---

## Practice Exercise

1. Look at the existing `@extend_schema` decorators in your views
2. Add documentation to a view that doesn't have it
3. Create custom response schemas for error cases
4. Add examples to your API documentation
5. Test the generated documentation

---

## Next Steps

- [Django Models and Admin](./django-admin-models.md) - Understanding data models
- [DRF Basics](./drf-basics.md) - Building REST APIs

---

## Additional Resources

- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

---