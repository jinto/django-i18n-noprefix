"""
Tests for utility functions.
"""
import pytest
from django.conf import settings
from django.utils import translation

from django_i18n_noprefix.utils import (
    activate_language,
    get_supported_languages,
    get_language_choices,
    is_valid_language,
    get_language_name,
    get_current_language,
    get_default_language,
    get_accept_language_header,
    parse_accept_language_header,
    get_best_matching_language,
)


class TestLanguageUtilities:
    """Test language utility functions."""
    
    def test_activate_language_valid(self, mock_request):
        """Test activating a valid language."""
        request = mock_request('/')
        result = activate_language(request, 'ko')
        
        assert result is True
        assert request.LANGUAGE_CODE == 'ko'
        assert translation.get_language() == 'ko'
    
    def test_activate_language_invalid(self, mock_request):
        """Test activating an invalid language."""
        request = mock_request('/')
        result = activate_language(request, 'invalid')
        
        assert result is False
        assert not hasattr(request, 'LANGUAGE_CODE') or request.LANGUAGE_CODE != 'invalid'
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) == 3
        assert ('ko', 'Korean') in languages
        assert ('en', 'English') in languages
        assert ('ja', 'Japanese') in languages
    
    def test_get_language_choices(self):
        """Test getting language choices for forms."""
        choices = get_language_choices()
        
        # Should be the same as get_supported_languages
        assert choices == get_supported_languages()
    
    def test_is_valid_language(self):
        """Test language validation."""
        assert is_valid_language('ko') is True
        assert is_valid_language('en') is True
        assert is_valid_language('ja') is True
        assert is_valid_language('invalid') is False
        assert is_valid_language('') is False
        assert is_valid_language('fr') is False  # Not in settings
    
    def test_get_language_name(self):
        """Test getting language name."""
        assert get_language_name('ko') == 'Korean'
        assert get_language_name('en') == 'English'
        assert get_language_name('ja') == 'Japanese'
        assert get_language_name('invalid') is None
        assert get_language_name('') is None
    
    def test_get_current_language_from_request(self, mock_request):
        """Test getting current language from request."""
        request = mock_request('/')
        request.LANGUAGE_CODE = 'ko'
        
        assert get_current_language(request) == 'ko'
    
    def test_get_current_language_fallback(self, mock_request):
        """Test getting current language with fallback."""
        request = mock_request('/')
        # No LANGUAGE_CODE set on request
        
        # Should fall back to Django's get_language()
        translation.activate('ja')
        assert get_current_language(request) == 'ja'
    
    def test_get_default_language(self):
        """Test getting default language."""
        # Should return the settings value
        assert get_default_language() == 'en'
    
    def test_get_accept_language_header(self, mock_request):
        """Test getting Accept-Language header."""
        # With header
        request = mock_request('/', headers={'Accept-Language': 'ko-KR,ko;q=0.9'})
        assert get_accept_language_header(request) == 'ko-KR,ko;q=0.9'
        
        # Without header
        request = mock_request('/')
        assert get_accept_language_header(request) is None
    
    def test_parse_accept_language_header(self):
        """Test parsing Accept-Language header."""
        # Complex header
        header = 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6'
        parsed = parse_accept_language_header(header)
        
        assert parsed == [
            ('ko-KR', 1.0),
            ('ko', 0.9),
            ('en-US', 0.8),
            ('en', 0.7),
            ('ja', 0.6),
        ]
        
        # Simple header
        header = 'en'
        parsed = parse_accept_language_header(header)
        assert parsed == [('en', 1.0)]
        
        # Empty header
        parsed = parse_accept_language_header('')
        assert parsed == []
        
        # None header
        parsed = parse_accept_language_header(None)
        assert parsed == []
        
        # Invalid quality value
        header = 'ko;q=invalid,en;q=0.5'
        parsed = parse_accept_language_header(header)
        assert parsed == [('ko', 1.0), ('en', 0.5)]
    
    def test_get_best_matching_language(self):
        """Test getting best matching language from header."""
        # Exact match
        header = 'ko,en;q=0.8'
        assert get_best_matching_language(header) == 'ko'
        
        # Regional variant match
        header = 'ko-KR,en-US;q=0.8'
        assert get_best_matching_language(header) == 'ko'
        
        # Fallback to second choice
        header = 'fr,en;q=0.8'
        assert get_best_matching_language(header) == 'en'
        
        # No match
        header = 'fr,de,es'
        assert get_best_matching_language(header) is None
        
        # Empty header
        assert get_best_matching_language('') is None
        
        # Complex real-world header
        header = 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6'
        assert get_best_matching_language(header) == 'ko'
    
    def test_parse_accept_language_header_edge_cases(self):
        """Test edge cases in Accept-Language parsing."""
        # Spaces around values
        header = ' ko-KR , ko ; q=0.9 , en ; q=0.8 '
        parsed = parse_accept_language_header(header)
        assert parsed[0] == ('ko-KR', 1.0)
        assert parsed[1] == ('ko', 0.9)
        assert parsed[2] == ('en', 0.8)
        
        # Multiple semicolons
        header = 'ko;;q=0.9'
        parsed = parse_accept_language_header(header)
        assert parsed == [('ko', 0.9)]
        
        # Quality value > 1 (should be capped at 1.0 by HTTP spec, but we accept it)
        header = 'ko;q=1.5'
        parsed = parse_accept_language_header(header)
        assert parsed == [('ko', 1.5)]  # We don't validate the range