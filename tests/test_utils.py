"""
Tests for utility functions.
"""
import pytest
from django.conf import settings
from django.utils import translation

from django_i18n_noprefix.utils import activate_language, is_valid_language


class TestActivateLanguage:
    """Test the activate_language helper function."""
    
    def test_activate_valid_language(self, mock_request):
        """Test activating a valid language."""
        request = mock_request('/')
        result = activate_language(request, 'ko')
        
        assert result is True
        assert request.LANGUAGE_CODE == 'ko'
        assert translation.get_language() == 'ko'
    
    def test_activate_invalid_language(self, mock_request):
        """Test activating an invalid language."""
        request = mock_request('/')
        result = activate_language(request, 'invalid')
        
        assert result is False
        assert not hasattr(request, 'LANGUAGE_CODE') or request.LANGUAGE_CODE != 'invalid'
    
    def test_activate_empty_language(self, mock_request):
        """Test activating an empty language code."""
        request = mock_request('/')
        result = activate_language(request, '')
        
        assert result is False


class TestIsValidLanguage:
    """Test the is_valid_language function."""
    
    def test_valid_languages(self):
        """Test validation of configured languages."""
        assert is_valid_language('ko') is True
        assert is_valid_language('en') is True
        assert is_valid_language('ja') is True
    
    def test_invalid_languages(self):
        """Test validation of invalid language codes."""
        assert is_valid_language('invalid') is False
        assert is_valid_language('') is False
        assert is_valid_language('fr') is False  # Not in test settings
        assert is_valid_language('xx') is False
    
    def test_case_sensitivity(self):
        """Test that language codes are case-sensitive."""
        assert is_valid_language('KO') is False  # Should be lowercase
        assert is_valid_language('EN') is False
        assert is_valid_language('Ko') is False