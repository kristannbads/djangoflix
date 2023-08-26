"""Test for the videos API."""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Video
from video.serializers import VideoSerializer
from core.db.models import PublishStateOptions

VIDEOS_URL = reverse("video:video-list")


def create_video(user, **kwargs):
    """Create adn return a sample recipe."""
    defaults = {
        "title": "One more chance",
        "description": "Love story",
        "state": PublishStateOptions.DRAFT,
    }
    defaults.update(kwargs)

    videos = Video.objects.create(user=user, **defaults)

    return videos


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicVideoApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(VIDEOS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateVideoApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="test123",
        )
        self.client.force_authenticate(self.user)

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

    def test_retrieve_videos(self):
        """Test retrieving a list of videos."""

        create_video(user=self.user, video_id="abc")
        create_video(user=self.user, video_id="abcde")

        qs = Video.objects.filter(user=self.user)
        self.assertEqual(qs.count(), 2)

        res = self.client.get(VIDEOS_URL)

        videos = Video.objects.all().order_by("-id")
        serializer = VideoSerializer(videos, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    # def test_video_list_limited_to_user(self):
    #     """Test list of videos is limited to authenticated user."""
