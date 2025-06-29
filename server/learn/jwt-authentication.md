# JWT Authentication

## 🎯 What You'll Learn

- What JWT (JSON Web Tokens) are and how they work
- How to implement JWT authentication in Django REST Framework
- Login, logout, and token refresh endpoints
- Securing your API views

---

## What is JWT Authentication?

JWT (JSON Web Token) is a way to authenticate users without storing session data on the server. Instead, the client stores a token that contains user information.

**How it works:**
1. User logs in with username/password
2. Server validates credentials and returns a JWT token
3. Client includes the token in subsequent requests
4. Server validates the token and identifies the user

---

## JWT Token Structure

A JWT token has three parts:
- **Header**: Algorithm and token type
- **Payload**: User data and expiration time
- **Signature**: Verification signature

Example token:
`eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9eyJ1c2VyX2lkIjoxLCJleHAiOjE2MzQ1Njc4OTB9.signature`


---

## Setting Up JWT in Django

### Installation

```bash
pip install djangorestframework-simplejwt
```

### Settings Configuration

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

---

## JWT Views and Endpoints

### Login Endpoint

```python
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

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

### Logout Endpoint

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Invalid refresh token'
        }, status=status.HTTP_400_BAD_REQUEST)
```

### Token Refresh Endpoint

```python
from rest_framework_simplejwt.views import TokenRefreshView

# This is automatically provided by DRF Simple JWT
# POST /api/token/refresh/
# Body: {"refresh": "your_refresh_token"}
```

---

## Using JWT in Views

### Securing Views

```python
from rest_framework.permissions import IsAuthenticated

class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]  # Requires valid JWT token
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user)
```

### Accessing User Information

```python
class ClothingItemViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingItemSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # request.user is automatically set from JWT token
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        # Filter by authenticated user
        return ClothingItem.objects.filter(user=self.request.user)
```

---

## Real Examples from Our Project

### Authentication Views

```python
@extend_schema(tags=['Authentication'])
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint that returns JWT tokens.
    
    Expected payload:
    {
        "username": "user123",
        "password": "password123"
    }
    """
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
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
```

### User Profile View

```python
@extend_schema(tags=['Authentication'])
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]  # Requires JWT token
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Get the current user's profile, create if doesn't exist."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
```

---

## Making Authenticated Requests

### Using the Access Token

```javascript
// Frontend JavaScript example
const token = 'your_access_token_here';

fetch('/api/wardrobe/clothing/', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Python Requests Example

```python
import requests

token = 'your_access_token_here'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:8000/api/wardrobe/clothing/', headers=headers)
data = response.json()
```

---

## Token Management

### Token Expiration

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # 1 day
}
```

### Refreshing Tokens

```python
# When access token expires, use refresh token to get new one
import requests

refresh_token = 'your_refresh_token_here'
response = requests.post('http://localhost:8000/api/token/refresh/', {
    'refresh': refresh_token
})

new_access_token = response.json()['access']
```

---

## Security Best Practices

1. **Store tokens securely** - Use secure storage (not localStorage)
2. **Use HTTPS** - Always in production
3. **Set appropriate expiration times** - Short access tokens, longer refresh tokens
4. **Implement token blacklisting** - For logout functionality
5. **Validate tokens on every request** - Don't trust client data

---

## Practice Exercise

1. Look at the authentication views in `apps/authentication/views.py`
2. Try logging in using the login endpoint
3. Use the returned token to access a protected endpoint
4. Test the logout functionality

---

## Next Steps

- [Django Auth System](./django-auth-system.md) - Understanding Django's auth system
- [Swagger Documentation](./swagger-drf-spectacular.md) - API documentation

---
