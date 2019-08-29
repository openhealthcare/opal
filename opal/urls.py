"""
Core Opal URlconfs
"""
from django.conf.urls import include, url
from django.contrib.auth.views import logout, password_change
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

from opal import views
from opal.core import api, subrecords, plugins
from opal.forms import ChangePasswordForm

api.initialize_router()

urlpatterns = [
    url(r'^$', views.IndexView.as_view()),

    url(r'^accounts/login/$', views.check_password_reset, name='login'),

    url(r'^accounts/logout/$',
        logout, {'next_page': '/'},
        name='logout'),

    url(r'^accounts/change-password/?$',
        password_change,
        {'post_change_redirect': '/',
         'password_change_form': ChangePasswordForm},
        name='change-password'),

    url(r'^accounts/banned', views.BannedView.as_view(), name='banned'),

    url(r'^admin/', admin.site.urls),

    # Template views
    url(r'^templates/patient_list.html/(?P<slug>[0-9a-z_\-]+)/?$',
        views.PatientListTemplateView.as_view(),
        name="patient_list_template_view"),

    url(r'^templates/patient_detail.html$',
        views.PatientDetailTemplateView.as_view(), name="patient_detail"),

    url(r'^templates/episode_detail.html/(?P<pk>\d+)/?$',
        views.EpisodeDetailTemplateView.as_view(), name="episode_detail"),

    # New Public facing API urls
    url(r'api/v0.1/', include(api.router.urls)),

    url(r'^templates/record/(?P<model>[0-9a-z_\-]+).html$',
        views.RecordTemplateView.as_view(), name="record_view"),

    url(r'^templates/forms/(?P<model>[0-9a-z_\-]+).html/?$',
        views.FormTemplateView.as_view(), name="form_view"),

]


# Generated subrecord template views
for subrecord_model in subrecords.subrecords():
    sub_url = subrecord_model.get_api_name()
    url_name = "{}_modal".format(sub_url)
    urlpatterns += [
        url(r'^templates/modals/%s.html/?$' % sub_url,
            views.ModalTemplateView.as_view(),
            {'model': subrecord_model},
            name=url_name
        ),
        url(r'^templates/modals/%s.html/(?P<list>[0-9a-z_\-]+/?)$' % sub_url,
            views.ModalTemplateView.as_view(),
            {'model': subrecord_model},
            name=url_name
        )
    ]


urlpatterns += staticfiles_urlpatterns()

for plugin in plugins.OpalPlugin.list():
    urlpatterns += plugin.get_urls()

urlpatterns += [
    url(
        r'templates/(?P<template_name>[0-9a-z_/]+.html)',
        views.RawTemplateView.as_view(),
        name="raw_template_view"
    )
]
