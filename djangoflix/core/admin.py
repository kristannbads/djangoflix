"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.admin import GenericTabularInline

from core import models
from core.db.models import PlaylistTypeChoices


class TaggedItemInline(GenericTabularInline):
    model = models.TaggedItem
    extra = 0


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
    inlines = [TaggedItemInline]
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


admin.site.register(models.VideoPublishedProxy, VideoPublishedProxyAdmin)


class MovieProxyAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline]
    fields = ["title", "description", "state", "category", "video", "slug"]
    list_display = ["title"]

    class Meta:
        model = models.MovieProxy

    def get_queryset(self, request):
        return models.MovieProxy.objects.all()


admin.site.register(models.MovieProxy, MovieProxyAdmin)


class SeasonEpisodeInline(admin.TabularInline):
    model = models.PlaylistItem
    extra = 0


class TVShowSeasonProxyAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline, SeasonEpisodeInline]
    fields = ["title", "description", "category", "slug", "state", "active"]
    list_display = ["title", "parent"]
    readonly_fields = ["parent"]

    class Meta:
        model = models.TVShowSeasonProxy

    def get_queryset(self, request):
        return models.TVShowSeasonProxy.objects.all()


admin.site.register(models.TVShowSeasonProxy, TVShowSeasonProxyAdmin)


class TVShowSeasonProxyInline(admin.TabularInline):
    model = models.TVShowSeasonProxy
    extra = 0
    fields = ["order", "title", "state"]


class TVShowProxyAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline, TVShowSeasonProxyInline]
    fields = ["title", "description", "state", "category", "video", "slug"]
    list_display = ["title"]

    class Meta:
        model = models.TVShowProxy

    def get_queryset(self, request):
        return models.TVShowProxy.objects.all()


admin.site.register(models.TVShowProxy, TVShowProxyAdmin)


class PlaylistItemInline(admin.TabularInline):
    model = models.PlaylistItem
    extra = 0


class PlaylistAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline, PlaylistItemInline]
    fields = ["title", "description", "type", "slug", "state", "active"]

    class Meta:
        model = models.Playlist

    def get_queryset(self, request):
        return models.Playlist.objects.filter(
            type=PlaylistTypeChoices.PLAYLIST
        )


admin.site.register(models.Playlist, PlaylistAdmin)

admin.site.register(models.Category)


class TaggedItemAdmin(admin.ModelAdmin):
    fields = ["tag", "content_type", "object_id", "content_object"]
    readonly_fields = ["content_object"]

    class Meta:
        model = models.TaggedItem


admin.site.register(models.TaggedItem, TaggedItemAdmin)
