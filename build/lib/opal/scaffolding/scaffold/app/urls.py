from opal.urls import urlpatterns as opatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = []

urlpatterns += opatterns
