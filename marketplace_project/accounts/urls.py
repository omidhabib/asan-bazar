from django.urls import path
from .views import RegisterView, LoginView, LogoutView, EditProfileView, SendOTPAPIView, VerifyOTPAPIView, AdminVerifyUserAPIView, ToggleFollowView, UserProfileRedirectView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileRedirectView.as_view(), name='profile'),
    path('edit-profile/', EditProfileView.as_view(), name='edit_profile'),
    path('api/send-otp/', SendOTPAPIView.as_view(), name='api_send_otp'),
    path('api/verify-otp/', VerifyOTPAPIView.as_view(), name='api_verify_otp'),
    path('api/admin/verify-user/', AdminVerifyUserAPIView.as_view(), name='api_admin_verify_user'),
    path('api/toggle-follow/<int:pk>/', ToggleFollowView.as_view(), name='toggle_follow'),
]
