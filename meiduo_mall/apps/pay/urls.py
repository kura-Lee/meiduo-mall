from django.urls import path
from apps.pay.views import PaymentView, PaymentStatusView


urlpatterns = [
    path('payment/status/', PaymentStatusView.as_view()),
    path('payment/<order_id>/', PaymentView.as_view()),
]
