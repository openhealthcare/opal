from django.conf.urls import patterns, url
from records import views

urlpatterns = patterns('',
    url(r'^patient/$', views.patient_create),
    url(r'^patient/(?P<id>\d+)/$', views.patient_detail),
    url(r'^admission/$', views.admission_create),
    url(r'^admission/(?P<id>\d+)/$', views.admission_detail),
    url(r'^(?P<subrecord_name>\w+)/$', views.subrecord_create),
    url(r'^(?P<subrecord_name>\w+)/(?P<id>\d+)/$', views.subrecord_detail),
)
