"""
Simple static files storage that never uses manifests.
"""
from django.contrib.staticfiles.storage import StaticFilesStorage


class SimpleStaticFilesStorage(StaticFilesStorage):
    """
    A simple static files storage that just returns the URL directly.
    No manifest, no hashing, no complexity.
    """

    def url(self, name):
        """Return the URL for the given file name without any manifest lookup."""
        from django.conf import settings
        from urllib.parse import urljoin
        return urljoin(settings.STATIC_URL, name)
