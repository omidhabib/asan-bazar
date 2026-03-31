from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet, user_rating_stats

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:user_id>/rating-stats/', user_rating_stats, name='user_rating_stats'),
]
