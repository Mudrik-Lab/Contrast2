from os import getenv

import pytz
from django.utils import timezone
from spa.middleware import SPAMiddleware
from django.conf import settings
from django.urls import is_valid_path


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        environment_timezone = getenv("USER_TZ", "Asia/Jerusalem")
        activated_timezone = pytz.timezone(environment_timezone)
        timezone.activate(activated_timezone)
        return self.get_response(request)


class MultiSPAMiddleware(SPAMiddleware):

    def resolve_spa_root(self):
        """
        Resolve spa root, by request domain or hard coded in settings for local
        """
        return self.spa_root  # TODO: placeholder to change

    def manual_set_spa_root(self, value):
        self.spa_root = value

    def process_request(self, request):
        # First try to serve the static files (on /static/ and on /)
        # which is relatively fast as files are stored in a self.files dict
        if self.autorefresh:  # debug mode
            static_file = self.find_file(request.path_info)
        else:  # from the collected static files
            static_file = self.files.get(request.path_info)
        if static_file is not None:
            return self.serve(static_file, request)
        else:
            # if no file was found there are two options:

            # 1) the file is in one of the Django urls
            # (e.g. a template or the Djangoadmin)
            # so we'll let Django handle this
            # (just return and let the normal middleware take its course)
            urlconf = getattr(request, 'urlconf', None)
            if is_valid_path(request.path_info, urlconf):
                return
            if (settings.APPEND_SLASH and not request.path_info.endswith('/') and
                    is_valid_path('%s/' % request.path_info, urlconf)):
                return

            # 2) the url is handled by frontend routing
            # redirect all unknown files to the SPA root
            try:
                return self.serve(self.resolve_spa_root(), request)
            except AttributeError:  # no SPA page stored yet
                self.manual_set_spa_root(self.find_file('/'))
                if self.spa_root:
                    return self.serve(self.resolve_spa_root(), request)
