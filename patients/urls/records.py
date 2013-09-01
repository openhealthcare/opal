from django.conf.urls import patterns, url
from utils import camelcase_to_underscore
from patients import models, views

urlpatterns = patterns('',
    url(r'^patient/?$', views.patient_search_view),
    url(r'^patient/(?P<pk>\d+)/?$', views.patient_detail_view),
    url(r'^episode/?$', views.episode_list_and_create_view),
)

subrecord_models = models.PatientSubrecord.__subclasses__() + models.EpisodeSubrecord.__subclasses__()

for subrecord_model in subrecord_models:
    sub_url = camelcase_to_underscore(subrecord_model.__name__)
    urlpatterns += patterns('',
        url(r'^%s/?$' % sub_url, views.subrecord_create_view, {'model': subrecord_model}),
        url(r'^%s/(?P<pk>\d+)/?$' % sub_url, views.subrecord_detail_view, {'model': subrecord_model}),
    )
