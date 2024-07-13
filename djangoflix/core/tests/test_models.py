"""
Tests for models.
"""
import random
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.apps import apps
from django.db.models import Avg

from rest_framework.test import APIClient
from django.utils.text import slugify
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from core.models import (
    MovieProxy,
    Playlist,
    TaggedItem,
    Video,
    Category,
    Rating,
    TVShowProxy,
    TVShowSeasonProxy,
)
from core.db.models import PublishStateOptions, RatingChoices

User = get_user_model()


def create_user(email="user@example.com", password="testpass123"):
    """Create a return a new user."""
    return User.objects.create_user(email, password)


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
        user = User.objects.create_user(
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
            user = User.objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            User.objects.create_user("", "test123")

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
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

        user = User.objects.create_user(
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
        """Test generation of slug field."""
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

        user = User.objects.create_user(
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
        Playlist.objects.create(
            title="Sample Playlist",
            description="Sample desc",
            video=self.video_a,
        )
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


class MovieProxyTests(TestCase):
    """Test MovieProxy model."""

    def setUp(self):
        self.movie_title = "This is my title"
        self.published_item_count = 1
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
        self.movie_a = MovieProxy.objects.create(
            title=self.movie_title,
            state=PublishStateOptions.PUBLISH,
        )
        self.movie_b = MovieProxy.objects.create(
            title=self.movie_title,
        )

        self.client.force_authenticate(self.user)

    def test_create_movie(self):
        """Test creating a movie is successful."""
        self.assertEqual(str(self.movie_a), self.movie_title)

    def test_movie_clip_items(self):
        """Test creating video in a movie"""
        self.movie_a.videos.set([self.video_a])
        count = self.movie_a.videos.all().count()
        self.assertEqual(count, 1)

    def test_valid_title(self):
        """Test matching title."""
        title = self.movie_title
        queryset = MovieProxy.objects.filter(title=title)
        self.assertTrue(queryset.exists())

    def test_movie_slug_unique(self):
        """Test uniqueness of generated slug."""
        self.assertNotEqual(self.movie_a.slug, self.movie_b.slug)

    def test_slug_field(self):
        """Test creating slug for movie"""
        title = self.movie_title
        test_slug = slugify(title)
        self.assertEqual(test_slug, self.movie_a.slug)

    def test_draft_case(self):
        """ "Test count of draft state created by MovieProxy."""
        qs = MovieProxy.objects.filter(state=PublishStateOptions.DRAFT)
        self.assertEqual(qs.count(), 1)

    def test_publish_case(self):
        """ "Test count of draft state created by MovieProxy."""
        qs = MovieProxy.objects.filter(state=PublishStateOptions.PUBLISH)
        self.assertEqual(qs.count(), 1)

    def test_publish_manager(self):
        """Test mpublished method of model."""
        published_qs = MovieProxy.objects.all().published()
        published_qs_2 = MovieProxy.objects.published()
        self.assertTrue(published_qs.exists())
        self.assertEqual(published_qs.count(), published_qs_2.count())
        self.assertEqual(published_qs.count(), self.published_item_count)


class TVShowProxyModelTestCase(TestCase):
    def create_show_with_seasons(self):
        """Test creating show with seasons."""
        the_office = TVShowProxy.objects.create(title="The Office Series")
        self.season_1 = TVShowSeasonProxy.objects.create(
            title="The Office Series Season 1",
            state=PublishStateOptions.PUBLISH,
            parent=the_office,
            order=1,
        )

        TVShowSeasonProxy.objects.create(
            title="The Office Series Season 2", parent=the_office, order=2
        )
        TVShowSeasonProxy.objects.create(
            title="The Office Series Season 3", parent=the_office, order=3
        )
        TVShowSeasonProxy.objects.create(
            title="The Office Series Season 4", parent=the_office, order=4
        )

        self.season_11 = TVShowSeasonProxy.objects.create(
            title="The Office Series Season 1", parent=the_office, order=4
        )
        self.show = the_office

    def create_videos(self):
        video_a = Video.objects.create(
            user=self.user, title="My title", video_id="abc123"
        )
        video_b = Video.objects.create(
            user=self.user, title="My title", video_id="abc1233"
        )
        video_c = Video.objects.create(
            user=self.user, title="My title", video_id="abc1234"
        )
        self.video_a = video_a
        self.video_b = video_b
        self.video_c = video_c
        self.video_qs = Video.objects.all()

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="test123",
        )
        self.client.force_authenticate(self.user)

        self.create_videos()
        self.create_show_with_seasons()
        self.obj_a = TVShowProxy.objects.create(
            title="This is my title", video=self.video_a
        )
        obj_b = TVShowProxy.objects.create(
            title="This is my title", state=PublishStateOptions.PUBLISH
        )

        obj_b.videos.set(self.video_qs)
        obj_b.save()
        self.obj_b = obj_b

    def test_show_has_seasons(self):
        """Test if show has seasons."""
        seasons = self.show.playlist_set.all()
        self.assertTrue(seasons.exists())
        self.assertEqual(seasons.count(), 5)

    def test_show_slug_unique(self):
        """Test uniqueness of generated slug."""
        self.assertNotEqual(self.season_1.slug, self.season_11.slug)

    def test_tvshow_video(self):
        """Test if video exists on show."""
        self.assertEqual(self.obj_a.video, self.video_a)

    def test_playlist_video_items(self):
        """Test count of video items in palylist."""
        count = self.obj_b.videos.all().count()
        self.assertEqual(count, 3)

    def test_playlist_video_through_model(self):
        """Test different query in getting videos."""
        v_qs = sorted(list(self.video_qs.values_list("id")))
        video_qs = sorted(list(self.obj_b.videos.all().values_list("id")))
        playlist_item_qs = sorted(
            list(self.obj_b.playlistitem_set.all().values_list("video"))
        )
        self.assertEqual(v_qs, video_qs, playlist_item_qs)

    def test_video_playlist_ids_property(self):
        """Test if euqality of video ids."""
        ids = self.obj_a.video.get_playlist_ids()
        actual_ids = list(
            TVShowProxy.objects.all()
            .filter(video=self.video_a)
            .values_list("id", flat=True)
        )
        self.assertEqual(ids, actual_ids)

    def test_video_playlist(self):
        """Test count of featured video."""
        qs = self.video_a.playlist_featured.all()
        self.assertEqual(qs.count(), 1)

    def test_slug_field(self):
        """Test generating slug."""
        title = self.obj_a.title
        test_slug = slugify(title)
        self.assertEqual(test_slug, self.obj_a.slug)

    def test_valid_title(self):
        """Test if filtering through title exists."""
        title = "This is my title"
        qs = TVShowProxy.objects.all().filter(title=title)
        self.assertTrue(qs.exists())

    def test_tv_shows_created_count(self):
        """Test count of created shows."""
        qs = TVShowProxy.objects.all()
        self.assertEqual(qs.count(), 3)

    def test_seasons_created_count(self):
        """Test count of created seasons."""
        qs = TVShowSeasonProxy.objects.all()
        self.assertEqual(qs.count(), 5)

    def test_tv_show_draft_case(self):
        """Test count of show with draft state."""
        qs = TVShowProxy.objects.all().filter(state=PublishStateOptions.DRAFT)
        self.assertEqual(qs.count(), 2)

    def test_seasons_draft_case(self):
        """Test count of seasons with draft state."""
        qs = TVShowSeasonProxy.objects.all().filter(
            state=PublishStateOptions.DRAFT
        )
        self.assertEqual(qs.count(), 4)

    def test_publish_case(self):
        """Test count of show with publish state."""
        now = timezone.now()
        published_qs = TVShowProxy.objects.all().filter(
            state=PublishStateOptions.PUBLISH, published_timestamp__lte=now
        )
        self.assertTrue(published_qs.exists())

    def test_publish_manager(self):
        """Test mpublished method of model."""
        published_qs = TVShowProxy.objects.all().published()
        published_qs_2 = TVShowProxy.objects.all().published()
        self.assertTrue(published_qs.exists())
        self.assertEqual(published_qs.count(), published_qs_2.count())


class CategoryTestCase(TestCase):
    """Test category model."""

    def setUp(self):
        cat_a = Category.objects.create(title="Action")
        cat_b = Category.objects.create(title="Comedy", active=False)

        self.playlist = Playlist.objects.create(
            title="This is my title", category=cat_a
        )

        self.cat_a = cat_a
        self.cat_b = cat_b

        def test_is_active(self):
            """Test if instance of a model is active."""
            self.assertTrue(self.cat_a.active)

        def test_is_not_active(self):
            """Test if instance of a model is not active."""
            self.assertFalse(self.cat_b.active)

        def test_category_on_playlist(self):
            """Test if category exists on playlist."""
            qs = self.cat_a.playlist_set.all()

            self.assertTrue(self.playlist.category.exists())
            self.assertEqual(qs.count(), 1)


class TaggedItemTestCase(TestCase):
    """Test taggeditem model."""

    def setUp(self):
        # self.tag_a = TaggedItem.objects.create(tag="new-tag")
        ply_title = "New title"
        self.playlist_obj = Playlist.objects.create(title=ply_title)
        self.playlist_obj2 = Playlist.objects.create(title=ply_title)
        self.ply_title = ply_title
        self.playlist_obj.tags.add(TaggedItem(tag="new tag"), bulk=False)
        self.playlist_obj2.tags.add(TaggedItem(tag="new tag"), bulk=False)

    def test_content_type_is_not_null(self):
        """Test if content type is not null."""
        with self.assertRaises(IntegrityError):
            self.tag_a = TaggedItem.objects.create(tag="new-tag")

    def test_create_via_content_type(self):
        """Test creating using content type."""
        c_type = ContentType.objects.get(app_label="core", model="playlist")

        tag_a = TaggedItem.objects.create(
            content_type=c_type,
            object_id=1,
            tag="new-tag",
        )
        self.assertIsNotNone(tag_a.pk)

        tag_b = TaggedItem.objects.create(
            content_type=c_type,
            object_id=100,
            tag="new-tag2",
        )
        self.assertIsNotNone(tag_b.pk)

    def test_case_via_model_content_type(self):
        """Test creating tags via model."""
        c_type = ContentType.objects.get_for_model(Playlist)

        tag_a = TaggedItem.objects.create(
            content_type=c_type,
            object_id=1,
            tag="new-tag",
        )
        self.assertIsNotNone(tag_a.pk)

    def test_case_via_app_loader_content_type(self):
        """Test creating tags via app loader."""
        PlaylistKlass = apps.get_model(
            app_label="core", model_name="Playlist"
        )

        c_type = ContentType.objects.get_for_model(PlaylistKlass)

        tag_a = TaggedItem.objects.create(
            content_type=c_type,
            object_id=1,
            tag="new-tag",
        )
        self.assertIsNotNone(tag_a.pk)

    def test_related_field(self):
        """Test if tags exists on playlist object."""

        self.assertTrue(self.playlist_obj.tags.all().exists)
        self.assertEqual(self.playlist_obj.tags.count(), 1)

    def test_related_field_create(self):
        """Test creating and adding tags in an existing object."""

        self.playlist_obj.tags.create(tag="another-tag")
        self.assertEqual(self.playlist_obj.tags.count(), 2)

    def test_related_field_query_name(self):
        """Test related field exists in playlist object."""
        qs = TaggedItem.objects.filter(playlist__title__iexact=self.ply_title)
        self.assertEqual(qs.count(), 2)

    def test_related_field_via_content_type(self):
        """Test creating related field exists."""
        c_type = ContentType.objects.get_for_model(Playlist)

        tag_qs = TaggedItem.objects.filter(
            content_type=c_type,
            object_id=self.playlist_obj.id,
        )
        self.assertEqual(tag_qs.count(), 1)

    def test_direct_obj_creation(self):
        """Test creating tags in an object."""
        obj = self.playlist_obj
        tag = TaggedItem.objects.create(content_object=obj, tag="another1")
        self.assertIsNotNone(tag.pk)


class RatingTestCase(TestCase):
    """Test for Rating model."""

    def create_playlists(self):
        """Bulk creation of playlist."""
        items = []
        self.playlist_count = random.randint(10, 200)
        for i in range(0, self.playlist_count):
            items.append(Playlist(title=f"TV show {i}"))
        Playlist.objects.bulk_create(items)
        self.playlists = Playlist.objects.all()

    def create_users(self):
        """Bulk creation of users."""
        items = []
        self.user_count = random.randint(10, 100)
        for i in range(0, self.user_count):
            items.append(User(email=f"user_{i}@example.com"))
        User.objects.bulk_create(items)
        self.users = User.objects.all()

    def create_ratings(self):
        """Bulk creation of ratings."""
        items = []
        self.rating_totals = []
        self.rating_count = 1_000
        for i in range(0, self.rating_count):
            user_obj = self.users.order_by("?").first()
            ply_obj = self.playlists.order_by("?").first()
            rating_val = random.choice(RatingChoices.choices)[0]
            if rating_val is not None:
                self.rating_totals.append(rating_val)
            items.append(
                Rating(
                    user=user_obj, content_object=ply_obj, value=rating_val
                )
            )
        Rating.objects.bulk_create(items)
        self.ratings = Rating.objects.all()

    def setUp(self):
        self.create_users()
        self.create_playlists()
        self.create_ratings()

    def test_user_count(self):
        """Test user count."""
        qs = User.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.user_count)
        self.assertEqual(self.users.count(), self.user_count)

    def test_playlist_count(self):
        """Test playlist count."""
        qs = Playlist.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.playlist_count)
        self.assertEqual(self.playlists.count(), self.playlist_count)

    def test_rating_count(self):
        """Test rating count."""
        qs = Rating.objects.all()
        self.assertTrue(qs.exists())
        self.assertEqual(qs.count(), self.rating_count)
        self.assertEqual(self.ratings.count(), self.rating_count)

    def test_rating_random_choices(self):
        """Test values for the rating choices."""
        value_set = set(Rating.objects.values_list("value", flat=True))
        self.assertTrue(len(value_set) > 1)

    def test_rating_agg(self):
        """Test average method from rating model."""
        db_avg = Rating.objects.aggregate(average=Avg("value"))["average"]
        self.assertIsNotNone(db_avg)
        self.assertTrue(db_avg > 0)

        total_sum = sum(self.rating_totals)
        passed_avg = total_sum / (len(self.rating_totals) * 1.0)
        self.assertEqual(round(passed_avg, 2), round(db_avg, 2))

    def test_rating_playlist_agg(self):
        """Test average method from playlist model."""
        item_1 = Playlist.objects.aggregate(average=Avg("ratings__value"))[
            "average"
        ]
        self.assertIsNotNone(item_1)
        self.assertTrue(item_1 > 0)
