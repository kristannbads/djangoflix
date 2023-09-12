from django.db import models


class PublishStateOptions(models.TextChoices):
    PUBLISH = "PU", "Publish"
    DRAFT = "DR", "Draft"


class PlaylistTypeChoices(models.TextChoices):
    MOVIE = "MOV", "Movie"
    SHOW = "TVS", "TV Show"
    SEASON = "SEA", "Season"
    PLAYLIST = "PLY", "Playlist"


class RatingChoices(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    __empty__ = "Unknown"
