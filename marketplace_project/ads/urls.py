from django.urls import path
from .views import (
    HomeView, AdDetailView, CreateAdView, CategoryAdsView,
    ToggleFavoriteView, InfiniteScrollAdsView, LiveSearchView,
    UserProfileView, FavoritesListView, FollowingAdsView, UpdateAdView, DeleteAdView,
    AddCommentView, AdMapListView, NearbyAdsView, MapPageView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('ad/<int:pk>/', AdDetailView.as_view(), name='ad_detail'),
    path('ad/<int:pk>/edit/', UpdateAdView.as_view(), name='edit_ad'),
    path('ad/<int:pk>/delete/', DeleteAdView.as_view(), name='delete_ad'),
    path('post-ad/', CreateAdView.as_view(), name='post_ad'),
    path('ad/<int:pk>/comment/', AddCommentView.as_view(), name='add_comment'),
    path('category/<slug:slug>/', CategoryAdsView.as_view(), name='category_ads'),
    path('favorites/', FavoritesListView.as_view(), name='favorites'),
    path('following/', FollowingAdsView.as_view(), name='following'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    # AJAX / API endpoints
    path('api/toggle-favorite/<int:pk>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('api/ads/', InfiniteScrollAdsView.as_view(), name='infinite_ads'),
    path('api/search/', LiveSearchView.as_view(), name='live_search'),
    path('products/map/', MapPageView.as_view(), name='product_map'),
    path('api/products/map/', AdMapListView.as_view(), name='api_product_map'),
    path('products/nearby/', NearbyAdsView.as_view(), name='nearby_products'),
]
