from django.conf.urls import url
from django.urls import path
from apps.users.views import UsernameCountView, MobileCountView, UserRegisterView, \
    LoginView, LogoutView, UserInfoView, UserEmailView, VerifyEmailView, CreateAddressView,\
    AddressView, DefaultAddress, TitleAddress, ChangePasswordView, UserHistoryView

urlpatterns = [
    path('usernames/<username:username>/count/', UsernameCountView.as_view(), name="usernamecount"),
    path('mobiles/<mobile:mobile>/count/', MobileCountView.as_view(), name="usernamecount"),
    path('register/', UserRegisterView.as_view(), name="usernamecount"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/', ChangePasswordView.as_view(), name='changepasswd'),
    path('info/', UserInfoView.as_view(), name='userinfo'),
    path('emails/', UserEmailView.as_view(), name='save_email'),
    path('emails/verification/', VerifyEmailView.as_view(), name='active_email'),
    path('addresses/create/', CreateAddressView.as_view()),
    path('addresses/', AddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/$', AddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$', DefaultAddress.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$', TitleAddress.as_view()),

    path('browse_histories/', UserHistoryView.as_view()),
]