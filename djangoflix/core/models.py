"""
Database models.
"""

from django.utils import timezone
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation

from core.db.models import PublishStateOptions, PlaylistTypeChoices
from core.db.receivers import slugify_pre_save, publish_state_pre_save


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"


class Video(models.Model):
    """Video object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=None,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video_id = models.CharField(max_length=210, unique=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(
        max_length=2,
        choices=PublishStateOptions.choices,
        default=PublishStateOptions.DRAFT,
    )
    published_timestamp = models.DateTimeField(
        auto_now_add=False, auto_now=False, blank=True, null=True
    )

    @property
    def is_published(self):
        return self.active

    def get_playlist_ids(self):

        playlists = self.playlist_item.all()
        if playlists.exists():

            return list(self.playlist_item.all().values_list("id", flat=True))
        else:
            return []

    def __str__(self):
        return self.title


class VideoAllProxy(Video):
    class Meta:
        proxy = True
        verbose_name = "All Video"
        verbose_name_plural = "All Videos"


class VideoPublishedProxy(Video):
    class Meta:
        proxy = True
        verbose_name = "Published Video"
        verbose_name_plural = "Published Videos"


pre_save.connect(publish_state_pre_save, sender=Video)
pre_save.connect(slugify_pre_save, sender=Video)


class TaggedItem(models.Model):
    """Tag object"""

    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    
    def __str__(self):
        return self.tag
    
   
class Category(models.Model):
    """Category object"""

    title = models.CharField(max_length=220)
    slug = models.SlugField(blank=True, null=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class PlaylistQuerySet(models.QuerySet):
    """Query set for Playlist Model"""

    def published(self):
        now = timezone.now()
        return self.filter(
            state=PublishStateOptions.PUBLISH, publish_timestamp__lte=now
        )


class PlaylistManager(models.Manager):
    """Manager for Playlist Model"""

    def get_queryset(self):
        return PlaylistQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()


class Playlist(models.Model):
    """Playlist object"""

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(
        Category, blank=True, null=True, on_delete=models.SET_NULL
    )
    order = models.IntegerField(default=1)
    title = models.CharField(max_length=255)
    type = models.CharField(
        max_length=3,
        choices=PlaylistTypeChoices.choices,
        default=PlaylistTypeChoices.PLAYLIST,
    )
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    video = models.ForeignKey(
        Video,
        related_name="playlist_featured",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    videos = models.ManyToManyField(
        Video,
        related_name="playlist_item",
        blank=True,
        through="PlaylistItem",
    )
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state = models.CharField(
        max_length=2,
        choices=PublishStateOptions.choices,
        default=PublishStateOptions.DRAFT,
    )
    published_timestamp = models.DateTimeField(
        auto_now_add=False, auto_now=False, blank=True, null=True
    )
    tags = GenericRelation(TaggedItem, related_query_name="playlist")

    objects = PlaylistManager()

    @property
    def is_published(self):
        return self.active

    def __str__(self):
        return self.title


class PlaylistItem(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-timestamp"]


pre_save.connect(publish_state_pre_save, sender=Playlist)
pre_save.connect(slugify_pre_save, sender=Playlist)


class MovieProxyManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(
            parent__isnull=True,
            type=PlaylistTypeChoices.MOVIE,
        )


class MovieProxy(Playlist):

    objects = MovieProxyManager()

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = PlaylistTypeChoices.MOVIE
        super().save(*args, **kwargs)


class TVShowProxyManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(
            parent__isnull=True,
            type=PlaylistTypeChoices.SHOW,
        )


class TVShowProxy(Playlist):

    objects = TVShowProxyManager()

    class Meta:
        verbose_name = "TV Show"
        verbose_name_plural = "TV Shows"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = PlaylistTypeChoices.SHOW
        super().save(*args, **kwargs)


class TVShowSeasonProxyManager(models.Manager):
    def all(self):
        return self.get_queryset().filter(
            parent__isnull=False,
            type=PlaylistTypeChoices.SEASON,
        )


class TVShowSeasonProxy(Playlist):

    objects = TVShowSeasonProxyManager()

    class Meta:
        verbose_name = "Season"
        verbose_name_plural = "Seasons"
        proxy = True

    def save(self, *args, **kwargs):
        self.type = PlaylistTypeChoices.SEASON
        super().save(*args, **kwargs)
