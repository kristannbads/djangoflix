"""Test for the playlists API."""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Playlist, Video
from playlist.serializers import PlaylistSerializer
from core.db.models import PublishStateOptions

PLAYLIST_URL = reverse("playlist:playlist-list")


def detail_url(playlist_id):
    """Create and return a playlist detail URL."""
    return reverse("playlist:playlist-detail", args=[playlist_id])


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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicPlaylistApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(PLAYLIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlaylistApiTests(TestCase):
    """Test authenticated API requests."""

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

    def test_retrieve_playlists(self):
        """Test retrieving a list of playlists."""

        create_playlist(title="abc", video=self.video_a)

        qs = Playlist.objects.filter(title="abc")
        self.assertEqual(qs.count(), 1)

        res = self.client.get(PLAYLIST_URL)

        playlists = Playlist.objects.all().order_by("-id")
        serializer = PlaylistSerializer(playlists, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_playlist_detail(self):
        """Test get playlist detail."""
        playlist = create_playlist(title="abc", video=self.video_a)

        url = detail_url(playlist.id)
        res = self.client.get(url)

        serializer = PlaylistSerializer(playlist)
        self.assertEqual(res.data, serializer.data)

    def test_create_playlist(self):
        """Test creating a playlist."""

        payload = {
            "title": "Sample playlist",
            "description": "Sample description",
        }

        res = self.client.post(PLAYLIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        playlist = Playlist.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(playlist, k), v)

    def test_partial_update(self):
        """Test partial update of a playlist."""

        playlist = create_playlist(
            title="Sample playlist title",
            description="Sample description",
        )

        payload = {"title": "New playlist title"}
        url = detail_url(playlist.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        playlist.refresh_from_db()
        self.assertEqual(playlist.title, payload["title"])

    def test_full_update(self):
        """Test full update of playlist."""

        playlist = create_playlist(
            title="Sample playlist title",
            description="Sample playlist description",
        )

        payload = {
            "title": "New Sample playlist",
            "description": "New playlist description",
        }

        url = detail_url(playlist.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        playlist.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(playlist, k), v)

    def test_delete_playlist(self):
        """Test deleting a playlist successful."""

        playlist = create_playlist()

        url = detail_url(playlist.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Playlist.objects.filter(id=playlist.id).exists())
