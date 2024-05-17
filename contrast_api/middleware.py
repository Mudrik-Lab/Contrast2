import os
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
    static_url = settings.STATIC_URL
    spa_roots = {}

    def update_files_dictionary(self, *args):
        super(SPAMiddleware, self).update_files_dictionary(*args)
        index_page_suffix = '/' + self.index_name
        index_name_length = len(self.index_name)
        static_prefix_length = len(settings.STATIC_URL) - 1
        directory_indexes = {}
        # TODO refactor this to adpat to use of multiple spa roots
        for url, static_file in self.files.items():
            if url.endswith(index_page_suffix):
                # For each index file found, add a corresponding URL->content
                # mapping for the file's parent directory,
                # so that the index page is served for
                # the bare directory URL ending in '/'.
                parent_directory_url = url[:-index_name_length]
                directory_indexes[parent_directory_url] = static_file
                # remember the root page for any other unrecognised files
                # to be frontend-routed
                self.spa_root = static_file
            else:
                # also serve static files on /
                # e.g. when /my/file.png is requested, serve /static/my/file.png
                directory_indexes[url[static_prefix_length:]] = static_file
        self.files.update(directory_indexes)
    def find_file(self, url, app_name=None):
        # In debug mode, find_file() is used to serve files directly
        # from the filesystem instead of using the list in `self.files`,
        # we append the index filename so that will be served if present.
        # TODO: handle the trailing slash for the case of e.g. /welcome/
        # (should be frontend-routed)
        if url.endswith('/'):
            # url += self.index_name
            url = f'/static/{app_name}/index.html'
            self.spa_roots[app_name] = super(SPAMiddleware, self).find_file(url)
            return self.spa_roots[app_name]
        else:
            # also serve static files on /
            # e.g. when /my/file.png is requested, serve /static/my/file.png
            if (not url.startswith(self.static_url)):
                url = os.path.join(self.static_url, url[1:])
            return super(SPAMiddleware, self).find_file(url)
    def process_request(self, request):
        self.static_url  = settings.STATIC_URL
        # First try to serve the static files (on /static/ and on /)
        # which is relatively fast as files are stored in a self.files dict
        static_app = self.resolve_spa_app(request)
        if static_app:
            self.static_url = f'/static/{static_app}/'
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
            app_name = self.resolve_spa_app(request)
            try:
                return self.serve(self.spa_roots.get(app_name), request)
            except AttributeError:  # no SPA page stored yet
                spa_root = self.find_file(f'/', app_name=app_name)
                self.spa_roots[app_name] = spa_root
                if self.spa_roots.get(app_name):
                    return self.serve(self.spa_roots[app_name], request)


    def resolve_spa_app(self, request):
        """
        Resolve spa root, by request domain or hard coded in settings for local
        """
        domain = request.META.get("HTTP_HOST", "")  # Get the domain from request headers
        app = settings.SPA_APPS_MAPPING.get(domain)
        return f"{app}"  # TODO: placeholder to change



