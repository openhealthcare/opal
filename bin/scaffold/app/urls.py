from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from opal.urls import urlpatterns as opatterns

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += opatterns
