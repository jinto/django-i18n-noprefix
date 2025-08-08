"""
Integration tests for i18n translation system with django-i18n-noprefix.

Tests that Django's translation system works correctly without URL prefixes.
"""

from unittest.mock import patch

from django.contrib.sessions.middleware import SessionMiddleware
from django.template import Context, Template
from django.test import Client, TestCase, override_settings
from django.utils import translation
from django.utils.translation import (
    get_language,
    get_language_from_request,
    get_language_info,
    gettext,
    gettext_lazy,
    ngettext,
    pgettext,
)

from django_i18n_noprefix.middleware import NoPrefixLocaleMiddleware


@override_settings(
    USE_I18N=True,
    USE_L10N=True,
    LANGUAGES=[
        ("en", "English"),
        ("ko", "Korean"),
        ("ja", "Japanese"),
    ],
    LANGUAGE_CODE="en",
    LOCALE_PATHS=[],  # We'll use mock translations
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
class I18nIntegrationTest(TestCase):
    """Test i18n translation system integration."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        translation.activate("en")

    def tearDown(self):
        """Clean up."""
        translation.deactivate()

    def test_translation_activation_via_middleware(self):
        """Test that middleware activates correct translation."""
        # Set Korean in session
        self.client.session["django_language"] = "ko"
        self.client.session.save()

        # Make request
        response = self.client.get("/")

        # Check that Korean was activated
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

        # During request, get_language should return Korean
        with translation.override("ko"):
            self.assertEqual(get_language(), "ko")

    def test_gettext_with_language_change(self):
        """Test gettext functions work with language changes."""
        # Mock translations for testing
        translations = {
            "en": {"Hello": "Hello", "Welcome": "Welcome"},
            "ko": {"Hello": "안녕하세요", "Welcome": "환영합니다"},
            "ja": {"Hello": "こんにちは", "Welcome": "ようこそ"},
        }

        def mock_gettext(message):
            lang = get_language()
            return translations.get(lang, {}).get(message, message)

        with patch("django.utils.translation.gettext", side_effect=mock_gettext):
            # Test with different languages
            with translation.override("en"):
                self.assertEqual(gettext("Hello"), "Hello")

            with translation.override("ko"):
                self.assertEqual(gettext("Hello"), "안녕하세요")

            with translation.override("ja"):
                self.assertEqual(gettext("Hello"), "こんにちは")

    def test_template_trans_tag_integration(self):
        """Test Django's {% trans %} tag works with our middleware."""
        template = Template(
            """
            {% load i18n %}
            {% trans "Hello" %}
        """
        )

        # Mock translation
        def mock_gettext(message):
            if get_language() == "ko" and message == "Hello":
                return "안녕하세요"
            return message

        with patch("django.utils.translation.gettext", side_effect=mock_gettext):
            # Test with Korean
            with translation.override("ko"):
                context = Context()
                rendered = template.render(context).strip()
                self.assertEqual(rendered, "안녕하세요")

            # Test with English
            with translation.override("en"):
                context = Context()
                rendered = template.render(context).strip()
                self.assertEqual(rendered, "Hello")

    def test_lazy_translation_evaluation(self):
        """Test lazy translations are evaluated correctly."""
        # Create lazy translation
        lazy_text = gettext_lazy("Welcome")

        # Mock translations
        def mock_gettext(message):
            lang = get_language()
            if lang == "ko" and str(message) == "Welcome":
                return "환영합니다"
            elif lang == "ja" and str(message) == "Welcome":
                return "ようこそ"
            return str(message)

        with patch("django.utils.translation.gettext", side_effect=mock_gettext):
            # Lazy text should evaluate based on current language
            with translation.override("ko"):
                self.assertEqual(str(lazy_text), "환영합니다")

            with translation.override("ja"):
                self.assertEqual(str(lazy_text), "ようこそ")

            with translation.override("en"):
                self.assertEqual(str(lazy_text), "Welcome")

    def test_plural_translations(self):
        """Test plural form translations work correctly."""

        def mock_ngettext(singular, plural, count):
            if get_language() == "ko":
                # Korean doesn't have plural forms like English
                return f"{count}개 항목"
            return singular if count == 1 else plural

        with patch("django.utils.translation.ngettext", side_effect=mock_ngettext):
            with translation.override("en"):
                self.assertEqual(ngettext("item", "items", 1), "item")
                self.assertEqual(ngettext("item", "items", 5), "items")

            with translation.override("ko"):
                self.assertEqual(ngettext("item", "items", 1), "1개 항목")
                self.assertEqual(ngettext("item", "items", 5), "5개 항목")

    def test_context_translation(self):
        """Test contextual translations with pgettext."""

        def mock_pgettext(context, message):
            if get_language() == "ko":
                if context == "month" and message == "May":
                    return "5월"
                elif context == "verb" and message == "May":
                    return "~할 수 있다"
            return message

        with patch("django.utils.translation.pgettext", side_effect=mock_pgettext):
            with translation.override("ko"):
                # Different translations based on context
                self.assertEqual(pgettext("month", "May"), "5월")
                self.assertEqual(pgettext("verb", "May"), "~할 수 있다")

            with translation.override("en"):
                self.assertEqual(pgettext("month", "May"), "May")
                self.assertEqual(pgettext("verb", "May"), "May")

    def test_language_info_functions(self):
        """Test language info functions work correctly."""
        # Test get_language_info
        for lang_code in ["en", "ko", "ja"]:
            info = get_language_info(lang_code)
            self.assertIn("name", info)
            self.assertIn("name_local", info)
            self.assertIn("code", info)
            self.assertEqual(info["code"], lang_code)

    def test_get_language_from_request_integration(self):
        """Test get_language_from_request with our middleware."""
        factory = Client()

        # Create request with session
        request = factory.get("/").wsgi_request
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session["django_language"] = "ja"
        request.session.save()

        # Process through our middleware
        def get_response(req):
            return None

        our_middleware = NoPrefixLocaleMiddleware(get_response)
        our_middleware.process_request(request)

        # Should detect Japanese from session
        detected_lang = get_language_from_request(request)
        self.assertEqual(detected_lang, "ja")

    def test_translation_fallback(self):
        """Test translation fallback when translation is missing."""

        # When translation is missing, should fallback to original
        def mock_gettext(message):
            # Only translate specific messages
            if get_language() == "ko" and message == "Translated":
                return "번역됨"
            # Everything else falls back to original
            return message

        with patch("django.utils.translation.gettext", side_effect=mock_gettext):
            with translation.override("ko"):
                # Translated message
                self.assertEqual(gettext("Translated"), "번역됨")
                # Untranslated message (fallback)
                self.assertEqual(gettext("Untranslated"), "Untranslated")

    def test_date_time_formatting(self):
        """Test date/time formatting respects language settings."""
        from datetime import date

        from django.utils import formats

        test_date = date(2024, 3, 15)

        # Different languages might format dates differently
        with translation.override("en"):
            # English format (this is a simplified test)
            formatted = formats.date_format(test_date, "SHORT_DATE_FORMAT")
            self.assertIsNotNone(formatted)

        with translation.override("ko"):
            # Korean format (would be different in real locale)
            formatted = formats.date_format(test_date, "SHORT_DATE_FORMAT")
            self.assertIsNotNone(formatted)

    def test_translation_in_view_context(self):
        """Test translations work correctly within view context."""
        # Make request with Korean language
        self.client.session["django_language"] = "ko"
        self.client.session.save()

        # Mock translation for the view
        def mock_gettext(message):
            if message == "Test Message":
                return "테스트 메시지" if get_language() == "ko" else message
            return message

        with patch("django.utils.translation.gettext", side_effect=mock_gettext):
            response = self.client.get("/")

            # In the view context, translations should use Korean
            with translation.override(response.wsgi_request.LANGUAGE_CODE):
                translated = gettext("Test Message")
                self.assertEqual(translated, "테스트 메시지")

    def test_javascript_catalog_url(self):
        """Test JavaScript catalog URL works without prefix."""
        # If using Django's JavaScriptCatalog view
        from django.urls import reverse

        # The JavaScript catalog URL should not have language prefix
        url = reverse("home")  # Using a simple URL as example
        self.assertNotIn("/en/", url)
        self.assertNotIn("/ko/", url)

    def test_translation_caching(self):
        """Test that translation caching works correctly."""
        # Translations should be cached per language
        cache_hits = []

        def mock_gettext(message):
            cache_hits.append((get_language(), message))
            return f"translated_{message}"

        with patch("django.utils.translation.gettext", side_effect=mock_gettext):
            # Multiple calls with same language
            with translation.override("ko"):
                gettext("Hello")
                gettext("Hello")  # Should potentially use cache

            # Language change should not use wrong cache
            with translation.override("ja"):
                result = gettext("Hello")
                self.assertEqual(result, "translated_Hello")

    def test_middleware_translation_preservation(self):
        """Test middleware preserves translation state correctly."""
        # Initial language
        with translation.override("en"):
            initial_lang = get_language()
            self.assertEqual(initial_lang, "en")

            # Make request with different language
            self.client.session["django_language"] = "ko"
            self.client.session.save()
            response = self.client.get("/")

            # After request, check language was activated
            self.assertEqual(response.wsgi_request.LANGUAGE_CODE, "ko")

        # After request completes, language should be deactivated properly
        # (Django's cleanup should handle this)
