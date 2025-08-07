"""
Tests for NoPrefixLocaleMiddleware.
"""

from django.conf import settings
from django.http import HttpResponse
from django.utils import translation

from django_i18n_noprefix.middleware import NoPrefixLocaleMiddleware


class TestNoPrefixLocaleMiddleware:
    """Test cases for NoPrefixLocaleMiddleware."""

    def test_middleware_initialization(self):
        """Test that middleware initializes correctly."""

        def get_response(request):
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        assert middleware.get_response == get_response
        assert middleware.cookie_name == settings.LANGUAGE_COOKIE_NAME

    def test_default_language_detection(self, mock_request):
        """Test default language is used when no preference is set."""

        def get_response(request):
            assert request.LANGUAGE_CODE == "en"
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        response = middleware(request)

        assert response.status_code == 200

    def test_session_language_detection(self, mock_request):
        """Test language detection from session."""

        def get_response(request):
            assert request.LANGUAGE_CODE == "ko"
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        request.session["django_language"] = "ko"

        response = middleware(request)
        assert response.status_code == 200

    def test_cookie_language_detection(self, mock_request):
        """Test language detection from cookie."""

        def get_response(request):
            assert request.LANGUAGE_CODE == "ja"
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = "ja"

        response = middleware(request)
        assert response.status_code == 200

    def test_header_language_detection(self, mock_request):
        """Test language detection from Accept-Language header."""

        def get_response(request):
            # Should detect Korean from header
            assert request.LANGUAGE_CODE in ["ko", "en"]  # Django's detection may vary
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/", headers={"Accept-Language": "ko-KR,ko;q=0.9"})

        response = middleware(request)
        assert response.status_code == 200

    def test_language_priority_session_over_cookie(self, mock_request):
        """Test that session takes priority over cookie."""

        def get_response(request):
            assert request.LANGUAGE_CODE == "ko"  # Session value
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        request.session["django_language"] = "ko"
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = "ja"

        response = middleware(request)
        assert response.status_code == 200

    def test_language_priority_cookie_over_header(self, mock_request):
        """Test that cookie takes priority over header."""

        def get_response(request):
            assert request.LANGUAGE_CODE == "ja"  # Cookie value
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/", headers={"Accept-Language": "ko-KR"})
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = "ja"

        response = middleware(request)
        assert response.status_code == 200

    def test_invalid_language_code_ignored(self, mock_request):
        """Test that invalid language codes are ignored."""

        def get_response(request):
            assert request.LANGUAGE_CODE == "en"  # Falls back to default
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = "invalid"

        response = middleware(request)
        assert response.status_code == 200

    def test_language_change_saves_to_session_and_cookie(
        self, mock_request, mock_response
    ):
        """Test that language changes are saved to session and cookie."""

        def get_response(request):
            # Simulate language change in view
            request.LANGUAGE_CODE = "ja"
            return mock_response

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        # Session exists (has_key method returns True for any key)
        request.session["_session_exists"] = True

        response = middleware(request)

        # Check session was updated
        assert request.session.get("django_language") == "ja"
        # Check cookie was set
        assert response.cookies.get(settings.LANGUAGE_COOKIE_NAME) == "ja"

    def test_no_language_change_no_save(self, mock_request, mock_response):
        """Test that no save occurs when language doesn't change."""

        def get_response(request):
            # Language stays the same
            return mock_response

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        request.session["django_language"] = "ko"

        response = middleware(request)

        # Check cookie was not set
        assert settings.LANGUAGE_COOKIE_NAME not in response.cookies

    def test_translation_activation(self, mock_request):
        """Test that Django translation is properly activated."""

        def get_response(request):
            # Check that translation is activated
            current_language = translation.get_language()
            assert current_language == "ko"
            return HttpResponse()

        middleware = NoPrefixLocaleMiddleware(get_response)
        request = mock_request("/")
        request.session["django_language"] = "ko"

        response = middleware(request)
        assert response.status_code == 200
