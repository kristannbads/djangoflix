from django.urls import path, include
from rest_framework.routers import DefaultRouter
from categories import views

router = DefaultRouter()
router.register("category", views.CategoryViewSet)

app_name = "category"

urlpatterns = [
    path("", include(router.urls)),
]
