from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ClothingCategory, ClothingItem, ClothingImage, AIAnalysis
from .serializers import (
    ClothingCategorySerializer, ClothingItemSerializer, ClothingItemCreateSerializer,
    ClothingItemListSerializer, ClothingImageSerializer, AIAnalysisSerializer
)
from .tasks import analyze_clothing_item
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Wardrobe'])
class ClothingCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClothingCategory.objects.all()
    serializer_class = ClothingCategorySerializer
    permission_classes = [IsAuthenticated]

@extend_schema(tags=['Wardrobe'])
class ClothingItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'brand', 'color', 'size', 'ai_analysis_status', 'is_active']
    search_fields = ['name', 'brand', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name', 'wear_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ClothingItem.objects.filter(user=self.request.user, is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ClothingItemCreateSerializer
        elif self.action == 'list':
            return ClothingItemListSerializer
        return ClothingItemSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        item = self.get_object()
        if item.ai_analysis_status == 'pending':
            analyze_clothing_item.delay(str(item.id))
            return Response({'message': 'Analysis started'}, status=status.HTTP_202_ACCEPTED)
        return Response({'message': 'Analysis already in progress or completed'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        stats = {
            'total_items': queryset.count(),
            'by_category': {},
            'by_status': {},
            'total_wear_count': sum(item.wear_count for item in queryset),
        }
        
        for item in queryset:
            category = item.category.name if item.category else 'Uncategorized'
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            stats['by_status'][item.ai_analysis_status] = stats['by_status'].get(item.ai_analysis_status, 0) + 1
        
        return Response(stats)

@extend_schema(tags=['Wardrobe'])
class ClothingImageViewSet(viewsets.ModelViewSet):
    serializer_class = ClothingImageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ClothingImage.objects.filter(clothing_item__user=self.request.user)
    
    def perform_create(self, serializer):
        # TODO: Add image processing logic here
        serializer.save()

@extend_schema(tags=['AI Analysis'])
class AIAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AIAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIAnalysis.objects.filter(clothing_item__user=self.request.user) 