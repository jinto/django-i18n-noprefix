"""
Django i18n without URL prefixes.

A Django package that provides internationalization (i18n) support without
adding language prefixes to URLs. This package complements Django's built-in
i18n functionality rather than replacing it.

For most i18n operations, use Django's built-in functions:
- `translation.get_language()` for current language
- `settings.LANGUAGES` for available languages  
- `translation.get_language_info()` for language details
"""

__version__ = '0.1.0'
__author__ = 'jinto'
__email__ = ''
__license__ = 'MIT'

# Default app config
default_app_config = 'django_i18n_noprefix.apps.I18nNoPrefixConfig'

# Public API - minimal, focused on our core functionality
from .middleware import NoPrefixLocaleMiddleware
from .utils import activate_language, is_valid_language

__all__ = [
    'NoPrefixLocaleMiddleware',
    'activate_language',
    'is_valid_language',
]