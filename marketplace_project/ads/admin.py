from django.contrib import admin
from .models import Category, Ad, Favorite

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'location', 'is_active', 'created_at', 'user']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'description', 'location', 'phone_number']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'ad', 'created_at']
    list_filter = ['created_at']
