# Django URLs and Views

## 🎯 What You'll Learn

In this module, you'll learn how Django handles web requests through URLs and views. You'll understand the difference between function-based and class-based views, and how Django REST Framework extends these concepts for building APIs.

## 🌐 How Django Handles Web Requests

When someone visits your website, Django follows this process:

1. **URL Pattern Matching**: Django looks at the URL and finds which view should handle it
2. **View Processing**: The view function/class processes the request
3. **Response**: Django sends back a response (HTML, JSON, etc.)

```
User visits /api/clothing/ → URL Router → View Function → Response
```

## 🗺️ URL Configuration

### Main URL Configuration

In `vestaire/urls.py` (the main URL file):

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/wardrobe/', include('apps.wardrobe.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### App-Specific URLs

Each Django app has its own `urls.py` file. For example, `apps/authentication/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.login_view, name='user-login'),
    path('logout/', views.logout_view, name='user-logout'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('user-info/', views.user_info_view, name='user-info'),
    path('change-password/', views.change_password_view, name='change-password'),
]
```

### URL Patterns Explained

```python
path('login/', views.login_view, name='user-login')
#     ↑        ↑                    ↑
#   URL path   View function      URL name
```

- **URL path**: What the user types in the browser
- **View function**: The function that handles the request
- **URL name**: A name you can use to reference this URL in your code

## 👁️ Understanding Views

Views are Python functions or classes that handle web requests and return responses.

### Function-Based Views (FBVs)

Simple views written as functions:

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def simple_view(request):
    """A simple function-based view"""
    return JsonResponse({'message': 'Hello, World!'})

@csrf_exempt
def clothing_list_view(request):
    """Get all clothing items for a user"""
    if request.method == 'GET':
        items = ClothingItem.objects.filter(user=request.user)
        data = [{'id': item.id, 'name': item.name} for item in items]
        return JsonResponse({'items': data})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
```

### Class-Based Views (CBVs)

More powerful views written as classes:

```python
from django.views import View
from django.http import JsonResponse

class ClothingListView(View):
    """A class-based view for listing clothing items"""

    def get(self, request):
        """Handle GET requests"""
        items = ClothingItem.objects.filter(user=request.user)
        data = [{'id': item.id, 'name': item.name} for item in items]
        return JsonResponse({'items': data})

    def post(self, request):
        """Handle POST requests"""
        # Create new clothing item
        name = request.POST.get('name')
        item = ClothingItem.objects.create(user=request.user, name=name)
        return JsonResponse({'id': item.id, 'name': item.name})
```

## 🎯 Real Examples from Our Project

### Authentication Views

From `apps/authentication/views.py`:

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

From `apps/wardrobe/views.py`:

```python
class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only show items belonging to the current user"""
        return ClothingItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the user when creating an item"""
        serializer.save(user=self.request.user)
```

## 🔧 URL Parameters and Path Variables

### Capturing URL Parameters

```python
# In urls.py
path('clothing/<int:item_id>/', views.clothing_detail_view, name='clothing-detail'),

# In views.py
def clothing_detail_view(request, item_id):
    """Get details of a specific clothing item"""
    try:
        item = ClothingItem.objects.get(id=item_id, user=request.user)
        return JsonResponse({
            'id': item.id,
            'name': item.name,
            'brand': item.brand,
            'color': item.color
        })
    except ClothingItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
```

### Query Parameters

```python
def clothing_list_view(request):
    """Get clothing items with optional filtering"""
    items = ClothingItem.objects.filter(user=request.user)

    # Filter by color if provided
    color = request.GET.get('color')
    if color:
        items = items.filter(color=color)

    # Filter by brand if provided
    brand = request.GET.get('brand')
    if brand:
        items = items.filter(brand=brand)

    data = [{'id': item.id, 'name': item.name} for item in items]
    return JsonResponse({'items': data})
