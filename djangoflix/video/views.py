"""Views for Video API."""
from video.serializers import VideoSerializer

from rest_framework import authentication, permissions
from rest_framework import viewsets

from core.models import Video


class VideoViewSet(viewsets.ModelViewSet):
    """View for video APIs."""

    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return (
            Video.objects.filter(user=self.request.user)
            .order_by("-id")
            .distinct()
        )

    def perform_create(self, serializer):
        """Create a new recipe."""

        serializer.save(user=self.request.user)
