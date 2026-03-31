from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer, UserRatingStatsSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        target_user_id = self.request.query_params.get('target_user')
        if target_user_id:
            return Review.objects.filter(target_user_id=target_user_id)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

@api_view(['GET'])
def user_rating_stats(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    reviews = Review.objects.filter(target_user=user)
    stats = reviews.aggregate(Avg('rating'))
    avg = stats['rating__avg'] or 0.0
    data = {
        'target_user_id': user.id,
        'average_rating': round(avg, 1),
        'total_reviews': reviews.count()
    }
    return Response(data)
