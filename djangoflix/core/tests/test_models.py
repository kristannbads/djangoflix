"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from django.utils.text import slugify

from core.models import Playlist, Video
from core.db.models import PublishStateOptions


def create_user(email="user@example.com", password="testpass123"):
    """Create a return a new user."""
    return get_user_model().objects.create_user(email, password)


def create_video(user, **kwargs):
    """Create and return a sample video."""
    defaults = {
        "title": "One more chance",
        "description": "Love story",
        "state": PublishStateOptions.DRAFT,
    }
    defaults.update(kwargs)

    videos = Video.objects.create(user=user, **defaults)

    return videos


def create_playlist(**kwargs):
    """Create and return a sample playlist."""
    defaults = {
        "title": "Action",
        "description": "sample desc",
        "state": PublishStateOptions.DRAFT,
    }
    defaults.update(kwargs)

    playlists = Playlist.objects.create(**defaults)

    return playlists


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.com", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123",
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


class ModelVideoTests(TestCase):
    """Test Video model."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="test123",
        )
        self.client.force_authenticate(self.user)

    def test_create_video(self):
        """Test creating a video is successful."""

        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )

        video = Video.objects.create(
            user=user, title="Sample Video", description="Sample desc"
        )

        self.assertEqual(str(video), video.title)

    def test_valid_title(self):
        """Test matching title."""
        create_video(user=self.user)
        title = "One more chance"
        queryset = Video.objects.filter(title=title)
        self.assertTrue(queryset.exists())

    def test_slug_field(self):
        video = create_video(user=self.user, video_id="video123")
        title = video.title
        test_slug = slugify(title)
        self.assertEqual(test_slug, video.slug)


class ModelPlaylistTests(TestCase):
    """Test Playlist model."""

    def create_show_with_seasons(self):
        """Test creating a playlist with parent."""
        the_office = Playlist.objects.create(title="The Office Series")
        Playlist.objects.create(
            title="The Office Series Season 1",
            parent=the_office,
            order=1,
        )
        Playlist.objects.create(
            title="The Office Series Season 2",
            parent=the_office,
            order=2,
        )
        Playlist.objects.create(
            title="The Office Series Season 3",
            parent=the_office,
            order=3,
        )
        self.show = the_office

    def setUp(self):
        self.client = APIClient()

        self.user = create_user(
            email="user@example.com",
            password="test123",
        )
        self.video_a = Video.objects.create(
            user=self.user, title="My title", video_id="abc123"
        )
        self.video_b = Video.objects.create(
            user=self.user, title="My title B", video_id="abc1234"
        )
        self.client.force_authenticate(self.user)
        self.create_show_with_seasons()

    def test_create_playlist(self):
        """Test creating a playlist is successful."""

        user = get_user_model().objects.create_user(
            "test@example.com",
            "testpass123",
        )
        video = Video.objects.create(
            user=user, title="Sample Video", description="Sample desc"
        )
        playlist = Playlist.objects.create(
            title="Sample Playlist", description="Sample desc", video=video
        )

        self.assertEqual(str(playlist), playlist.title)

    def test_show_has_seasons(self):
        """Test show it show has seasons."""

        seasons = self.show.playlist_set.all()
        self.assertTrue(seasons.exists())
        self.assertEqual(seasons.count(), 3)

    def test_valid_title(self):
        """Test matching title."""
        create_playlist(title="abc", video=self.video_a)
        title = "abc"
        queryset = Playlist.objects.filter(title=title)
        self.assertTrue(queryset.exists())

    def test_video_playlist(self):
        """Test video with palylists"""

        create_playlist(video=self.video_a)

        qs = self.video_a.playlist_featured.all()
        self.assertEqual(qs.count(), 1)

    def test_slug_field(self):
        """Test creating slug for playlist"""
        playlist = create_playlist(title="abc", video=self.video_a)
        title = playlist.title
        test_slug = slugify(title)
        self.assertEqual(test_slug, playlist.slug)

    def test_video_playlist_ids_property(self):
        """Test videos on playlist"""
        ids = self.video_a.get_playlist_ids()
        actual_ids = list(
            Playlist.objects.filter(video=self.video_a).values_list(
                "id", flat=True
            )
        )
        self.assertEqual(ids, actual_ids)

    def test_playlist_video_items(self):
        """Test count videos on playlist."""
        playlist = create_playlist(title="abc")
        playlist.videos.set([self.video_a, self.video_b])
        playlist.save()
        count = playlist.videos.all().count()
        self.assertEqual(count, 2)

    def test_playlist_video_through_model(self):
        """Test count videos on playlist."""
        playlist = create_playlist(title="abc")
        playlist.videos.set([self.video_a, self.video_b])
        playlist.save()

        v_qs = sorted(list(Video.objects.all().values_list("id")))
        video_qs = sorted(list(playlist.videos.all().values_list("id")))
        playlist_item_qs = sorted(
            list(playlist.playlistitem_set.all().values_list("video"))
        )

        self.assertEqual(v_qs, video_qs, playlist_item_qs)
