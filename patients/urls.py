import re
from django.conf.urls import patterns, url
from patients import models, views

camelcase_to_underscore = lambda str: re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', '_\\1', str).lower().strip('_')

urlpatterns = patterns('',
    url(r'^$', views.PatientList.as_view()),
)

for subrecord_model in models.SingletonSubrecord.__subclasses__():
    sub_url = camelcase_to_underscore(subrecord_model.__name__)
    urlpatterns += patterns('', url(r'^(?P<patient_id>\d+)/%s/$' % sub_url, views.SingletonSubrecordDetail.as_view(model=subrecord_model)))

for subrecord_model in models.Subrecord.__subclasses__():
    sub_url = camelcase_to_underscore(subrecord_model.__name__)
    urlpatterns += patterns('',
        url(r'^(?P<patient_id>\d+)/%s/$' % sub_url, views.SubrecordList.as_view(model=subrecord_model)),
        url(r'^(?P<patient_id>\d+)/%s/(?P<id>\d+)/$' % sub_url, views.SubrecordDetail.as_view(model=subrecord_model)))
