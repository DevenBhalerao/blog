from django import template
from django.contrib.contenttypes.models import ContentType
from votes.models import Vote
register = template.Library()
import logging

logger = logging.getLogger(__name__)


@register.filter
def has_voted(instance, user):
    content_type = ContentType.objects.get_for_model(instance.__class__)
    # logger.debug(content_type)
    voted = Vote.objects.filter(user=user,
                                content_type=content_type,
                                object_id=instance.id
                                )
    if voted:
        css_class = "upvoted"
    else:
        css_class = "not_voted"
    
    return css_class
