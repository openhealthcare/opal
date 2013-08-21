from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from patients import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view()),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^contact/$', views.ContactView.as_view()),
    url(r'^schema/list/$', views.list_schema_view),
    url(r'^schema/detail/$', views.detail_schema_view),
    url(r'^options/$', 'options.views.options_view'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^patient/', include('patients.urls.records')),
    url(r'^templates/', include('patients.urls.templates')),
)

urlpatterns += staticfiles_urlpatterns()
