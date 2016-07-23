from django.views.generic import (DetailView, ListView, DeleteView,
  FormView)
from django.core.urlresolvers import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import  HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from comments.models import Comment
from votes.models import Vote
from .models import Post
from django.contrib.contenttypes.models import ContentType

from comments.forms import CommentForm
from votes.forms import VoteForm
from .forms import PostForm
import logging

logger = logging.getLogger(__name__)


class IndexView(ListView):
    template_name = 'blogapp/index.html'

    def get_queryset(self):
        return Post.objects.all()


# @login_required(login_url='/login/')
def post_list(request):
    today = timezone.now().date()
    queryset_list = Post.objects.all()  # .order_by("-timestamp")
    query = request.GET.get("q")
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


# class DetailView(DetailView):
#     model = Post
#     template_name = 'blogapp/detail.html'

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
            # print request.POST.get("parent_id")
            parent_id = int(request.POST.get("parent_id"))
            # print "exception not thrown"
        except:
            # print "exception thrown"
            parent_id = None
        if parent_id:
            # print "parent_id exists"
            # print parent_id
            parent_qs = Comment.objects.filter(id=parent_id)
            # print parent_qs
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
                # print parent_obj
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
    logger.debug(request.POST)
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
    # instance = get_object_or_404(content_type, id=upvoted_object_id)
    # comments = Comment.objects.filter_by_instance(instance)
    # initial_data = {
    #     "content_type": instance.get_content_type,
    #     "object_id": instance.id,
    # }

# class CreateView(FormView):
#     form_class = PostForm
#     template_name = 'blogapp/form.html'
#     fields = ["title",
#               "content",
#               "image",
#               "url",
#               ]

#     def form_valid(self, form):
#         new_post = form.save()
#         print new_post
#         return reverse('blogapp:detail', kwargs={"slug": new_post.slug})


def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
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
