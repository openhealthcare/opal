from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from patients import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view()),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^contact/$', views.ContactView.as_view()),
    url(r'^schema/$', views.schema_view),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^patient/', include('patients.urls.records')),
    url(r'^templates/', include('patients.urls.templates')),
)

urlpatterns += staticfiles_urlpatterns()
