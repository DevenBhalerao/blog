from django.contrib import admin
from blogapp.models import Post
# Register your models here.


class PostModelAdmin(admin.ModelAdmin):
    list_display = ["title", "timestamp", "updated"]

    class Meta:
        model = Post


admin.site.register(Post, PostModelAdmin)
