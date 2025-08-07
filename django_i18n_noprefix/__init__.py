"""
Django i18n without URL prefixes.

A Django package that provides internationalization (i18n) support without
adding language prefixes to URLs.
"""

__version__ = '0.1.0'
__author__ = 'jinto'
__email__ = ''
__license__ = 'MIT'

# Default app config
default_app_config = 'django_i18n_noprefix.apps.I18nNoPrefixConfig'

# Public API
from .middleware import NoPrefixLocaleMiddleware
from .utils import (
    activate_language,
    get_supported_languages,
    get_language_choices,
    is_valid_language,
    get_language_name,
    get_current_language,
    get_default_language,
)

__all__ = [
    'NoPrefixLocaleMiddleware',
    'activate_language',
    'get_supported_languages',
    'get_language_choices',
    'is_valid_language',
    'get_language_name',
    'get_current_language',
    'get_default_language',
]