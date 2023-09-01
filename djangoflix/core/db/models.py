from django.db import models


class PublishStateOptions(models.TextChoices):
    PUBLISH = "PU", "Publish"
    DRAFT = "DR", "Draft"


class PlaylistTypeChoices(models.TextChoices):
    MOVIE = "MOV", "Movie"
    SHOW = "TVS", "TV Show"
    SEASON = "SEA", "Season"
    PLAYLIST = "PLY", "Playlist"
