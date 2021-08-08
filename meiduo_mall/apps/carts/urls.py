from django.urls import path
from apps.carts.views import CartView, CartsSelectAllView, CartsSimpleView

urlpatterns = [
    path('carts/', CartView.as_view()),
    path('carts/selection/', CartsSelectAllView.as_view()),
    path('carts/simple/', CartsSimpleView.as_view()),
]