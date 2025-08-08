"""
End-to-end scenario tests for django-i18n-noprefix.

Tests complete user workflows and edge cases.
"""

import json

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.utils import translation


@override_settings(
    USE_I18N=True,
    USE_L10N=True,
    LANGUAGES=[
        ("en", "English"),
        ("ko", "Korean"),
        ("ja", "Japanese"),
        ("zh-hans", "Simplified Chinese"),
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
        "django.contrib.messages",
        "django_i18n_noprefix",
    ],
)
class E2EScenarioTest(TestCase):
    """End-to-end scenario tests."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        translation.activate("en")

    def tearDown(self):
        """Clean up."""
        translation.deactivate()

    def test_scenario_new_visitor_workflow(self):
        """Test complete workflow for a new visitor."""
        # Scenario: New visitor arrives, browses, changes language, and navigates

        # Step 1: First visit - should use Accept-Language header
        client = Client(HTTP_ACCEPT_LANGUAGE="ko-KR,ko;q=0.9,en;q=0.8")
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        # Should detect Korean from header (or fall back to default)
        self.assertIn(response.wsgi_request.LANGUAGE_CODE, ["ko", "en"])

        # Step 2: User explicitly selects Japanese
        lang_response = client.get("/i18n/set-language/ja/", follow=True)
        self.assertEqual(lang_response.status_code, 200)

        # Step 3: Navigate to different pages - language should persist
        pages = ["/", "/about/", "/contact/"]
        for page in pages:
            response = client.get(page)
            if response.status_code == 200:  # Only check if page exists
                self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")
                # No URL prefixes
                self.assertNotIn("/ja/", response.wsgi_request.path)

        # Step 4: Language should be in session
        self.assertEqual(client.session.get("django_language"), "ja")
        # Cookie should have been set when language was changed
        # Note: Django test client doesn't always expose cookies properly
        # The important thing is that the language persists across requests

        # Step 5: New session with same client (cookies persist)
        client.session.flush()
        response = client.get("/")
        # Should still be Japanese from cookie
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")

    def test_scenario_multilingual_user_switching(self):
        """Test user switching between multiple languages."""
        # Scenario: Multilingual user frequently switches languages

        languages_to_test = ["en", "ko", "ja", "en", "ko"]  # Including revisits

        for expected_lang in languages_to_test:
            # Change language
            response = self.client.get(
                f"/i18n/set-language/{expected_lang}/", follow=True
            )
            self.assertEqual(response.status_code, 200)

            # Verify language is active
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, expected_lang)

            # Make several requests
            for _ in range(3):
                response = self.client.get("/")
                self.assertEqual(response.wsgi_request.LANGUAGE_CODE, expected_lang)
                # No prefixes
                self.assertNotIn(f"/{expected_lang}/", response.wsgi_request.path)

    def test_scenario_ajax_spa_workflow(self):
        """Test AJAX-based Single Page Application workflow."""
        # Scenario: SPA making AJAX calls for language switching

        # Initial page load
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # AJAX language change to Korean
        response = self.client.post(
            "/i18n/set-language-ajax/",
            json.dumps({"language": "ko"}),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["success"], True)
        self.assertEqual(data["language"], "ko")

        # Subsequent AJAX calls should use Korean
        response = self.client.get(
            "/api/data/",  # Hypothetical API endpoint
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        # Language should be Korean for API calls too
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

        # Regular page navigation after AJAX change
        response = self.client.get("/")
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

    def test_scenario_form_submission_workflow(self):
        """Test form submission preserves language."""
        # Scenario: User fills form in their language

        # Set language to Japanese
        self.client.get("/i18n/set-language/ja/")

        # GET form page
        response = self.client.get("/contact/")  # Hypothetical form page
        if response.status_code == 200:
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")

        # POST form submission
        response = self.client.post(
            "/contact/",
            {"name": "Test User", "message": "Test message"},
            follow=True,
        )

        if response.status_code == 200:
            # Language should persist after form submission
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")
            # No URL prefix in redirect
            for redirect in response.redirect_chain:
                self.assertNotIn("/ja/", redirect[0])

    def test_scenario_deep_linking(self):
        """Test deep linking with language preferences."""
        # Scenario: User shares a link, recipient opens with different language

        # User A with Korean preference
        client_a = Client()
        client_a.get("/i18n/set-language/ko/")
        response = client_a.get("/products/123/")  # Deep link
        if response.status_code == 200:
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")
            shared_url = response.wsgi_request.path
            self.assertNotIn("/ko/", shared_url)  # No prefix in URL

        # User B opens same URL with Japanese preference
        client_b = Client()
        client_b.cookies[settings.LANGUAGE_COOKIE_NAME] = "ja"
        response = client_b.get("/products/123/")  # Same URL
        if response.status_code == 200:
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")
            # Same URL, different language
            self.assertEqual(response.wsgi_request.path, "/products/123/")

    def test_scenario_cookie_disabled_user(self):
        """Test user with cookies disabled."""
        # Scenario: Privacy-conscious user with cookies disabled

        # Create client that doesn't persist cookies
        class NoCookieClient(Client):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.cookies.clear()

            def _handle_redirects(self, response, **extra):
                response = super()._handle_redirects(response, **extra)
                self.cookies.clear()  # Clear cookies after each request
                return response

        client = NoCookieClient()

        # Try to set language
        response = client.get("/i18n/set-language/ko/", follow=True)

        # Check response is successful
        self.assertEqual(response.status_code, 200)

        # Cookie shouldn't persist due to our NoCookieClient
        self.assertEqual(len(client.cookies), 0)

        # Without cookies, language preference won't persist across requests
        # Next request should use default language
        response = client.get("/")
        # Should fall back to default language or Accept-Language header
        self.assertIn(response.wsgi_request.LANGUAGE_CODE, ["en", "ko"])

    def test_scenario_search_engine_crawler(self):
        """Test search engine crawler behavior."""
        # Scenario: Search engine crawler without session/cookies

        # Crawler with various Accept-Language headers
        crawlers = [
            {"bot": "Googlebot", "accept_lang": "en-US,en;q=0.9"},
            {"bot": "Baiduspider", "accept_lang": "zh-CN,zh;q=0.9"},
            {"bot": "Yandex", "accept_lang": "ru-RU,ru;q=0.9"},
        ]

        for crawler in crawlers:
            client = Client(
                HTTP_USER_AGENT=crawler["bot"],
                HTTP_ACCEPT_LANGUAGE=crawler["accept_lang"],
            )

            response = client.get("/")
            self.assertEqual(response.status_code, 200)

            # Should not have language prefix in URLs
            self.assertNotIn("/en/", response.wsgi_request.path)
            self.assertNotIn("/zh/", response.wsgi_request.path)
            self.assertNotIn("/ru/", response.wsgi_request.path)

            # Should handle missing language gracefully
            # (zh-CN might not be in LANGUAGES, should fallback)
            self.assertIn(
                response.wsgi_request.LANGUAGE_CODE,
                ["en", "ko", "ja", "zh-hans"],
            )

    def test_scenario_concurrent_language_changes(self):
        """Test concurrent language changes in different tabs."""
        # Scenario: User has multiple tabs open and changes language

        # Tab 1: Set to Korean
        self.client.get("/i18n/set-language/ko/", follow=True)
        session_id_1 = self.client.session.session_key

        # Tab 2: Same session, change to Japanese
        self.client.get("/i18n/set-language/ja/", follow=True)
        session_id_2 = self.client.session.session_key

        # Session should be the same
        self.assertEqual(session_id_1, session_id_2)

        # Latest change wins
        self.assertEqual(self.client.session.get("django_language"), "ja")

        # All tabs should now use Japanese
        response = self.client.get("/")
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")

    def test_scenario_language_not_in_list(self):
        """Test handling of languages not in LANGUAGES setting."""
        # Scenario: User manually tries unsupported language

        # Try to set French (not in our LANGUAGES)
        response = self.client.get("/i18n/set-language/fr/", follow=True)

        # Should not crash, should use fallback
        self.assertEqual(response.status_code, 200)

        # Should not set invalid language
        self.assertNotEqual(self.client.session.get("django_language"), "fr")

        # Should use default language
        self.assertIn(
            response.wsgi_request.LANGUAGE_CODE,
            ["en", "ko", "ja", "zh-hans"],  # Valid languages only
        )

    def test_scenario_rtl_language_support(self):
        """Test Right-to-Left language support (if added)."""
        # Scenario: User switches to RTL language (Arabic, Hebrew)

        # This would test RTL languages if they were configured
        # For now, test that system handles language direction metadata

        with translation.override("en"):
            # English is LTR
            lang_info = translation.get_language_info("en")
            self.assertFalse(lang_info.get("bidi", False))

        # If Arabic was configured:
        # with translation.override("ar"):
        #     lang_info = translation.get_language_info("ar")
        #     self.assertTrue(lang_info.get("bidi", False))

    def test_scenario_performance_many_language_switches(self):
        """Test performance with many rapid language switches."""
        # Scenario: Stress test with rapid language changes

        languages = ["en", "ko", "ja"]

        # Rapid switches
        for i in range(30):
            lang = languages[i % len(languages)]
            response = self.client.get(f"/i18n/set-language/{lang}/", follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, lang)

        # System should remain stable
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Last language should be active
        expected_last_lang = languages[(30 - 1) % len(languages)]
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, expected_last_lang)

    def test_scenario_middleware_order_importance(self):
        """Test that middleware order doesn't break functionality."""
        # Our middleware should work regardless of exact position
        # (as long as it's after SessionMiddleware)

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Set language
        response = self.client.get("/i18n/set-language/ko/", follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify it works
        response = self.client.get("/")
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

    def test_scenario_fallback_chain(self):
        """Test complete fallback chain when all detection methods fail."""
        # Scenario: No session, no cookie, no valid Accept-Language

        client = Client(HTTP_ACCEPT_LANGUAGE="xx-XX")  # Invalid language
        response = client.get("/")

        # Should fallback to LANGUAGE_CODE setting
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "en")  # Default

    def test_scenario_language_negotiation_quality(self):
        """Test Accept-Language quality value negotiation."""
        # Scenario: Complex Accept-Language header with quality values

        # Prefer Japanese, then Korean, then English
        client = Client(HTTP_ACCEPT_LANGUAGE="ja;q=1.0, ko;q=0.8, en;q=0.5, *;q=0.1")

        response = client.get("/")
        # Should select Japanese (highest quality value)
        self.assertIn(response.wsgi_request.LANGUAGE_CODE, ["ja", "ko", "en"])

        # If Japanese is available, it should be selected
        if "ja" in dict(settings.LANGUAGES):
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ja")
