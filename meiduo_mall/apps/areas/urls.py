from django.conf.urls import url
from django.urls import path, re_path

from apps.areas.views import AreasView, SubAreasView

urlpatterns = [
    path('areas/', AreasView.as_view()),
    re_path(r'^areas/(?P<pk>[1-9]\d+)/$', SubAreasView.as_view()),

]