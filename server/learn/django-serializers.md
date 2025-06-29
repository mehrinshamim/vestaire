# Django Serializers

## 🎯 What You'll Learn

- What serializers are and why they're important
- How to convert Django models to JSON and vice versa
- Validation and data transformation
- Nested serializers and relationships

---

## What are Serializers?

Serializers convert complex data types (like Django models) to and from JSON. They're essential for building APIs.

**Why we need them:**
- Convert model instances to JSON for API responses
- Convert JSON data to model instances for saving
- Validate incoming data
- Handle nested relationships

---

## Basic Serializers

### Simple Serializer

```python
from rest_framework import serializers
from .models import ClothingItem

class ClothingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'brand', 'color', 'size', 'price']
```

### Using the Serializer

```python
# Convert model to JSON
item = ClothingItem.objects.get(id=1)
serializer = ClothingItemSerializer(item)
json_data = serializer.data
# Result: {'id': 1, 'name': 'Blue T-Shirt', 'brand': 'Nike', ...}

# Convert JSON to model
json_data = {'name': 'Red Shirt', 'brand': 'Adidas', 'color': 'Red'}
serializer = ClothingItemSerializer(data=json_data)
if serializer.is_valid():
    item = serializer.save()
```

---

## Field Types and Options

### Common Field Types

```python
class ClothingItemSerializer(serializers.ModelSerializer):
    # Basic fields
    name = serializers.CharField(max_length=200)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_active = serializers.BooleanField(default=True)
    
    # Read-only fields
    created_at = serializers.DateTimeField(read_only=True)
    
    # Custom fields
    full_name = serializers.SerializerMethodField()
    
    def get_full_name(self, obj):
        return f"{obj.brand} {obj.name}"
    
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'brand', 'price', 'is_active', 'created_at', 'full_name']
```

### Field Options

```python
class ClothingItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=200,
        required=True,
        help_text="Enter the item name"
    )
    price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'price']
```

---

## Validation

### Built-in Validation

```python
class ClothingItemSerializer(serializers.ModelSerializer):
    def validate_name(self, value):
        """Custom validation for name field"""
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long")
        return value
    
    def validate_price(self, value):
        """Custom validation for price field"""
        if value and value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate(self, data):
        """Validate multiple fields together"""
        if data.get('brand') == 'Nike' and data.get('price', 0) < 50:
            raise serializers.ValidationError("Nike items must cost at least $50")
        return data
    
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'brand', 'price']
```

### Using Validators

```python
from rest_framework.validators import UniqueValidator

class ClothingItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[UniqueValidator(queryset=ClothingItem.objects.all())]
    )
    
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'brand']
```

---

## Nested Serializers

### Foreign Key Relationships

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ClothingItemSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Read-only nested serializer
    
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'brand', 'user']
```

### Many-to-Many Relationships

```python
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ClothingItemSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'brand', 'tags']
```

---

## Real Examples from Our Project

### User Registration Serializer

```python
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

### Clothing Item Serializer

```python
class ClothingItemSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = ClothingItem
        fields = [
            'id', 'name', 'user', 'category', 'category_name',
            'brand', 'color', 'size', 'material', 'pattern',
            'price', 'purchase_date', 'purchase_location',
            'description', 'ai_analysis_status', 'wear_count',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
```

### User Profile Serializer

```python
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'bio', 'preferences', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
```

---

## Advanced Serializer Features

### SerializerMethodField

```python
class ClothingItemSerializer(serializers.ModelSerializer):
    image_count = serializers.SerializerMethodField()
    last_worn = serializers.SerializerMethodField()
    
    def get_image_count(self, obj):
        return obj.images.count()
    
    def get_last_worn(self, obj):
        # Custom logic to get last worn date
        return obj.last_worn_date if hasattr(obj, 'last_worn_date') else None
    
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'image_count', 'last_worn']
```

### Custom Create/Update Methods

```python
class ClothingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingItem
        fields = ['id', 'name', 'brand', 'user']
    
    def create(self, validated_data):
        # Custom logic when creating
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Custom logic when updating
        instance.name = validated_data.get('name', instance.name)
        instance.brand = validated_data.get('brand', instance.brand)
        instance.save()
        return instance
```

---

## Using Serializers in Views

### In APIView

```python
class ClothingItemAPIView(APIView):
    def get(self, request):
        items = ClothingItem.objects.filter(user=request.user)
        serializer = ClothingItemSerializer(items, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ClothingItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

### In ViewSet

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

## Best Practices

1. **Use ModelSerializer for simple cases**
2. **Validate data thoroughly**
3. **Handle nested relationships carefully**
4. **Use read_only_fields for computed data**
5. **Keep serializers focused and simple**

---

## Practice Exercise

1. Look at the serializers in `apps/authentication/serializers.py`
2. Create a new serializer for a different model
3. Add custom validation to your serializer
4. Test it by creating and updating objects

---

## Next Steps

- [DRF Basics](./drf-basics.md) - Building REST APIs
- [JWT Authentication](./jwt-authentication.md) - Securing your APIs

---