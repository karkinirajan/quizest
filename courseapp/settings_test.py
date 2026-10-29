"""Settings for the test suite: debug on, in-memory DB, temp media, plain static storage."""

import os
import tempfile

os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("DJANGO_DEBUG", "true")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from .settings import *  # noqa: E402,F401,F403

ALLOWED_HOSTS = ["testserver", "localhost"]
MEDIA_ROOT = tempfile.mkdtemp(prefix="quizest-media-")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
MIDDLEWARE = [m for m in MIDDLEWARE if "whitenoise" not in m]  # noqa: F405
