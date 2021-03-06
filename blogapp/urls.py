from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from blogapp import views
from .views import (
    post_list,
    post_create,
    # post_detail,
    # post_update,
    # post_delete,
    )

urlpatterns = [
    # url(r'^$', views.IndexView.as_view(), name='list'),
    url(r'^$', post_list, name='list'),
    url(r'^create/$', post_create, name='post_create'),
    url(r'^vote/$', views.vote_handler, name='vote_handler'),
    url(r'^account/(?P<user_id>[\d]+)/$', views.account_page, name='account_page'),
    url(r'^(?P<slug>[\w-]+)/$', views.post_detail, name='detail'),
    url(r'^(?P<slug>[\w-]+)/delete/$', views.DeleteView.as_view()),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.UpdateView.as_view(), name='edit'),
    # Note : form for upvoting posts has been hardcoded to below url    
    

]
