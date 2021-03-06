from __future__ import unicode_literals
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

# Create your models here.
import logging

logger = logging.getLogger(__name__)


class VoteManager(models.Manager):

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(VoteManager, self).filter(
            content_type=content_type,
            object_id=obj_id
        )
        if obj_id == 21:
            logger.debug(qs)
        return qs


class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     null=True
                                     )
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    objects = VoteManager()
