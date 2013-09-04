from django.conf.urls import patterns, url
from utils import camelcase_to_underscore
from patients import models, views

urlpatterns = patterns('',
    url(r'^episode_list.html/?$', views.EpisodeListTemplateView.as_view()),
    url(r'^episode_detail.html/?$', views.EpisodeDetailTemplateView.as_view()),
    url(r'^search.html/?$', views.SearchTemplateView.as_view()),
    url(r'^modals/add_episode.html/?$', views.AddEpisodeTemplateView.as_view()),
    url(r'^modals/hospital_number.html/?$', views.HospitalNumberTemplateView.as_view()),
    url(r'^modals/reopen_episode.html/?$', views.ReopenEpisodeTemplateView.as_view()),
    url(r'^modals/discharge_episode.html/?$', views.DischargeEpisodeTemplateView.as_view()),
    url(r'^modals/delete_item_confirmation.html/?$', views.DeleteItemConfirmationView.as_view()),
)

subrecord_models = models.PatientSubrecord.__subclasses__() + models.EpisodeSubrecord.__subclasses__()

for subrecord_model in subrecord_models:
    sub_url = camelcase_to_underscore(subrecord_model.__name__)
    urlpatterns += patterns('',
        url(r'^modals/%s.html/?$' % sub_url, views.ModalTemplateView.as_view(), {'model': subrecord_model}),
    )
