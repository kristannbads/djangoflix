"""Serializer class for video API."""

from rest_framework import serializers
from core.models import Playlist
from tags.serializers import TagSerializer
from categories.serializers import CategorySerializer


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for playlist."""

    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Playlist
        fields = ["title", "description", "type", "id", "category", "tags"]
        read_only_fields = ["id"]
