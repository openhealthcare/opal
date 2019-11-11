"""
Urls file for an opal application
"""
from django.conf.urls import include, url
from opal.views import IndexView
from opal.urls import urlpatterns as opatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', IndexView.as_view()),
]

urlpatterns += opatterns
