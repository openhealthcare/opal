"""
Urls for OPAL's search functionality
"""
from django.conf.urls import patterns, url

from opal.core.search import views

urlpatterns = patterns(
    '',

    url(r'^search/templates/search.html/?$', views.SearchTemplateView.as_view()),
    url(r'^search/templates/extract.html/?$', views.ExtractTemplateView.as_view()),
    url(r'^search/templates/modals/save_filter_modal.html/?$',
        views.SaveFilterModalView.as_view()),

    url(r'^search/patient/?$', views.patient_search_view),
    url(r'^search/simple/$', views.simple_search_view),
    url(r'^search/extract/$', views.ExtractSearchView.as_view()),
    url(r'^search/extract/download$', views.DownloadSearchView.as_view()),
    url(r'^search/filters/?$', views.FilterView.as_view()),
    url(r'^search/filters/(?P<pk>\d+)/?$', views.FilterDetailView.as_view()),
)
