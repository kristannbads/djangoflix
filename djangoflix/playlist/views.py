"""Views for Playlist API."""
from playlist.serializers import PlaylistSerializer

from rest_framework import authentication, permissions
from rest_framework import viewsets

from core.models import Playlist


class PlaylistViewSet(viewsets.ModelViewSet):
    """View for playlist APIs."""

    serializer_class = PlaylistSerializer
    queryset = Playlist.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        return queryset.all().order_by("-id").distinct()
