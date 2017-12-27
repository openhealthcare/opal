"""
Urls for Opal's search functionality
"""
from django.conf.urls import url

from opal.core.search import views

urlpatterns = [
    url(r'^search/$', views.SearchIndexView.as_view(), name="search_index"),
    url(r'^search/templates/search.html/?$',
        views.SearchTemplateView.as_view()),

    url(r'^search/templates/extract.html/?$',
        views.ExtractTemplateView.as_view()),

    url(r'^search/templates/modals/save_filter_modal.html/?$',
        views.SaveFilterModalView.as_view()),

    url(r'^search/patient/?$',
        views.patient_search_view, name="patient_search"),

    url(r'^search/simple/$',
        views.simple_search_view, name="simple_search"),

    url(r'^search/extract/$',
        views.ExtractSearchView.as_view(), name="extract_search"),

    url(r'^search/extract/download$',
        views.DownloadSearchView.as_view(), name="extract_download"),

    url(r'^search/filters/?$',
        views.FilterView.as_view(), name="extract_filters"),

    url(r'^search/filters/(?P<pk>\d+)/?$',
        views.FilterDetailView.as_view(), name="extract_filters"),

    url(r'^search/extract/result/(?P<task_id>[a-zA-Z0-9-]*)',
        views.ExtractResultView.as_view(), name='extract_result'),

    url(r'^search/extract/download/(?P<task_id>[a-zA-Z0-9-]*)',
        views.ExtractFileView.as_view(), name='extract_file'),
]
