"""
Core OPAL URlconfs
"""
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from opal import views
from opal.core import api
from opal.forms import ChangePasswordForm
from opal import models
from opal.utils import camelcase_to_underscore
from opal.core.subrecords import subrecords

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view()),

    url(r'^accounts/login/$', views.check_password_reset, name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^accounts/change-password/?$', 'django.contrib.auth.views.password_change',
        {'post_change_redirect': '/', 'password_change_form': ChangePasswordForm},
        name='change-password'),
    url(r'^accounts/templates/account_detail.html',
        views.AccountDetailTemplateView.as_view()),
    url(r'^accounts/banned', views.BannedView.as_view(), name='banned'),
    url(r'^admin/?', include(admin.site.urls)),


    # Internal (Legacy) API views
    url(r'^episode/?$', views.episode_list_and_create_view),
    url(r'^episode/(?P<tag>[a-z_\-]+)/?$', views.EpisodeListView.as_view()),
    url(r'^episode/(?P<tag>[a-z_\-]+)/(?P<subtag>[a-z_\-]+)/?$', views.EpisodeListView.as_view()),
    url(r'^episode/(?P<pk>\d+)/?$', views.episode_detail_view),

    url(r'^episode/(?P<pk>\d+)/actions/copyto/(?P<category>[a-zA-Z_\-]+)/?$',
        views.EpisodeCopyToCategoryView.as_view()),

    # Template vires
    url(r'^templates/episode_list.html/?$', views.EpisodeListTemplateView.as_view()),
    url(r'^templates/episode_list.html/(?P<tag>[a-z_\-]+)/?$', views.EpisodeListTemplateView.as_view()),
    url(r'^templates/episode_list.html/(?P<tag>[a-z_\-]+)/(?P<subtag>[a-z_\-]+)/?$', views.EpisodeListTemplateView.as_view()),

    url(r'^templates/episode_detail.html/(?P<pk>\d+)/?$',
        views.EpisodeDetailTemplateView.as_view()),

    url(r'^templates/modals/tagging.html/?', views.TagsTemplateView.as_view()),

    url(r'^templates/modals/undischarge.html/?$',
        views.UndischargeTemplateView.as_view()),
    url(r'^templates/modals/add_episode.html/?$',
        views.AddEpisodeTemplateView.as_view()),
    url(r'^templates/modals/add_episode_without_teams.html/?$',
        views.AddEpisodeWithoutTeamsTemplateView.as_view()),
    url(r'^templates/modals/hospital_number.html/?$',
        views.HospitalNumberTemplateView.as_view()),
    url(r'^templates/modals/reopen_episode.html/?$',
        views.ReopenEpisodeTemplateView.as_view()),
    url(r'^templates/modals/discharge_episode.html/?$',
        views.DischargeEpisodeTemplateView.as_view()),
    url(r'^templates/modals/copy_to_category.html/?$',
        views.CopyToCategoryTemplateView.as_view()),

    url(r'^templates/modals/delete_item_confirmation.html/?$',
        views.DeleteItemConfirmationView.as_view()),

    # New Public facing API urls
    url(r'api/v0.1/episode/admit', csrf_exempt(api.APIAdmitEpisodeView.as_view())),
    url(r'api/v0.1/episode/refer', csrf_exempt(api.APIReferPatientView.as_view())),
    url(r'api/v0.1/', include(api.router.urls)),
)

# Generated subrecord template views
for subrecord_model in subrecords():
    sub_url = camelcase_to_underscore(subrecord_model.__name__)
    urlpatterns += patterns(
        '',
        url(r'^templates/modals/%s.html/?$' % sub_url,
            views.ModalTemplateView.as_view(), {'model': subrecord_model}),
        url(r'^templates/modals/%s.html/(?P<tag>[a-z_\-]+)/?$' % sub_url,
            views.ModalTemplateView.as_view(), {'model': subrecord_model}),
        url(r'^templates/modals/%s.html/(?P<tag>[a-z_\-]+)/(?P<subtag>[a-z_\-]+)/?$' % sub_url,
            views.ModalTemplateView.as_view(), {'model': subrecord_model}),
    )


urlpatterns += staticfiles_urlpatterns()

from opal.core import plugins

for plugin in plugins.plugins():
    urlpatterns += plugin.urls

urlpatterns += patterns(
    '',
    url(r'templates/(?P<template_name>[a-z_/]+.html)', views.RawTemplateView.as_view())
)
