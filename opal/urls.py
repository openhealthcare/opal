from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

from opal import views
from opal.forms import ChangePasswordForm
from opal import models
from opal.utils import camelcase_to_underscore

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

    url(r'^schema/list/$', views.ListSchemaView.as_view()),
    url(r'^schema/detail/$', views.DetailSchemaView.as_view()),
    url(r'^schema/extract/$', views.ExtractSchemaView.as_view()),
    url(r'^options/$', views.options_view),
    url(r'^userprofile/$', views.userprofile_view),
    url(r'^admin/?', include(admin.site.urls)),
    url(r'^patient/?$', views.patient_search_view),
    url(r'^episode/?$', views.episode_list_and_create_view),
    url(r'^episode/(?P<tag>[a-z_]+)/?$', views.EpisodeListView.as_view()),
    url(r'^episode/(?P<tag>[a-z_]+)/(?P<subtag>[a-z_]+)/?$', views.EpisodeListView.as_view()),
    url(r'^episode/(?P<pk>\d+)/?$', views.episode_detail_view),

    url(r'^tagging/(?P<pk>\d+)/?', views.TaggingView.as_view()),

    url(r'^search/extract/$', views.ExtractSearchView.as_view()),
    url(r'^search/extract/download$', views.DownloadSearchView.as_view()),

    url(r'^filters/?$', views.FilterView.as_view()),
    url(r'^filters/(?P<pk>\d+)/?$', views.FilterDetailView.as_view()),

    url(r'^templates/episode_list.html/?$', views.EpisodeListTemplateView.as_view()),
    url(r'^templates/episode_list.html/(?P<tag>[a-z_]+)/?$', views.EpisodeListTemplateView.as_view()),
    url(r'^templates/episode_list.html/(?P<tag>[a-z_]+)/(?P<subtag>[a-z_]+)/?$', views.EpisodeListTemplateView.as_view()),

    url(r'^templates/episode_detail.html/?$',
        views.EpisodeDetailTemplateView.as_view()),
    url(r'^templates/discharge_list.html/?$', views.DischargeListTemplateView.as_view()),
    url(r'^templates/discharge_list.html/(?P<tag>[a-z_]+)/?$', views.DischargeListTemplateView.as_view()),
    url(r'^templates/discharge_list.html/(?P<tag>[a-z_]+)/(?P<subtag>[a-z_]+)/?$', views.DischargeListTemplateView.as_view()),

    url(r'^templates/search.html/?$', views.SearchTemplateView.as_view()),
    url(r'^templates/extract.html/?$', views.ExtractTemplateView.as_view()),
    url(r'^templates/modals/tagging.html/?$', views.TagsTemplateView.as_view()),

    url(r'^templates/modals/undischarge.html/?$',
        views.UndischargeTemplateView.as_view()),
    url(r'^templates/modals/add_episode.html/?$',
        views.AddEpisodeTemplateView.as_view()),
    url(r'^templates/modals/hospital_number.html/?$',
        views.HospitalNumberTemplateView.as_view()),
    url(r'^templates/modals/reopen_episode.html/?$',
        views.ReopenEpisodeTemplateView.as_view()),
    url(r'^templates/modals/discharge_episode.html/?$',
        views.DischargeEpisodeTemplateView.as_view()),
    url(r'^templates/modals/delete_item_confirmation.html/?$',
        views.DeleteItemConfirmationView.as_view()),
    url(r'^templates/modals/save_filter_modal.html/?$',
        views.SaveFilterModalView.as_view()),

)

subrecord_models = models.PatientSubrecord.__subclasses__() + models.EpisodeSubrecord.__subclasses__()

for subrecord_model in subrecord_models:
    sub_url = camelcase_to_underscore(subrecord_model.__name__)
    urlpatterns += patterns('',
        url(r'^%s/?$' % sub_url, views.subrecord_create_view,
            {'model': subrecord_model}),
        url(r'^%s/(?P<pk>\d+)/?$' % sub_url,
            views.subrecord_detail_view, {'model': subrecord_model}),
        url(r'^templates/modals/%s.html/?$' % sub_url,
            views.ModalTemplateView.as_view(), {'model': subrecord_model}),
    )

urlpatterns += staticfiles_urlpatterns()

from opal.utils import OpalPlugin

for plugin in OpalPlugin.__subclasses__():
    urlpatterns += plugin.urls
