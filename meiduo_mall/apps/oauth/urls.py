from django.conf.urls import url
from django.urls import path
from apps.oauth.views import QQAuthURLView, QQAuthUserView

urlpatterns = [
    path('qq/authorization/', QQAuthURLView.as_view()),
    path('oauth_callback/', QQAuthUserView.as_view()),
]