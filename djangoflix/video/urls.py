from django.urls import path, include
from rest_framework.routers import DefaultRouter
from video import views

router = DefaultRouter()
router.register("videos", views.VideoViewSet)

app_name = "video"

urlpatterns = [
    path("", include(router.urls)),
]
