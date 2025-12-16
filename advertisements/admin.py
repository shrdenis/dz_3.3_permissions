from django.contrib import admin

from advertisements.models import Advertisement, Favorite


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "status", "creator", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "description")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "advertisement", "created_at")
    list_filter = ("created_at",)
