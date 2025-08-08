"""
Integration tests for Django's reverse() function with no-prefix i18n.

Tests that URL reversing works correctly without language prefixes.
"""

from django.test import Client, TestCase, override_settings
from django.urls import resolve, reverse
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
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
    ],
    ROOT_URLCONF="tests.test_project.urls",
    INSTALLED_APPS=[
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django.contrib.sessions",
        "django_i18n_noprefix",
    ],
)
class ReverseIntegrationTest(TestCase):
    """Test reverse() function without URL prefixes."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        translation.activate("en")

    def tearDown(self):
        """Clean up."""
        translation.deactivate()

    def test_reverse_no_language_prefix(self):
        """Test that reverse() doesn't add language prefixes."""
        # Test with different active languages
        for lang_code in ["en", "ko", "ja"]:
            with translation.override(lang_code):
                # Reverse URL should not contain language prefix
                url = reverse("home")
                self.assertNotIn(f"/{lang_code}/", url)
                self.assertEqual(url, "/")

                # Test with named URL
                url = reverse("i18n:set-language", kwargs={"lang_code": "ko"})
                self.assertNotIn(f"/{lang_code}/", url)
                self.assertEqual(url, "/i18n/set-language/ko/")

    def test_reverse_consistency_across_languages(self):
        """Test that URLs remain consistent across language changes."""
        # Get URL in English
        with translation.override("en"):
            url_en = reverse("home")

        # Get URL in Korean
        with translation.override("ko"):
            url_ko = reverse("home")

        # Get URL in Japanese
        with translation.override("ja"):
            url_ja = reverse("home")

        # All URLs should be identical (no prefixes)
        self.assertEqual(url_en, url_ko)
        self.assertEqual(url_ko, url_ja)
        self.assertEqual(url_en, "/")

    def test_reverse_with_arguments(self):
        """Test reverse() with URL arguments."""
        # Test URL with arguments
        for lang_code in ["en", "ko", "ja"]:
            with translation.override(lang_code):
                url = reverse("i18n:set-language", args=["ko"])
                self.assertEqual(url, "/i18n/set-language/ko/")
                self.assertNotIn(f"/{lang_code}/", url)

    def test_reverse_with_kwargs(self):
        """Test reverse() with keyword arguments."""
        # Test URL with kwargs
        for lang_code in ["en", "ko", "ja"]:
            with translation.override(lang_code):
                url = reverse("i18n:set-language", kwargs={"lang_code": "ja"})
                self.assertEqual(url, "/i18n/set-language/ja/")
                self.assertNotIn(f"/{lang_code}/", url)

    def test_reverse_in_request_context(self):
        """Test reverse() within actual request context."""
        # Make request with Korean language
        self.client.session["django_language"] = "ko"
        self.client.session.save()

        response = self.client.get("/")

        # In the request context, reverse should still work without prefixes
        with translation.override(response.wsgi_request.LANGUAGE_CODE):
            url = reverse("home")
            self.assertEqual(url, "/")
            self.assertNotIn("/ko/", url)

    def test_resolve_without_prefix(self):
        """Test that resolve() works for URLs without language prefix."""
        # Test resolving URLs without prefixes
        resolver_match = resolve("/")
        self.assertEqual(resolver_match.url_name, "home")

        resolver_match = resolve("/i18n/set-language/ko/")
        self.assertEqual(resolver_match.url_name, "set-language")
        self.assertEqual(resolver_match.kwargs["lang_code"], "ko")

    def test_reverse_with_query_string(self):
        """Test that reverse() handles query strings correctly."""
        # reverse() doesn't handle query strings directly, but we can build them
        base_url = reverse("home")
        full_url = f"{base_url}?search=test&page=2"

        # Verify no language prefix in base URL
        self.assertEqual(base_url, "/")
        self.assertNotIn("/en/", full_url)
        self.assertNotIn("/ko/", full_url)

    def test_reverse_after_language_change(self):
        """Test reverse() after changing language via middleware."""
        # Initial request in English
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # Change to Korean
        response = self.client.get("/i18n/set-language/ko/", follow=True)

        # Now test reverse in Korean context
        with translation.override("ko"):
            url = reverse("home")
            self.assertEqual(url, "/")
            self.assertNotIn("/ko/", url)

            # Test another URL
            url = reverse("i18n:set-language-ajax")
            self.assertEqual(url, "/i18n/set-language-ajax/")
            self.assertNotIn("/ko/", url)

    def test_reverse_lazy_compatibility(self):
        """Test that reverse_lazy works correctly."""
        from django.urls import reverse_lazy

        # Test with reverse_lazy (often used in class-based views)
        for lang_code in ["en", "ko", "ja"]:
            with translation.override(lang_code):
                url = str(reverse_lazy("home"))
                self.assertEqual(url, "/")
                self.assertNotIn(f"/{lang_code}/", url)

    def test_build_absolute_uri_without_prefix(self):
        """Test building absolute URIs without language prefixes."""
        request = self.client.get("/").wsgi_request

        # Build absolute URI
        absolute_uri = request.build_absolute_uri(reverse("home"))

        # Should not contain language prefix
        self.assertIn("http://testserver/", absolute_uri)
        self.assertNotIn("/en/", absolute_uri)
        self.assertNotIn("/ko/", absolute_uri)

    def test_named_url_patterns(self):
        """Test that named URL patterns work correctly."""
        # Test all our named patterns
        named_patterns = [
            ("home", "/"),
            ("i18n:set-language-ajax", "/i18n/set-language-ajax/"),
        ]

        for name, expected_url in named_patterns:
            with translation.override("ko"):
                url = reverse(name)
                self.assertEqual(url, expected_url)
                self.assertNotIn("/ko/", url)

    def test_app_namespace_urls(self):
        """Test URLs with app namespace."""
        # Our i18n URLs use namespace
        url = reverse("i18n:set-language", kwargs={"lang_code": "ja"})
        self.assertEqual(url, "/i18n/set-language/ja/")

        # No language prefix should be added
        for lang in ["en", "ko", "ja"]:
            with translation.override(lang):
                url = reverse("i18n:set-language", kwargs={"lang_code": "en"})
                self.assertEqual(url, "/i18n/set-language/en/")
                self.assertNotIn(f"/{lang}/", url)
