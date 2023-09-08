"""Serializer class for video API."""

from rest_framework import serializers
from core.models import Playlist
from tags.serializers import TaggedObjectRelatedField


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for playlist."""

    tags = TaggedObjectRelatedField(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ["title", "description", "id", "tags"]
        read_only_fields = ["id"]
