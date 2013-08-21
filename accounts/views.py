"""
OPAL System level views
"""
from django.contrib.auth.views import login
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.models import UserProfile

def check_password_reset(request, *args, **kwargs):
    """
    Check to see if the user needs to reset their password
    """
    response = login(request, *args, **kwargs)
    if response.status_code == 302:
        try:
            profile = request.user.get_profile()
            print profile
            if profile and profile.force_password_change:
                return redirect('django.contrib.auth.views.password_change')
        except UserProfile.DoesNotExist:
            print 'creatin'
            UserProfile.objects.create(user=request.user, force_password_change=True)
            return redirect('django.contrib.auth.views.password_change')
    return response

class AccountDetailTemplateView(TemplateView):
    template_name = 'accounts/account_detail.html'
