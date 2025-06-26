from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClothingCategoryViewSet, ClothingItemViewSet, 
    ClothingImageViewSet, AIAnalysisViewSet
)

app_name = 'wardrobe'

router = DefaultRouter()
router.register(r'categories', ClothingCategoryViewSet, basename='category')
router.register(r'items', ClothingItemViewSet, basename='item')
router.register(r'images', ClothingImageViewSet, basename='image')
router.register(r'analysis', AIAnalysisViewSet, basename='analysis')

urlpatterns = [
    path('', include(router.urls)),
] 