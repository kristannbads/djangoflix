"""Serializer class for video API."""

from rest_framework import serializers
from playlist.serializers import PlaylistSerializer
from core.models import Video, Playlist


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for videos."""

    playlist_item = PlaylistSerializer(many=True, required=False)

    class Meta:
        model = Video
        fields = ["title", "description", "id", "video_id", "playlist_item"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):

        playlist_data = validated_data.pop("playlist_item", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if playlist_data is not None:
            instance.playlist_item.clear()

            for ply in playlist_data:
                ply_obj, created = Playlist.objects.get_or_create(
                    **ply,
                )
                instance.playlist_item.add(ply_obj)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
