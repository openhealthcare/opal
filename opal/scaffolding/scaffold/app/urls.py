from django.conf.urls import patterns, include, url

from opal.urls import urlpatterns as opatterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += opatterns
