"""
Urls for Opal's search functionality
"""
from django.conf.urls import url

from opal.core.search import views

urlpatterns = [
    url(r'^search/$', views.SearchIndexView.as_view(), name="search"),

    url(r'^search/templates/extract.html/?$',
        views.ExtractTemplateView.as_view()),

    url(r'^search/patient/?$',
        views.patient_search_view, name="patient_search"),

    url(r'^search/simple/$',
        views.simple_search_view, name="simple_search"),

    url(r'^search/extract/$',
        views.ExtractSearchView.as_view(), name="extract_search"),

    url(r'^search/extract/download$',
        views.DownloadSearchView.as_view(), name="extract_download"),

    url(r'^search/extract/result/(?P<task_id>[a-zA-Z0-9-]*)',
        views.ExtractResultView.as_view(), name='extract_result'),

    url(r'^search/extract/download/(?P<task_id>[a-zA-Z0-9-]*)',
        views.ExtractFileView.as_view(), name='extract_file'),
]
