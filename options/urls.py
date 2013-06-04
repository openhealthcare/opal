from django.conf.urls import patterns, url
from options import model_names

urlpatterns = patterns('')

for name in model_names:
    urlpatterns += patterns('', url(r'^%s_list/' % name, 'options.views.options_view', {'model_name': name}))
