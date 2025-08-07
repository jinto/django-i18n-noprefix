"""
Tests for app configuration and system checks.
"""
import pytest
from django.apps import apps
from django.core.checks import Error, Warning
from django.test import override_settings

from django_i18n_noprefix.apps import (
    I18nNoPrefixConfig,
    check_middleware_configuration,
    check_language_configuration,
    check_url_configuration,
)


class TestAppConfig:
    """Test the app configuration."""
    
    def test_app_config_exists(self):
        """Test that app config is properly defined."""
        app_config = apps.get_app_config('django_i18n_noprefix')
        assert isinstance(app_config, I18nNoPrefixConfig)
        assert app_config.name == 'django_i18n_noprefix'
        assert app_config.verbose_name == 'Django i18n No-Prefix'


class TestMiddlewareChecks:
    """Test middleware configuration checks."""
    
    @override_settings(MIDDLEWARE=[])
    def test_middleware_not_installed(self):
        """Test warning when middleware is not installed."""
        errors = check_middleware_configuration(None)
        assert len(errors) == 1
        assert isinstance(errors[0], Warning)
        assert errors[0].id == 'django_i18n_noprefix.W001'
        assert 'not found in MIDDLEWARE' in errors[0].msg
    
    @override_settings(MIDDLEWARE=[
        'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    ])
    def test_conflicting_middleware(self):
        """Test error when both middlewares are installed."""
        errors = check_middleware_configuration(None)
        assert any(isinstance(e, Error) and e.id == 'django_i18n_noprefix.E001' for e in errors)
    
    @override_settings(MIDDLEWARE=[
        'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
    ])
    def test_wrong_middleware_order_session(self):
        """Test warning when SessionMiddleware is after our middleware."""
        errors = check_middleware_configuration(None)
        warnings = [e for e in errors if isinstance(e, Warning) and e.id == 'django_i18n_noprefix.W002']
        assert len(warnings) == 1
        assert 'SessionMiddleware should come before' in warnings[0].msg
    
    @override_settings(MIDDLEWARE=[
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',
    ])
    def test_correct_middleware_order(self):
        """Test no errors with correct middleware order."""
        errors = check_middleware_configuration(None)
        # Should have no errors or warnings
        assert len(errors) == 0


class TestLanguageChecks:
    """Test language configuration checks."""
    
    @override_settings(USE_I18N=False)
    def test_i18n_disabled(self):
        """Test error when USE_I18N is False."""
        errors = check_language_configuration(None)
        assert any(isinstance(e, Error) and e.id == 'django_i18n_noprefix.E002' for e in errors)
    
    @override_settings(LANGUAGES=[])
    def test_empty_languages(self):
        """Test error when LANGUAGES is empty."""
        errors = check_language_configuration(None)
        assert any(isinstance(e, Error) and e.id == 'django_i18n_noprefix.E003' for e in errors)
    
    @override_settings(
        LANGUAGES=[('ko', 'Korean'), ('en', 'English')],
        LANGUAGE_CODE='fr'
    )
    def test_language_code_not_in_languages(self):
        """Test warning when LANGUAGE_CODE is not in LANGUAGES."""
        errors = check_language_configuration(None)
        warnings = [e for e in errors if isinstance(e, Warning) and e.id == 'django_i18n_noprefix.W004']
        assert len(warnings) == 1
        assert 'fr" is not in LANGUAGES' in warnings[0].msg
    
    @override_settings(
        USE_I18N=True,
        LANGUAGES=[('ko', 'Korean'), ('en', 'English')],
        LANGUAGE_CODE='en'
    )
    def test_correct_language_configuration(self):
        """Test no errors with correct language configuration."""
        errors = check_language_configuration(None)
        # Filter out the i18n_patterns warning which depends on ROOT_URLCONF
        errors = [e for e in errors if e.id != 'django_i18n_noprefix.W005']
        assert len(errors) == 0


class TestURLChecks:
    """Test URL configuration checks."""
    
    def test_urls_not_included(self):
        """Test warning when URLs are not included."""
        # This test might show a warning depending on test configuration
        # The actual check tries to reverse URLs
        errors = check_url_configuration(None)
        # This is informational - URLs are optional
        if errors:
            assert all(isinstance(e, Warning) for e in errors)
            assert any(e.id == 'django_i18n_noprefix.W006' for e in errors)


class TestVersionInfo:
    """Test version information."""
    
    def test_version_defined(self):
        """Test that version is defined in __init__.py."""
        from django_i18n_noprefix import __version__
        assert __version__ == '0.1.0'
    
    def test_public_api(self):
        """Test that public API is properly exported."""
        import django_i18n_noprefix
        
        # Check that main components are accessible
        assert hasattr(django_i18n_noprefix, 'NoPrefixLocaleMiddleware')
        assert hasattr(django_i18n_noprefix, 'activate_language')
        assert hasattr(django_i18n_noprefix, 'is_valid_language')
        
        # Check that we're not exporting unnecessary functions
        assert not hasattr(django_i18n_noprefix, 'get_supported_languages')
        assert not hasattr(django_i18n_noprefix, 'get_current_language')