from django.urls import path, re_path
from apis.views import *


urlpatterns = [
    re_path('^sign_up/$', SignUpView.as_view(), name='sign-up'),
    re_path('^users/$', UserSearchView.as_view(), name='users'),
    re_path('^friend_request/$', SendFriendRequestView.as_view(), name='friend-request'),
    re_path('^friend_list/$', FriendsListView.as_view(), name='friend-list'),
]