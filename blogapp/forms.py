from django import forms
# from django.contrib.auth.models import User
from pagedown.widgets import PagedownWidget
from .models import Post


class PostForm(forms.ModelForm):
    content = forms.CharField(widget=PagedownWidget())

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "image",
        ]




# class LoginForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = [
#             "username",
#             "password",
#             "email",
#             "first_name",
#             "last_name"
#         ]
