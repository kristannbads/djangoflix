from core.db.models import PublishStateOptions
from django.utils import timezone
from django.utils.text import slugify


def publish_state_pre_save(sender, instance, *args, **kwargs):
    is_publish = instance.state == PublishStateOptions.PUBLISH
    is_draft = instance.state == PublishStateOptions.DRAFT
    if is_publish and instance.published_timestamp is None:
        instance.published_timestamp = timezone.now()
    elif is_draft:
        instance.published_timestamp = None


def slugify_pre_save(sender, instance, *args, **kwargs):
    title = instance.title
    slug = instance.slug
    if slug is None:
        instance.slug = slugify(title)
