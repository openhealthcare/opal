"""
Urls for the pathway OPAL plugin
"""
from django.conf.urls import patterns, url

from opal.core.pathway import views, api

urlpatterns = patterns(
    '',
    url(r'^pathway/$', views.PathwayIndexView.as_view(), name="pathway_index"),
    url(
        r'^pathway/templates/(?P<name>[a-z_]+).html$',
        views.PathwayTemplateView.as_view(), name="pathway_template"
    ),
    url(
        r'^pathway/detail/(?P<name>[0-9a-z_-]+)$',
        api.PathwayApi.as_view({
            'post': 'create',
            'get': 'retrieve'
        }),
        name="pathway"
    ),
    url(
        r'^pathway/detail/(?P<name>[0-9a-z_-]+)/(?P<patient_id>[0-9]+)/(?P<episode_id>[0-9]+)?$',
        api.PathwayApi.as_view({
            'post': 'create',
            'get': 'retrieve'
        }),
        name="pathway"
    ),
)
