from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from votes.models import Vote

# Create your models here.
# from blogapp.models import Post
import logging

logger = logging.getLogger(__name__)


class CommentManager(models.Manager):

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(CommentManager, self).filter(
            content_type=content_type,
            object_id=obj_id
        ).filter(parent=None)
        return qs


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    # post = models.ForeignKey(Post)

    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     null=True
                                     )
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    objects = CommentManager()
    parent = models.ForeignKey("self", null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __unicode__(self):
        return str(self.user.username)

    def __str__(self):
        return str(self.user.username)

    @property
    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True

    @property
    def vote_count(self):
        instance = self
        # logger.debug("the comment is {no}".format(no=instance.id))
        votes = Vote.objects.filter_by_instance(instance)
        if instance.id == 21:
            logger.debug("the votes is {no}".format(no=len(votes)))
        return len(votes)

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


