b§)

# Generated subrecord template views
for subrecord_model in subrecords.subrecords():
    sub_url = subrecord_model.get_api_name()
    url_name = "{}_modal".format(sub_url)
    urlpatterns += patterns(
        '',
        url(r'^templates/modals/%s.html/?$' % sub_url,
            views.ModalTemplateView.as_view(),
            {'model': subrecord_model},
            name=url_name
        ),
        url(r'^templates/modals/%s.html/(?P<list>[a-z_\-]+/?)$' % sub_url,
            views.ModalTemplateView.as_view(),
            {'model': subrecord_model},
            name=url_name
        ),
    )


urlpatterns += staticfiles_urlpatterns()

from opal.core import plugins

for plugin in plugins.plugins():
    urlpatterns += plugin.urls

urlpatterns += patterns(
    '',
    url(
        r'templates/(?P<template_name>[0-9a-z_/]+.html)',
        views.RawTemplateView.as_view(),
        name="raw_template_view"
    )
)
