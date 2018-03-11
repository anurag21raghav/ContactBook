from django.conf.urls import include
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^$', views.ContactBook, name="index"),
    url(r'^search/$', views.Search, name="search")
]

