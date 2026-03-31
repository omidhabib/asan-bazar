from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from .forms import UserRegisterForm, UserLoginForm, EditProfileForm
from .models import User


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserRegisterForm()
        return render(request, 'register.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful. You can now login.')
            return redirect('login')
        return render(request, 'register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserLoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            print(f"DEBUG LOGIN: phone={phone_number}, pass={password}")
            user = authenticate(request, phone_number=phone_number, password=password)
            print(f"DEBUG LOGIN RESULT: {user}")
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.full_name}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid phone number or password.')
        return render(request, 'login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('home')


class EditProfileView(LoginRequiredMixin, View):
    """Allow users to edit their profile photo and full name."""

    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, 'edit_profile.html', {'form': form})

    def post(self, request):
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile', pk=request.user.pk)
        return render(request, 'edit_profile.html', {'form': form})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import SendOTPSerializer, VerifyOTPSerializer, AdminVerifyUserSerializer
from .models import OTP, UserFollow

class SendOTPAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            # Ensure users can only send OTP to their own phone
            if request.user.phone_number != phone_number:
                return Response({'error': 'You can only request OTP for your own phone number.'}, status=status.HTTP_403_FORBIDDEN)
            
            otp = OTP.generate_otp(phone_number)
            # In a real app, send `otp.code` via SMS here
            print(f"OTP for {phone_number} is {otp.code}")
            return Response({'message': 'OTP sent successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            
            if request.user.phone_number != phone_number:
                return Response({'error': 'Invalid phone number.'}, status=status.HTTP_403_FORBIDDEN)

            try:
                otp = OTP.objects.get(phone_number=phone_number, code=code, is_used=False)
                if otp.is_valid():
                    otp.is_used = True
                    otp.save()
                    
                    user = request.user
                    user.is_verified = True
                    user.save()
                    
                    return Response({'message': 'Phone number verified successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'OTP is expired or invalid.'}, status=status.HTTP_400_BAD_REQUEST)
            except OTP.DoesNotExist:
                return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminVerifyUserAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = AdminVerifyUserSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            is_verified = serializer.validated_data['is_verified']
            
            try:
                user = User.objects.get(pk=user_id)
                user.is_verified = is_verified
                user.save()
                status_text = "verified" if is_verified else "unverified"
                return Response({'message': f'User {user.full_name} is now {status_text}.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ToggleFollowView(LoginRequiredMixin, View):
    """AJAX endpoint — toggle follow on a user."""
    def post(self, request, pk):
        user_to_follow = get_object_or_404(User, pk=pk)
        if user_to_follow == request.user:
            return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)
        
        follow, created = UserFollow.objects.get_or_create(follower=request.user, followed=user_to_follow)
        if not created:
            follow.delete()
            is_following = False
        else:
            is_following = True
        return JsonResponse({
            'is_following': is_following,
            'count': user_to_follow.followers.count(),
        })


class UserProfileRedirectView(LoginRequiredMixin, View):
    """Redirect to the current user's profile."""
    def get(self, request):
        return redirect('user_profile', pk=request.user.pk)
