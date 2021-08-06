from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView, UserRegisterView


urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view(), name="usernamecount"),
    path('mobiles/<mobile:mobile>/count/',MobileCountView.as_view(), name="usernamecount"),
    path('register/', UserRegisterView.as_view(), name="usernamecount"),
]