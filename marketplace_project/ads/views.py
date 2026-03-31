import json
import math
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Ad, Category, Favorite
from .forms import CreateAdForm

User = get_user_model()


class HomeView(ListView):
    model = Ad
    template_name = 'home.html'
    context_object_name = 'ads'
    paginate_by = 12

    def get_queryset(self):
        from django.db.models import Avg, Count
        queryset = Ad.objects.filter(is_active=True).select_related('user', 'category').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-created_at')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query) | Q(city__icontains=query)
            )
        
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__iexact=city)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        # 34 Afghanistan Provinces
        context['afghan_cities'] = [
            "Kabul", "Kandahar", "Herat", "Mazar-i-Sharif", "Jalalabad", "Kunduz", "Ghazni", 
            "Balkh", "Baghlan", "Khost", "Faryab", "Jawzjan", "Helmand", "Nangarhar", 
            "Paktia", "Kunar", "Nuristan", "Laghman", "Panjshir", "Kapisa", "Parwan", 
            "Wardak", "Logar", "Bamyan", "Daikundi", "Ghor", "Uruzgan", "Zabul", 
            "Nimruz", "Farah", "Badghis", "Sar-e Pol", "Samangan", "Takhar", "Badakhshan"
        ]
        if self.request.user.is_authenticated:
            context['user_favorites'] = set(
                Favorite.objects.filter(user=self.request.user).values_list('ad_id', flat=True)
            )
        else:
            context['user_favorites'] = set()
        return context


class CategoryAdsView(ListView):
    model = Ad
    template_name = 'home.html'
    context_object_name = 'ads'
    paginate_by = 12

    def get_queryset(self):
        from django.db.models import Avg, Count
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Ad.objects.filter(category=self.category, is_active=True).select_related('user', 'category').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        if self.request.user.is_authenticated:
            context['user_favorites'] = set(
                Favorite.objects.filter(user=self.request.user).values_list('ad_id', flat=True)
            )
        else:
            context['user_favorites'] = set()
        return context


