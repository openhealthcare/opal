from django.conf.urls import patterns, url
from utils import camelcase_to_underscore
from patients import models, views

urlpatterns = patterns('',
    url(r'^$', views.patient_list_and_create_view),
    url(r'^(?P<pk>\d+)/$', views.patient_detail_view),
    url(r'^templates/patient_list.html/$', views.PatientListTemplateView.as_view()),
    url(r'^templates/patient_detail.html/$', views.PatientDetailTemplateView.as_view()),
    url(r'^templates/search.html/$', views.SearchTemplateView.as_view()),
)

for subrecord_model in models.Subrecord.__subclasses__():
    sub_url = camelcase_to_underscore(subrecord_model.__name__)
    urlpatterns += patterns('',
        url(r'^%s/$' % sub_url, views.subrecord_create_view, {'model': subrecord_model}),
        url(r'^%s/(?P<pk>\d+)/$' % sub_url, views.subrecord_detail_view, {'model': subrecord_model}),
    )
