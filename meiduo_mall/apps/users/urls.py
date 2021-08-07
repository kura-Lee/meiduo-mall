from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView, UserRegisterView, LoginView, LogoutView


urlpatterns = [
    path('usernames/<username:username>/count/',UsernameCountView.as_view(), name="usernamecount"),
    path('mobiles/<mobile:mobile>/count/',MobileCountView.as_view(), name="usernamecount"),
    path('register/', UserRegisterView.as_view(), name="usernamecount"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='login'),
]