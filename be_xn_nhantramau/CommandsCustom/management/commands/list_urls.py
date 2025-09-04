# yourapp/management/commands/list_urls.py

from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver
import inspect

class Command(BaseCommand):
    help = 'List all URLs in the project with detailed view function or method names'

    def handle(self, *args, **kwargs):
        urlconf = get_resolver()
        urls = self.extract_urls(urlconf.url_patterns)
        for url, view_detail in urls:
            self.stdout.write(f'URL:: [ "{url}" ] -> VIEW:: [ "{view_detail}" ]')

    def extract_urls(self, patterns, parent_pattern=''):
        urls = []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                full_pattern = parent_pattern + str(pattern.pattern)
                view_detail = self.get_view_detail(pattern.callback)
                urls.append((full_pattern, view_detail))
            elif isinstance(pattern, URLResolver):
                nested_urls = self.extract_urls(pattern.url_patterns, parent_pattern + str(pattern.pattern))
                urls.extend(nested_urls)
        return urls

    def get_view_detail(self, callback):
        if hasattr(callback, 'view_class'):
            # Class-based view
            view_class = callback.view_class
            return f'{view_class.__module__}.{view_class.__name__}.{callback.__name__}'
        else:
            # Function-based view
            return f'{callback.__module__}.{callback.__name__}'

        # Get the file and line number where the view is defined
        view_file = inspect.getfile(callback)
        view_lines = inspect.getsourcelines(callback)
        start_line = view_lines[1]
        end_line = start_line + len(view_lines[0]) - 1
        return f'{view_file} (lines {start_line}-{end_line})'
