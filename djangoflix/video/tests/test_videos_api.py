"""Test for the videos API."""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Video
from video.serializers import VideoSerializer
from core.db.models import PublishStateOptions

VIDEOS_URL = reverse("video:video-list")


def detail_url(video_id):
    """Create and return a video detail URL."""
    return reverse("video:video-detail", args=[video_id])


def create_video(user, **kwargs):
    """Create adn return a sample video."""
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

    def test_video_list_limited_to_user(self):
        """Test list of videos is limited to authenticated user."""

        other_user = create_user(
            email="other_ser@example.com", password="test123"
        )
        create_video(user=other_user)
        create_video(user=self.user, video_id="video sample id")

        res = self.client.get(VIDEOS_URL)

        videos = Video.objects.filter(user=self.user)
        serializer = VideoSerializer(videos, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_video_detail(self):
        """Test get video detail."""
        video = create_video(user=self.user)

        url = detail_url(video.id)
        res = self.client.get(url)

        serializer = VideoSerializer(video)
        self.assertEqual(res.data, serializer.data)

    def test_create_video(self):
        """Test creating a video."""

        payload = {
            "title": "Sample video",
            "description": "Sample description",
            "video_id": "testvideoid",
        }

        res = self.client.post(VIDEOS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        video = Video.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(video, k), v)
        self.assertEqual(video.user, self.user)

    def test_partial_update(self):
        """Test partial update of a video."""

        video = create_video(
            user=self.user,
            title="Sample video title",
            description="Sample description",
        )

        payload = {"title": "New video title"}
        url = detail_url(video.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        video.refresh_from_db()
        self.assertEqual(video.title, payload["title"])
        self.assertEqual(video.user, self.user)

    def test_full_update(self):
        """Test full update of video."""
        video = create_video(
            user=self.user,
            title="Sample video title",
            description="Sample video description",
        )

        payload = {
            "title": "New Sample video",
            "description": "New video description",
            "video_id": "testvideoid",
        }

        url = detail_url(video.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        video.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(video, k), v)
        self.assertEqual(video.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the video user results in an error."""
        new_user = create_user(email="user2@example.com", password="test123")
        video = create_video(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(video.id)
        self.client.patch(url, payload)

        video.refresh_from_db()
        self.assertEqual(video.user, self.user)

    def test_delete_video(self):
        """Test deleting a video successful."""

        video = create_video(user=self.user)

        url = detail_url(video.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Video.objects.filter(id=video.id).exists())

    def test_delete_other_users_video_error(self):
        """Test trying to delete another users video gives error."""
        new_user = create_user(email="user2@example.com", password="test123")
        video = create_video(user=new_user)

        url = detail_url(video.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Video.objects.filter(id=video.id).exists())
