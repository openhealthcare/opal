from django.utils.log import AdminEmailHandler
from django.conf import settings


class ConfidentialEmailer(AdminEmailHandler):
    def __init__(self, *args, **kwargs):
        super(ConfidentialEmailer, self).__init__(*args, **kwargs)
        self.include_html = False

    def get_brand_name(self):
        return getattr(settings, "OPAL_BRAND_NAME", "unnamed opal app")

    def format_subject(self, subject):
        return "{} error".format(self.get_brand_name())

    def emit(self, record):
        record.msg = 'censored'
        record.args = []
        detail = ""
        if hasattr(record, "request") and record.request:
            if record.request.user.is_authenticated():
                user = record.request.user.username
            else:
                user = "anonymous"

            msg = "sent to host {0} on application {1} from user {2} with {3}"

            detail = msg.format(
                record.request.META.get("HTTP_HOST"),
                self.get_brand_name(),
                user,
                record.request.META.get("REQUEST_METHOD"),
            )
        record.request = None

        record.exc_text = "from {0}:{1}".format(
            record.filename,
            record.lineno
        )

        record.exc_text += "\n{}".format(detail)
        return super(ConfidentialEmailer, self).emit(record)
