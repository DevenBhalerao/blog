from django.views.generic import (DeleteView, FormView)
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse


from accounts.forms import ChangePasswordForm
from comments.models import Comment
from votes.models import Vote
from .models import Post
from django.contrib.contenttypes.models import ContentType

from comments.forms import CommentForm
from votes.forms import VoteForm
from .forms import PostForm
import logging

logger = logging.getLogger(__name__)


def account_page(request, user_id=None):
    content_type_post = ContentType.objects.get_for_model(Post)
    content_type_comment = ContentType.objects.get_for_model(Comment)
    user = User.objects.get(id=user_id)
    liked_comments_votes = Vote.objects.filter(
        user=user,
        content_type=content_type_comment
    )
    liked_posts_votes = Vote.objects.filter(
        user=user,
        content_type=content_type_post
    )
    submitted_posts = Post.objects.filter(
        submitter=user,
    )
    submitted_comments = Comment.objects.filter(
        user=user,
    )
    liked_comments = list()
    liked_posts = list()
    for vote in liked_comments_votes:
        comments = Comment.objects.filter(id=vote.object_id)
        for comment in comments:
            liked_comments.append(comment)
        # logger.debug(liked_comments)
    for vote in liked_posts_votes:
        posts = Post.objects.filter(id=vote.object_id)
        for post in posts:
            liked_posts.append(post)
    form = ChangePasswordForm(request.POST or None)
    if form.is_valid():
        user = request.user
        form_user = form.cleaned_data.get('username')
        if user.username != form_user:
            messages.add_message(
                request, messages.INFO,
                'You can only change your own password'
            )
        else:
            password = form.cleaned_data.get('password_new')
            user.set_password(password)
            user.save()
            messages.add_message(
                request, messages.INFO, 'Password changed Succesfully!')
        return redirect("/")
    context = {
        "user": user,
        "liked_comments": liked_comments,
        "liked_posts": liked_posts,
        "change_password_form": form,
        "submitted_posts": submitted_posts,
        "submitted_comments": submitted_comments,
    }
    return render(request, 'blogapp/account.html', context)


# @login_required(login_url='/login/')
def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.all()  # .order_by("-timestamp")
    query = request.GET.get("search")
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        ).distinct()
    paginator = Paginator(queryset_list, 8)  # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        "title": "List",
        "page_request_var": page_request_var,
        "today": today,
    }
    return render(request, 'blogapp/index.html', context)


def post_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    comments = Comment.objects.filter_by_instance(instance)
    initial_data = {
        "content_type": instance.get_content_type,
        "object_id": instance.id,
    }
    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid() and request.user.is_authenticated():
        c_type = comment_form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        object_id = comment_form.cleaned_data.get("object_id")
        content_data = comment_form.cleaned_data.get("content")
        parent_obj = None
        try:
            parent_id = int(request.POST.get("parent_id"))
        except:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            # print parent_qs
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
        new_comment, created = Comment.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            content=content_data,
            parent=parent_obj,
        )
        if created:
            return HttpResponseRedirect(
                new_comment.content_object.get_absolute_url()
            )
    comments = instance.comments
    context = {
        "instance": instance,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "blogapp/detail.html", context)


def vote_handler(request):
    vote_form = VoteForm(request.POST or None)
    if vote_form.is_valid() and request.user.is_authenticated():
        c_type = vote_form.cleaned_data.get("content_type_upvote")
        content_type = ContentType.objects.get(model=c_type)
        object_id = vote_form.cleaned_data.get("object_id_upvote")
        new_vote, created = Vote.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
        )
        if created:
            logger.debug(
                "new vote created for {content_type} with parent id {id} and {user}"
                .format(content_type=content_type,
                        id=new_vote.object_id, user=request.user)
            )
        else:
            logger.debug("already voted, deleteing {id}".format(id=object_id))
            new_vote.delete()
    return HttpResponse('')


def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {"form": form, }
    return render(request, 'blogapp/form.html', context)


class UpdateView(FormView):
    form_class = PostForm
    template_name = 'blogapp/form.html'
    fields = ["title",
              "content",
              "image",
              "url",
              ]


class DeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('blogapp:list')


class CreateUserView(FormView):
    model = User
    template_name = "blogapp/form.html"
    success_url = reverse_lazy('blogapp:list')
    fields = ["username",
              "password",
              "email",
              "first_name",
              "last_name",
              ]


def get_success_url(self, form):
    user = authenticate(username=self.username, password=self.password)
    if user is not None:
        login(self.request, user)
        return reverse_lazy('blogapp:list')
