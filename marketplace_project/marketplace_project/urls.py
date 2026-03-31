from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# Customize admin site
admin.site.site_header = "Asan Bazar Administration"
admin.site.site_title = "Asan Bazar Admin"
admin.site.index_title = "Welcome to Asan Bazar Admin Panel"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')), # For language switcher
]

urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('ads.urls')),
    path('', include('chat.urls')),
    path('api/', include('reviews.urls')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
