"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ["id"]
    list_display = ["email", "name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    readonly_fields = ["last_login"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)


class VideoAllAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "video_id",
        "state",
        "is_published",
    ]
    search_fields = ["title"]
    list_filter = ["state", "active", "user"]
    readonly_fields = [
        "id",
        "is_published",
        "published_timestamp",
    ]

    class Meta:
        model = models.VideoAllProxy


admin.site.register(models.VideoAllProxy, VideoAllAdmin)


class VideoPublishedProxyAdmin(admin.ModelAdmin):
    list_display = ["title", "video_id"]
    search_fields = ["title"]
    readonly_fields = ["user", "id", "is_published", "published_timestamp"]

    class Meta:
        model = models.VideoPublishedProxy

    def get_queryset(self, request):
        return models.VideoPublishedProxy.objects.filter(active=True)


class PlaylistItemInline(admin.TabularInline):
    model = models.PlaylistItem
    extra = 0


class PlaylistAdmin(admin.ModelAdmin):
    inlines = [PlaylistItemInline]
    fields = ["title", "description", "slug", "state", "active"]

    class Meta:
        model = models.Playlist


admin.site.register(models.VideoPublishedProxy, VideoPublishedProxyAdmin)

admin.site.register(models.Playlist, PlaylistAdmin)
