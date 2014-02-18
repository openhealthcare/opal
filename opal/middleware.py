"""
OPAL Middlewares
"""
# Hat tip: http://kevinzhang.org/posts/django-angularjs-and-csrf-xsrf-protection.html

ANGULAR_HEADER_NAME = 'HTTP_X_XSRF_TOKEN'

class AngularCSRFRename(object):
    def process_request(self, request):
        if ANGULAR_HEADER_NAME in request.META:
            request.META['HTTP_X_CSRFTOKEN'] = request.META[ANGULAR_HEADER_NAME]
            del request.META[ANGULAR_HEADER_NAME]


class DjangoReversionWorkaround(object):
    def process_request(self, request):
        access = request.user.is_authenticated()
