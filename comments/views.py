from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Comment
# Create your views here.


def comment_delete(request, id):
    obj = get_object_or_404(Comment, id=id)
    context = {
        "object": obj
    }
    return render("render", "confirm_delete.html", context)
