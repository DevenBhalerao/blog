from django.contrib import admin

# Register your models here.
from .models import Vote


class VoteModelAdmin(admin.ModelAdmin):
    list_display = ["object_id", "content_type", "user"]

    class Meta:
        model = Vote

admin.site.register(Vote, VoteModelAdmin)
