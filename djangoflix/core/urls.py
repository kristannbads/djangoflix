from django.urls import path
from core import views

app_name = "std"

urlpatterns = [
    path("", views.FeaturedPlaylistListView.as_view()),
    path("media/<int:pk>/", views.PlaylistDetailView.as_view()),
    path("playlists/", views.PlaylistListView.as_view()),
    path("movies/<slug:slug>/", views.MovieDetailView.as_view()),
    path("movies/", views.MovieListView.as_view()),
    path(
        "shows/<slug:showSlug>/seasons/<slug:seasonSlug>/",
        views.TVShowSeasonDetailView.as_view(),
    ),
    path("shows/<slug:slug>/seasons/", views.TVShowDetailView.as_view()),
    path("shows/<slug:slug>/", views.TVShowDetailView.as_view()),
    path("shows/", views.TVShowListView.as_view()),
]
