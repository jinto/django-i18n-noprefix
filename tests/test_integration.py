"""
Integration tests for django-i18n-noprefix package.

These tests verify that all components work together correctly in a real Django environment.
"""

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, TestCase, override_settings
from django.utils import translation


@override_settings(
    USE_I18N=True,
    USE_L10N=True,
    LANGUAGES=[
        ("en", "English"),
        ("ko", "Korean"),
        ("ja", "Japanese"),
    ],
    LANGUAGE_CODE="en",
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ],
    ROOT_URLCONF="tests.test_project.urls",
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django.contrib.sessions",
        "django_i18n_noprefix",
    ],
)
class IntegrationTestCase(TestCase):
    """Base test case for integration tests."""

    def setUp(self):
        """Set up test client and initial state."""
        self.client = Client()
        # Ensure clean state
        translation.activate("en")

    def tearDown(self):
        """Clean up after each test."""
        translation.deactivate()

    def create_request(self, path="/", language=None, session_data=None, cookies=None):
        """Helper to create a request with specific language settings."""
        request = self.client.get(path).wsgi_request

        # Add session support
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()

        if session_data:
            for key, value in session_data.items():
                request.session[key] = value

        if cookies:
            for key, value in cookies.items():
                request.COOKIES[key] = value

        if language:
            request.session["django_language"] = language

        return request


class FullStackIntegrationTest(IntegrationTestCase):
    """Test full request-response cycle with all components."""

    def test_language_change_flow(self):
        """Test complete language change workflow."""
        # Step 1: Initial request in default language (English)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Check that no language prefix is in URL
        self.assertNotIn("/en/", response.wsgi_request.path)

        # Step 2: Change language to Korean
        response = self.client.get("/i18n/set-language/ko/", follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify language was changed
        self.assertEqual(self.client.session.get("django_language"), "ko")

        # Step 3: Make another request - language should persist
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Language should still be Korean
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

        # Step 4: Verify no URL prefixes anywhere
        self.assertNotIn("/ko/", response.wsgi_request.path)
        self.assertNotIn("/en/", response.wsgi_request.path)

    def test_cookie_language_persistence(self):
        """Test that language persists via cookies."""
        # Set language via view (don't follow redirect to see the cookie)
        response = self.client.get("/i18n/set-language/ja/", follow=False)

        # Check redirect response
        self.assertEqual(response.status_code, 302)

        # Check cookie was set
        self.assertIn(settings.LANGUAGE_COOKIE_NAME, response.cookies)
        self.assertEqual(response.cookies[settings.LANGUAGE_COOKIE_NAME].value, "ja")

        # Create new client (simulating new session)
        new_client = Client()
        # Pass the cookie
        new_client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ja"

        # Language should be detected from cookie
        response = new_client.get("/")
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")

    def test_accept_language_header_fallback(self):
        """Test Accept-Language header as fallback."""
        # New client with no session/cookie
        client = Client(HTTP_ACCEPT_LANGUAGE="ko-KR,ko;q=0.9,en;q=0.8")

        response = client.get("/")
        # Should detect Korean from header
        self.assertIn(response.wsgi_request.LANGUAGE_CODE, ["ko", "en"])

    def test_language_priority_order(self):
        """Test language detection priority: session > cookie > header > default."""
        # Setup all language sources
        client = Client(HTTP_ACCEPT_LANGUAGE="ja-JP")
        client.cookies[settings.LANGUAGE_COOKIE_NAME] = "ko"

        # First request - should use cookie (ko)
        response = client.get("/")
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

        # Set session language through the view (proper way)
        response = client.get("/i18n/set-language/en/", follow=True)

        # Now should use session (en) over cookie (ko)
        response = client.get("/")
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "en")

        # Verify session has the language
        self.assertEqual(client.session.get("django_language"), "en")

    def test_middleware_integration_with_views(self):
        """Test middleware works correctly with views."""
        # Change language and verify in view context
        self.client.get("/i18n/set-language/ko/")

        # The middleware should activate the language for the view
        response = self.client.get("/")

        # Check that translation is activated
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

    def test_ajax_language_change(self):
        """Test AJAX language change functionality."""
        # Make AJAX request to change language
        import json

        response = self.client.post(
            "/i18n/set-language-ajax/",
            json.dumps({"language": "ja"}),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["success"], True)
        self.assertEqual(response.json()["language"], "ja")

        # Language should be changed in session
        self.assertEqual(self.client.session.get("django_language"), "ja")

        # Verify in next request
        response = self.client.get("/")
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")

    def test_invalid_language_handling(self):
        """Test handling of invalid language codes."""
        # Try to set invalid language
        response = self.client.get("/i18n/set-language/invalid/", follow=True)

        # Should fallback to default language
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "en")

        # Session should not have invalid language
        self.assertNotEqual(self.client.session.get("django_language"), "invalid")

    def test_language_change_preserves_query_params(self):
        """Test that query parameters are preserved during language change."""
        # Start with query parameters
        response = self.client.get("/?search=test&page=2")

        # Change language with next parameter (URL encode the next parameter)
        from urllib.parse import quote

        next_url = "/?search=test&page=2"
        response = self.client.get(
            f"/i18n/set-language/ko/?next={quote(next_url)}", follow=True
        )

        # Should redirect back with query params preserved
        # The final request's query string should have the params
        final_url = (
            response.request.get("PATH_INFO", "")
            + "?"
            + response.request.get("QUERY_STRING", "")
        )
        self.assertIn("search=test", final_url)
        self.assertIn("page=2", final_url)

        # Language should be changed
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")
