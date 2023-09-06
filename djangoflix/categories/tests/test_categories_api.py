"""Test for the categorys API."""

from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Category
from categories.serializers import CategorySerializer

CATEGORY_URL = reverse("category:category-list")


def detail_url(category_id):
    """Create and return a category detail URL."""
    return reverse("category:category-detail", args=[category_id])


def create_category(**kwargs):
    """Create and return a sample category."""
    defaults = {
        "title": "Comedy",
    }
    defaults.update(kwargs)

    category = Category.objects.create(**defaults)

    return category


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicCategoryApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(CATEGORY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()

        self.user = create_user(
            email="user@example.com",
            password="test123",
        )
        self.cat_a = Category.objects.create(title="My title a")
        self.cat_b = Category.objects.create(title="My title b")
        self.client.force_authenticate(self.user)

    def test_retrieve_categories(self):
        """Test retrieving a list of categorys."""

        create_category(title="abc")

        qs = Category.objects.filter(title="abc")
        self.assertEqual(qs.count(), 1)

        res = self.client.get(CATEGORY_URL)

        categories = Category.objects.all().order_by("-id")
        serializer = CategorySerializer(categories, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_categories_detail(self):
        """Test get category detail."""
        category = create_category(title="abc")

        url = detail_url(category.id)
        res = self.client.get(url)

        serializer = CategorySerializer(category)
        self.assertEqual(res.data, serializer.data)

    def test_create_category(self):
        """Test creating a category."""

        payload = {
            "title": "Sample category",
        }

        res = self.client.post(CATEGORY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        category = Category.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(category, k), v)

    def test_partial_update(self):
        """Test partial update of a category."""

        category = create_category(
            title="Sample category title",
        )

        payload = {"title": "New category title"}
        url = detail_url(category.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.title, payload["title"])

    def test_full_update(self):
        """Test full update of category."""

        category = create_category(
            title="Sample category title",
        )

        payload = {
            "title": "New Sample category",
        }

        url = detail_url(category.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(category, k), v)

    def test_delete_category(self):
        """Test deleting a category successful."""

        category = create_category()

        url = detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category.id).exists())
