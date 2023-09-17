from django.views.generic import ListView, DetailView
from django.http import Http404
from django.utils import timezone
from core.models import Playlist, MovieProxy, TVShowProxy, TVShowSeasonProxy
from core.db.models import PublishStateOptions


class PlaylistMixin:
    template_name = "playlist_list.html"
    title = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.title is not None:
            context["title"] = self.title
        print(context)
        return context

    def get_queryset(self):
        return super().get_queryset().published()


class PlaylistListView(PlaylistMixin, ListView):
    queryset = Playlist.objects.all()
    title = "Playlist"


class PlaylistDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/playlist_detail.html"
    queryset = Playlist.objects.all()


class FeaturedPlaylistListView(PlaylistMixin, ListView):
    queryset = Playlist.objects.featured_playlist()
    title = "Featured"


class MovieListView(PlaylistMixin, ListView):
    queryset = MovieProxy.objects.all()
    title = "Movies"


class MovieDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/movie_detail.html"
    queryset = MovieProxy.objects.all()
    title = "Movies"


class TVShowListView(PlaylistMixin, ListView):
    queryset = TVShowProxy.objects.all()
    title = "TV Show"


class TVShowDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/tvshow_detail.html"
    queryset = TVShowProxy.objects.all()
    title = "TV Show"


class TVShowSeasonDetailView(PlaylistMixin, DetailView):
    template_name = "playlists/season_detail.html"
    queryset = TVShowSeasonProxy.objects.all()
    title = "TV Show"

    def get_object(self):
        kwargs = self.kwargs
        show_slug = kwargs.get("showSlug")
        season_slug = kwargs.get("seasonSlug")
        now = timezone.now()
        try:
            obj = TVShowSeasonProxy.objects.get(
                state=PublishStateOptions.PUBLISH,
                published_timestamp__lte=now,
                parent__slug__iexact=show_slug,
                slug__iexact=season_slug,
            )
        except TVShowSeasonProxy.MultipleObjectsReturned:
            qs = TVShowSeasonProxy.objects.filter(
                parent__slug__iexact=show_slug, slug__iexact=season_slug
            ).publish()
            obj = qs.first()
        except Exception:
            raise Http404

        return obj
