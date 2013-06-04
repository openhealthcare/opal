from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^destinations/', 'options.views.destinations'),
    url(r'^antimicrobials/', 'options.views.antimicrobials'),
)
