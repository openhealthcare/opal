from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from patients.views import IndexView, ContactView, schema_view, SearchView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view()),
    url(r'^contact/$', ContactView.as_view()),
    url(r'^schema/$', schema_view),
    url(r'^options/', include('options.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^patient/', include('patients.urls')),
    url(r'^search/', SearchView.as_view()),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)

urlpatterns += staticfiles_urlpatterns()
