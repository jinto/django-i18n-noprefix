"""
Django settings for test project.
"""

from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings
SECRET_KEY = "django-insecure-test-key-for-testing-only"
DEBUG = True
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_i18n_noprefix",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Replace Django's LocaleMiddleware with our custom middleware
    "django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware",
]

ROOT_URLCONF = "tests.test_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "tests" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Languages configuration
LANGUAGES = [
    ("ko", "Korean"),
    ("en", "English"),
    ("ja", "Japanese"),
]

# Locale paths
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom settings for django-i18n-noprefix
I18N_NOPREFIX_DEFAULT_LANGUAGE = "en"
I18N_NOPREFIX_COOKIE_NAME = "django_language"
I18N_NOPREFIX_COOKIE_AGE = 365 * 24 * 60 * 60  # 1 year
I18N_NOPREFIX_COOKIE_PATH = "/"
I18N_NOPREFIX_COOKIE_DOMAIN = None
I18N_NOPREFIX_COOKIE_SECURE = False
I18N_NOPREFIX_COOKIE_HTTPONLY = False
I18N_NOPREFIX_COOKIE_SAMESITE = "Lax"
