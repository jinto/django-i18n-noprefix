"""
Integration tests for template rendering with django-i18n-noprefix.

Tests that template tags work correctly in real template rendering scenarios.
"""

from django.contrib.sessions.middleware import SessionMiddleware
from django.template import Context, Template
from django.test import Client, RequestFactory, TestCase, override_settings
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
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
)
class TemplateIntegrationTest(TestCase):
    """Test template tag rendering in real scenarios."""

    def setUp(self):
        """Set up test environment."""
        self.client = Client()
        self.factory = RequestFactory()
        translation.activate("en")

    def tearDown(self):
        """Clean up."""
        translation.deactivate()

    def create_request_with_session(self, path="/", language=None):
        """Create a request with session support."""
        request = self.factory.get(path)

        # Add session
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()

        # Add language
        if language:
            request.session["django_language"] = language
            request.LANGUAGE_CODE = language
            translation.activate(language)  # Activate the language
        else:
            request.LANGUAGE_CODE = "en"
            translation.activate("en")

        return request

    def test_language_selector_rendering(self):
        """Test language_selector template tag renders correctly."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector %}
        """
        )

        request = self.create_request_with_session(language="en")
        context = Context({"request": request})

        rendered = template.render(context)

        # Check that selector contains all languages
        self.assertIn("English", rendered)
        self.assertIn("Korean", rendered)
        self.assertIn("Japanese", rendered)

        # Check that current language is marked
        self.assertIn("selected", rendered)
        self.assertIn('data-current-language="en"', rendered)

        # Check no language prefixes in URLs
        self.assertNotIn("/en/", rendered)
        self.assertNotIn("/ko/", rendered)
        self.assertNotIn("/ja/", rendered)

    def test_language_selector_styles(self):
        """Test different language selector styles."""
        styles = ["dropdown", "list", "inline"]

        for style in styles:
            template = Template(
                f"""
                {{% load i18n_noprefix %}}
                {{% language_selector style="{style}" %}}
            """
            )

            request = self.create_request_with_session()
            context = Context({"request": request})

            rendered = template.render(context)

            # Each style should have its specific class
            if style == "dropdown":
                self.assertIn("i18n-noprefix-selector--dropdown", rendered)
            elif style == "list":
                self.assertIn("i18n-noprefix-selector--list", rendered)
            elif style == "inline":
                self.assertIn("i18n-noprefix-selector--inline", rendered)

    def test_switch_language_url_tag(self):
        """Test switch_language_url generates correct URLs."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% switch_language_url 'ko' %}
        """
        )

        request = self.create_request_with_session(path="/about/")
        context = Context({"request": request})

        rendered = template.render(context).strip()

        # Should generate URL to switch language (URL encoded)
        self.assertEqual(rendered, "/i18n/set-language/ko/?next=%2Fabout%2F")

        # No language prefix at the beginning of URL
        self.assertFalse(rendered.startswith("/en/"))
        self.assertFalse(rendered.startswith("/ko/"))

    def test_switch_language_url_with_custom_next(self):
        """Test switch_language_url with custom next URL."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% switch_language_url 'ja' next_url='/custom/' %}
        """
        )

        request = self.create_request_with_session()
        context = Context({"request": request})

        rendered = template.render(context).strip()

        # Should use custom next URL
        self.assertEqual(rendered, "/i18n/set-language/ja/?next=%2Fcustom%2F")

    def test_is_current_language_filter(self):
        """Test is_current_language filter."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% if 'ko'|is_current_language %}current{% else %}not current{% endif %}
        """
        )

        # Test with Korean as current
        request = self.create_request_with_session(language="ko")
        context = Context({"request": request})
        rendered = template.render(context).strip()
        self.assertEqual(rendered, "current")

        # Test with English as current
        request = self.create_request_with_session(language="en")
        context = Context({"request": request})
        rendered = template.render(context).strip()
        self.assertEqual(rendered, "not current")

    def test_template_tag_with_middleware_integration(self):
        """Test template tags work with middleware-set language."""
        # Set language through the proper set_language view
        response = self.client.get("/i18n/set-language/ja/", follow=True)

        # Verify language was set
        self.assertEqual(self.client.session.get("django_language"), "ja")

        # Create template that uses our tags
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector %}
        """
        )

        # Get request from client
        response = self.client.get("/")
        request = response.wsgi_request

        context = Context({"request": request})
        rendered = template.render(context)

        # Japanese should be marked as current in dropdown
        self.assertIn('value="ja"', rendered)
        # Check that ja is the selected option
        self.assertIn('<option \n          value="ja"', rendered)
        # Look for selected attribute near ja option
        import re

        # Check that the ja option has selected attribute
        self.assertTrue(
            re.search(r'value="ja"[^>]*selected', rendered)
            or re.search(r'selected[^>]*value="ja"', rendered)
        )

    def test_template_rendering_with_context_processors(self):
        """Test template rendering with Django context processors."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector %}
            Current: {{ request.LANGUAGE_CODE }}
        """
        )

        request = self.create_request_with_session(language="ko")
        context = Context({"request": request})

        rendered = template.render(context)

        # Check language code is available
        self.assertIn("Current: ko", rendered)

        # Korean should be marked as current in selector (dropdown uses selected attribute)
        self.assertIn("selected", rendered)
        self.assertIn('value="ko"', rendered)

    def test_template_tag_escaping(self):
        """Test that template tags properly escape content."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% switch_language_url 'en' next_url='/path/?q=<script>alert(1)</script>' %}
        """
        )

        request = self.create_request_with_session()
        context = Context({"request": request})

        rendered = template.render(context)

        # Should URL encode dangerous characters
        self.assertNotIn("<script>", rendered)
        # URL encoding uses %3C for < and %3E for >
        self.assertIn("%3Cscript%3E", rendered)

    def test_language_selector_accessibility(self):
        """Test language selector includes accessibility attributes."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector %}
        """
        )

        request = self.create_request_with_session()
        context = Context({"request": request})

        rendered = template.render(context)

        # Check accessibility attributes for dropdown style
        self.assertIn('aria-label="Language selection"', rendered)
        # Note: dropdown style doesn't have role="navigation" or hreflang
        # Those are for list/inline styles

    def test_template_inheritance_compatibility(self):
        """Test that our tags work with template inheritance."""
        # Base template
        base_template = Template(
            """
            {% load i18n_noprefix %}
            <html>
            <body>
                {% block language_selector %}
                    {% language_selector %}
                {% endblock %}
            </body>
            </html>
        """
        )

        request = self.create_request_with_session()
        context = Context({"request": request})

        rendered = base_template.render(context)

        # Should render within HTML structure
        self.assertIn("<html>", rendered)
        self.assertIn("i18n-noprefix-selector", rendered)

    def test_multiple_template_tags_in_same_template(self):
        """Test multiple template tags work together."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector style="dropdown" %}
            <hr>
            {% language_selector style="inline" %}
            <hr>
            Current: {% if 'en'|is_current_language %}English{% endif %}
            Switch: {% switch_language_url 'ko' %}
        """
        )

        request = self.create_request_with_session(language="en")
        context = Context({"request": request})

        rendered = template.render(context)

        # All components should be present
        self.assertIn("i18n-noprefix-selector--dropdown", rendered)
        self.assertIn("i18n-noprefix-selector--inline", rendered)
        self.assertIn("Current: English", rendered)
        self.assertIn("/i18n/set-language/ko/", rendered)

    def test_template_tag_with_ajax_attribute(self):
        """Test template tags with AJAX functionality."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector style="dropdown" %}
        """
        )

        request = self.create_request_with_session()
        context = Context({"request": request})

        rendered = template.render(context)

        # Dropdown should include onchange for AJAX-like behavior
        self.assertIn("onchange", rendered)
        self.assertIn("data-url", rendered)