class AdDetailView(DetailView):
    model = Ad
    template_name = 'ad_detail.html'
    context_object_name = 'ad'

    def get_queryset(self):
        return Ad.objects.filter(is_active=True).select_related('user', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ad = self.get_object()
        context['is_favorited'] = (
            self.request.user.is_authenticated and
            Favorite.objects.filter(user=self.request.user, ad=ad).exists()
        )
        context['favorites_count'] = ad.favorited_by.count()
        
        from reviews.models import Review
        from django.db.models import Avg
        
        # Product Ratings (New Requirement)
        ad_reviews = Review.objects.filter(ad=ad).select_related('reviewer')
        ad_stats = ad_reviews.aggregate(Avg('rating'))
        context['ad_avg_rating'] = round(ad_stats['rating__avg'] or 0.0, 1)
        context['ad_review_count'] = ad_reviews.count()
        context['ad_reviews'] = ad_reviews[:5]

        # Seller Ratings (Keep for sidebar)
        seller_reviews = Review.objects.filter(target_user=ad.user)
        seller_stats = seller_reviews.aggregate(Avg('rating'))
        context['seller_avg_rating'] = round(seller_stats['rating__avg'] or 0.0, 1)
        context['seller_review_count'] = seller_reviews.count()
        context['seller_reviews'] = seller_reviews.select_related('reviewer').order_by('-created_at')[:3]
        
        context['comments'] = ad.comments.select_related('user').all()
        
        return context


class CreateAdView(LoginRequiredMixin, CreateView):
    model = Ad
    form_class = CreateAdForm
    template_name = 'post_ad.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ToggleFavoriteView(View):
    """AJAX endpoint — toggle favorite on an ad."""
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        ad = get_object_or_404(Ad, pk=pk, is_active=True)
        fav, created = Favorite.objects.get_or_create(user=request.user, ad=ad)
        if not created:
            fav.delete()
            is_favorited = False
        else:
            is_favorited = True
        return JsonResponse({
            'is_favorited': is_favorited,
            'count': ad.favorited_by.count(),
        })


class InfiniteScrollAdsView(View):
    """AJAX endpoint — return next page of ads as HTML partials."""
    def get(self, request):
        page = int(request.GET.get('page', 1))
        per_page = 12
        query = request.GET.get('q', '')
        category_slug = request.GET.get('category', '')

        from django.db.models import Avg, Count
        ads = Ad.objects.filter(is_active=True).select_related('user', 'category').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-created_at')
        if query:
            ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category_slug:
            ads = ads.filter(category__slug=category_slug)

        start = (page - 1) * per_page
        end = page * per_page
        ads_page = ads[start:end]
        has_more = ads.count() > end

        if request.user.is_authenticated:
            user_favorites = set(Favorite.objects.filter(user=request.user).values_list('ad_id', flat=True))
        else:
            user_favorites = set()

        html = render_to_string('partials/ad_card.html', {
            'ads': ads_page,
            'user_favorites': user_favorites,
            'request': request,
        })
        return JsonResponse({'html': html, 'has_more': has_more})


class LiveSearchView(View):
    """AJAX live search — return top 6 results as JSON."""
    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = []
        if len(query) >= 2:
            ads = Ad.objects.filter(
                is_active=True
            ).filter(
                Q(title__icontains=query) | Q(location__icontains=query)
            ).select_related('category')[:6]
            results = [{
                'id': ad.pk,
                'title': ad.title,
                'price': str(ad.price),
                'location': ad.location,
                'image': ad.image.url if ad.image else '',
                'url': f'/ad/{ad.pk}/',
            } for ad in ads]
        return JsonResponse({'results': results})


class UserProfileView(View):
    """Public user profile page."""
    def get(self, request, pk):
        profile_user = get_object_or_404(User, pk=pk)
        ads = Ad.objects.filter(user=profile_user, is_active=True).order_by('-created_at')
        from reviews.models import Review
        from django.db.models import Avg
        user_reviews = Review.objects.filter(target_user=profile_user).select_related('reviewer')
        rating_stats = user_reviews.aggregate(Avg('rating'))
        avg_rating = rating_stats['rating__avg'] or 0.0
        
        # Follow information
        from accounts.models import UserFollow
        followers_count = UserFollow.objects.filter(followed=profile_user).count()
        following_count = UserFollow.objects.filter(follower=profile_user).count()
        
        is_following = False
        if request.user.is_authenticated:
            is_following = UserFollow.objects.filter(follower=request.user, followed=profile_user).exists()
        
        return render(request, 'profile.html', {
            'profile_user': profile_user,
            'ads': ads,
            'ad_count': ads.count(),
            'reviews': user_reviews,
            'avg_rating': round(avg_rating, 1),
            'review_count': user_reviews.count(),
            'is_following': is_following,
            'followers_count': followers_count,
            'following_count': following_count,
        })

class FollowingAdsView(LoginRequiredMixin, ListView):
    """Show users that the current user is following."""
    template_name = 'following.html'
    context_object_name = 'following_users'
    paginate_by = 12

    def get_queryset(self):
        """Get all users that the current user is following."""
        from accounts.models import UserFollow
        return UserFollow.objects.filter(follower=self.request.user).select_related('followed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Following'
        return context

class FavoritesListView(LoginRequiredMixin, ListView):
    """Show all ads the user has favorited."""
    model = Ad
    template_name = 'favorites.html'
    context_object_name = 'ads'
    paginate_by = 12

    def get_queryset(self):
        favorites = Favorite.objects.filter(user=self.request.user).select_related('ad', 'ad__user', 'ad__category')
        return [f.ad for f in favorites]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class UpdateAdView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ad
    form_class = CreateAdForm
    template_name = 'edit_ad.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user

    def get_success_url(self):
        return reverse_lazy('ad_detail', kwargs={'pk': self.object.pk})


class DeleteAdView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ad
    template_name = 'ad_confirm_delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.user

class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ad = get_object_or_404(Ad, pk=pk, is_active=True)
        text = request.POST.get('text', '').strip()
        if text:
            from .models import AdComment
            AdComment.objects.create(ad=ad, user=request.user, text=text)
        return redirect('ad_detail', pk=pk)

class AdMapListView(View):
    """Return all active ads with coordinates for map markers."""
    def get(self, request):
        ads = Ad.objects.filter(is_active=True, latitude__isnull=False, longitude__isnull=False)
        data = [{
            'id': ad.pk,
            'title': ad.title,
            'price': str(ad.price),
            'lat': float(ad.latitude),
            'lng': float(ad.longitude),
            'url': f'/ad/{ad.pk}/',
        } for ad in ads]
        return JsonResponse(data, safe=False)


class NearbyAdsView(View):
    """Return ads within a certain radius (km) of a given lat/lng."""
    def get(self, request):
        try:
            lat = float(request.GET.get('lat'))
            lng = float(request.GET.get('lng'))
            radius = float(request.GET.get('radius', 10))  # Default 10km
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid lat, lng, or radius'}, status=400)

        # Basic bounding box approximation
        # 1 degree lat is approx 111km
        lat_delta = radius / 111.0
        # 1 degree lng is approx 111km * cos(lat)
        lng_delta = radius / (111.0 * math.cos(math.radians(lat)))

        ads = Ad.objects.filter(
            is_active=True,
            latitude__range=(lat - lat_delta, lat + lat_delta),
            longitude__range=(lng - lng_delta, lng + lng_delta)
        ).select_related('category', 'user')

        results = [{
            'id': ad.pk,
            'title': ad.title,
            'price': str(ad.price),
            'location': ad.location,
            'image': ad.image.url if ad.image else '',
            'url': f'/ad/{ad.pk}/',
        } for ad in ads]

        return JsonResponse(results, safe=False)


class MapPageView(ListView):
    """Render the main map page."""
    model = Ad
    template_name = 'map_view.html'
    context_object_name = 'ads'