```

## 🛡️ Request Methods and HTTP Verbs

Django views can handle different HTTP methods:

```python
class ClothingItemView(View):

    def get(self, request, item_id):
        """GET /clothing/123/ - Retrieve an item"""
        # Get item details
        pass

    def post(self, request):
        """POST /clothing/ - Create a new item"""
        # Create new item
        pass

    def put(self, request, item_id):
        """PUT /clothing/123/ - Update an entire item"""
        # Update item
        pass

    def patch(self, request, item_id):
        """PATCH /clothing/123/ - Update part of an item"""
        # Partial update
        pass

    def delete(self, request, item_id):
        """DELETE /clothing/123/ - Delete an item"""
        # Delete item
        pass
```

## 🎨 Django REST Framework Views

DRF provides powerful views for building APIs:

### APIView

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

### ViewSets

ViewSets combine common operations:

```python
from rest_framework import viewsets

class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()
```

### Generic Views

DRF provides generic views for common patterns:

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

## 🔗 URL Routing with DRF

### Using Routers

DRF routers automatically create URL patterns for ViewSets:

```python
# In urls.py
from rest_framework.routers import DefaultRouter
from .views import ClothingItemViewSet

router = DefaultRouter()
router.register(r'clothing', ClothingItemViewSet, basename='clothing')

urlpatterns = [
    path('', include(router.urls)),
]

# This creates these URLs automatically:
# GET    /clothing/          - List all items
# POST   /clothing/          - Create new item
# GET    /clothing/{id}/     - Get specific item
# PUT    /clothing/{id}/     - Update item
# PATCH  /clothing/{id}/     - Partial update
# DELETE /clothing/{id}/     - Delete item
```

### Custom Actions

Add custom actions to ViewSets:

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
        total_worn = self.get_queryset().aggregate(Sum('wear_count'))['wear_count__sum'] or 0
        return Response({
            'total_items': total_items,
            'total_worn': total_worn
        })
```

## 🎯 Best Practices

### 1. Use Meaningful URL Names

```python
# Good
path('clothing/<int:item_id>/', views.clothing_detail, name='clothing-detail'),

# Use in templates or code
from django.urls import reverse
url = reverse('clothing-detail', args=[item.id])
```

### 2. Handle Errors Gracefully

```python
def clothing_detail_view(request, item_id):
    try:
        item = ClothingItem.objects.get(id=item_id, user=request.user)
        return JsonResponse({'item': item.to_dict()})
    except ClothingItem.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'Server error'}, status=500)
```

### 3. Use Appropriate HTTP Status Codes

```python
from rest_framework import status

# Success responses
return Response(data, status=status.HTTP_200_OK)      # OK
return Response(data, status=status.HTTP_201_CREATED) # Created
return Response(data, status=status.HTTP_204_NO_CONTENT) # No content

# Error responses
return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
```

### 4. Validate Request Data

```python
def create_clothing_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)

        # Create the item
        item = ClothingItem.objects.create(
            user=request.user,
            name=name
        )
        return JsonResponse({'id': item.id, 'name': item.name})
```

## 📝 Practice Exercise

1. Look at the URL patterns in `apps/authentication/urls.py` and `apps/wardrobe/urls.py`
2. Try creating a simple view that returns a list of clothing categories
3. Add a URL pattern for your new view
4. Test it by visiting the URL in your browser

## 🔗 Next Steps

Now that you understand URLs and views, learn about:

- [Django Serializers](./django-serializers.md) - Converting data to/from JSON
- [DRF Basics](./drf-basics.md) - Building REST APIs

## 📚 Additional Resources

- [Django URL Documentation](https://docs.djangoproject.com/en/stable/topics/http/urls/)
- [Django Views Documentation](https://docs.djangoproject.com/en/stable/topics/http/views/)
- [DRF Views Documentation](https://www.django-rest-framework.org/api-guide/views/)
- [DRF Routers Documentation](https://www.django-rest-framework.org/api-guide/routers/)

---

**Ready to work with data?** Learn about serializers in [Django Serializers](./django-serializers.md).
