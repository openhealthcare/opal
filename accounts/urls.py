"""
Urls for user accounts
"""
from django.conf.urls import patterns, url

from accounts.forms import ChangePasswordForm
from accounts import views

urlpatterns = patterns(
    '',
    url(r'^login/$', 'accounts.views.check_password_reset', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^change-password/?$', 'django.contrib.auth.views.password_change',
        {'post_change_redirect': '/', 'password_change_form': ChangePasswordForm},
        name='change-password'),
    url(r'^templates/account_detail.html', views.AccountDetailTemplateView.as_view()),
)
