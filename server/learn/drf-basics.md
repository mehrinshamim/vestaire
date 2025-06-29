# Django REST Framework Basics

## 🎯 What You'll Learn

- What Django REST Framework (DRF) is and why it's useful
- Different types of DRF views (APIView, ViewSet, Generic Views)
- DRF routers and URL patterns
- Building complete REST APIs

---

## What is Django REST Framework?

Django REST Framework (DRF) is a powerful toolkit for building Web APIs. It extends Django to make it easy to build RESTful APIs.

**Key features:**
- Serializers for converting data
- Powerful views for handling requests
- Authentication and permissions
- Automatic API documentation
- Browsable API interface

---

## DRF Views Overview

### APIView

The most basic DRF view - similar to Django's View class:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ClothingItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all clothing items"""
        items = ClothingItem.objects.filter(user=request.user)
        serializer = ClothingItemSerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new clothing item"""
        serializer = ClothingItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Generic Views

DRF provides generic views for common operations:

```python
from rest_framework import generics

class ClothingItemListCreateView(generics.ListCreateAPIView):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ClothingItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)
```

### ViewSets

ViewSets combine common operations into a single class:

```python
from rest_framework import viewsets

class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

---

## DRF Routers

Routers automatically create URL patterns for ViewSets:

```python
from rest_framework.routers import DefaultRouter
from .views import ClothingItemViewSet

router = DefaultRouter()
router.register(r'clothing', ClothingItemViewSet, basename='clothing')

urlpatterns = [
    path('', include(router.urls)),
]
```

**This creates these URLs automatically:**
- `GET /clothing/` - List all items
- `POST /clothing/` - Create new item
- `GET /clothing/{id}/` - Get specific item
- `PUT /clothing/{id}/` - Update item
- `PATCH /clothing/{id}/` - Partial update
- `DELETE /clothing/{id}/` - Delete item

---

## Real Examples from Our Project

### Authentication Views

```python
@extend_schema(tags=['Authentication'])
class UserRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

@extend_schema(tags=['Authentication'])
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
```

### Wardrobe Views

```python
class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
```

---

## Custom Actions in ViewSets

Add custom endpoints to ViewSets:

```python
from rest_framework.decorators import action
from rest_framework.response import Response

class ClothingItemViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=True, methods=['post'])
    def mark_as_worn(self, request, pk=None):
        """Mark an item as worn"""
        item = self.get_object()
        item.wear_count += 1
        item.save()
        return Response({'message': 'Item marked as worn'})
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get user's clothing statistics"""
        total_items = self.get_queryset().count()
        return Response({
            'total_items': total_items,
            'total_worn': self.get_queryset().aggregate(Sum('wear_count'))['wear_count__sum'] or 0
        })
```

**This creates these additional URLs:**
- `POST /clothing/{id}/mark_as_worn/` - Mark item as worn
- `GET /clothing/statistics/` - Get statistics

---

## DRF Mixins

Mixins provide reusable functionality:

```python
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import GenericAPIView

class ClothingItemListCreateView(ListModelMixin, CreateModelMixin, GenericAPIView):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
```

---

## DRF Settings

Configure DRF in your Django settings:

```python
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
```

---

## Best Practices

1. **Use ViewSets for CRUD operations**
2. **Use Generic Views for simple cases**
3. **Use APIView for complex custom logic**
4. **Add custom actions for specific operations**
5. **Use routers for automatic URL generation**

---

## Practice Exercise

1. Look at the ViewSets in `apps/wardrobe/views.py`
2. Create a new ViewSet for a different model
3. Add custom actions to your ViewSet
4. Test the API endpoints

---

## Next Steps

- [JWT Authentication](./jwt-authentication.md) - Securing your APIs
- [Swagger Documentation](./swagger-drf-spectacular.md) - API documentation

---