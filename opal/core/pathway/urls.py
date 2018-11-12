"""
Urls for the pathway Opal plugin
"""
from django.conf.urls import url

from opal.core.pathway import views, api

PATHWAY_REGEX = "(?P<name>[0-9a-z_\-]+)"  # noqa: W605
PATIENT_ID_REGEX = "(?P<patient_id>[0-9]+)"
EPISODE_ID_REGEX = "(?P<episode_id>[0-9]+)"

urlpatterns = [
    url(r'^pathway/$', views.PathwayIndexView.as_view(), name="pathway_index"),
    url(
        r'^pathway/templates/{}.html$'.format(PATHWAY_REGEX),
        views.PathwayTemplateView.as_view(), name="pathway_template"
    ),
    url(
        r'^pathway/detail/{}$'.format(PATHWAY_REGEX),
        api.PathwayApi.as_view({
            'post': 'create',
            'get': 'retrieve'
        }),
        name="pathway"
    ),
    url(
        r'^pathway/detail/{0}/{1}$'.format(PATHWAY_REGEX, PATIENT_ID_REGEX),
        api.PathwayApi.as_view({
            'post': 'create',
            'get': 'retrieve'
        }),
        name="pathway"
    ),
    url(
        r'^pathway/detail/{0}/{1}/{2}$'.format(
            PATHWAY_REGEX, PATIENT_ID_REGEX, EPISODE_ID_REGEX
        ),
        api.PathwayApi.as_view({
            'post': 'create',
            'get': 'retrieve'
        }),
        name="pathway"
    ),
]
