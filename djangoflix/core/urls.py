from django.urls import path
from core import views

app_name = "std"

urlpatterns = [
    path("", views.FeaturedPlaylistListView.as_view()),
    path("playlists/", views.PlaylistListView.as_view()),
    path("movies/", views.MovieListView.as_view()),
    path("shows/", views.TVShowListView.as_view()),
]
