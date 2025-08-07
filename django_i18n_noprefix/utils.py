"""
Utility functions for django-i18n-noprefix.
"""
from typing import List, Tuple, Optional

from django.conf import settings
from django.http import HttpRequest
from django.utils import translation


def activate_language(request: HttpRequest, lang_code: str) -> bool:
    """
    Activate a language for the current request.
    
    This is a convenience function to use in views when you need to
    change the language programmatically.
    
    Args:
        request: The HTTP request object
        lang_code: The language code to activate
    
    Returns:
        True if the language was activated, False if invalid
    
    Example:
        >>> activate_language(request, 'ko')
        True
    """
    if is_valid_language(lang_code):
        translation.activate(lang_code)
        request.LANGUAGE_CODE = lang_code
        return True
    return False


def get_supported_languages() -> List[Tuple[str, str]]:
    """
    Get the list of supported languages from Django settings.
    
    Returns:
        List of tuples containing (language_code, language_name)
    
    Example:
        >>> get_supported_languages()
        [('ko', 'Korean'), ('en', 'English'), ('ja', 'Japanese')]
    """
    return list(settings.LANGUAGES)


def get_language_choices() -> List[Tuple[str, str]]:
    """
    Get language choices suitable for form fields.
    
    This is an alias for get_supported_languages() but indicates
    the intended use for Django form ChoiceField.
    
    Returns:
        List of tuples containing (language_code, language_name)
    
    Example:
        >>> from django import forms
        >>> class LanguageForm(forms.Form):
        ...     language = forms.ChoiceField(choices=get_language_choices())
    """
    return get_supported_languages()


def is_valid_language(lang_code: str) -> bool:
    """
    Check if a language code is valid (exists in LANGUAGES setting).
    
    Args:
        lang_code: The language code to validate
    
    Returns:
        True if the language code is valid, False otherwise
    
    Example:
        >>> is_valid_language('ko')
        True
        >>> is_valid_language('invalid')
        False
    """
    available_languages = [lang[0] for lang in settings.LANGUAGES]
    return lang_code in available_languages


def get_language_name(lang_code: str) -> Optional[str]:
    """
    Get the human-readable name for a language code.
    
    Args:
        lang_code: The language code
    
    Returns:
        The language name if found, None otherwise
    
    Example:
        >>> get_language_name('ko')
        'Korean'
        >>> get_language_name('invalid')
        None
    """
    for code, name in settings.LANGUAGES:
        if code == lang_code:
            return name
    return None


def get_current_language(request: HttpRequest) -> str:
    """
    Get the current active language for the request.
    
    This is a convenience wrapper around Django's get_language()
    that ensures consistency with our middleware.
    
    Args:
        request: The HTTP request object
    
    Returns:
        The current language code
    
    Example:
        >>> get_current_language(request)
        'ko'
    """
    # First check if the request has LANGUAGE_CODE set by our middleware
    if hasattr(request, 'LANGUAGE_CODE'):
        return request.LANGUAGE_CODE
    
    # Fallback to Django's get_language()
    return translation.get_language() or settings.LANGUAGE_CODE


def get_default_language() -> str:
    """
    Get the default language from settings.
    
    Returns:
        The default language code
    
    Example:
        >>> get_default_language()
        'en'
    """
    return getattr(
        settings,
        'I18N_NOPREFIX_DEFAULT_LANGUAGE',
        settings.LANGUAGE_CODE
    )


def get_accept_language_header(request: HttpRequest) -> Optional[str]:
    """
    Get the Accept-Language header from the request.
    
    Args:
        request: The HTTP request object
    
    Returns:
        The Accept-Language header value if present, None otherwise
    
    Example:
        >>> get_accept_language_header(request)
        'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    """
    return request.META.get('HTTP_ACCEPT_LANGUAGE')


def parse_accept_language_header(header: str) -> List[Tuple[str, float]]:
    """
    Parse the Accept-Language header into a list of (language, quality) tuples.
    
    Args:
        header: The Accept-Language header value
    
    Returns:
        List of tuples containing (language_code, quality_value)
        sorted by quality value in descending order
    
    Example:
        >>> parse_accept_language_header('ko-KR,ko;q=0.9,en-US;q=0.8')
        [('ko-KR', 1.0), ('ko', 0.9), ('en-US', 0.8)]
    """
    if not header:
        return []
    
    languages = []
    for item in header.split(','):
        parts = item.strip().split(';')
        lang = parts[0].strip()
        
        # Extract quality value
        quality = 1.0
        for part in parts[1:]:
            if part.strip().startswith('q='):
                try:
                    quality = float(part.strip()[2:])
                except ValueError:
                    quality = 1.0
                break
        
        languages.append((lang, quality))
    
    # Sort by quality value (descending)
    languages.sort(key=lambda x: x[1], reverse=True)
    return languages


def get_best_matching_language(accept_header: str) -> Optional[str]:
    """
    Get the best matching language from Accept-Language header.
    
    This function parses the Accept-Language header and returns
    the first language that matches one of the supported languages.
    
    Args:
        accept_header: The Accept-Language header value
    
    Returns:
        The best matching language code if found, None otherwise
    
    Example:
        >>> get_best_matching_language('ko-KR,ko;q=0.9,en-US;q=0.8')
        'ko'
    """
    parsed_languages = parse_accept_language_header(accept_header)
    supported_languages = [lang[0] for lang in settings.LANGUAGES]
    
    for lang_code, _ in parsed_languages:
        # Try exact match first
        if lang_code in supported_languages:
            return lang_code
        
        # Try language code without region (e.g., 'ko' from 'ko-KR')
        if '-' in lang_code:
            base_lang = lang_code.split('-')[0]
            if base_lang in supported_languages:
                return base_lang
    
    return None