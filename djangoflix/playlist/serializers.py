"""Serializer class for video API."""

from rest_framework import serializers

from core.models import Playlist


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for playlist."""

    class Meta:
        model = Playlist
        fields = ["title", "description", "id", "video"]
        read_only_fields = ["id"]
