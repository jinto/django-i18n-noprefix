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
        else:
            request.LANGUAGE_CODE = "en"

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
        self.assertIn('data-current="true"', rendered)

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
                self.assertIn("language-selector-dropdown", rendered)
            elif style == "list":
                self.assertIn("language-selector-list", rendered)
            elif style == "inline":
                self.assertIn("language-selector-inline", rendered)

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

        # Should generate URL to switch language
        self.assertEqual(rendered, "/i18n/set-language/ko/?next=/about/")

        # No language prefix
        self.assertNotIn("/en/", rendered)
        self.assertNotIn("/ko/", rendered)

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
        self.assertEqual(rendered, "/i18n/set-language/ja/?next=/custom/")

    def test_is_current_language_filter(self):
        """Test is_current_language filter."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% if 'ko'|is_current_language:request %}current{% else %}not current{% endif %}
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
        # Make actual request through client
        self.client.session["django_language"] = "ja"
        self.client.session.save()

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

        # Japanese should be marked as current
        self.assertIn('hreflang="ja"', rendered)
        self.assertIn('data-current="true"', rendered)

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

        # Korean should be marked as current in selector
        self.assertIn('hreflang="ko"', rendered)

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

        # Should escape dangerous characters
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

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

        # Check accessibility attributes
        self.assertIn('role="navigation"', rendered)
        self.assertIn("aria-label=", rendered)
        self.assertIn("hreflang=", rendered)

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
        self.assertIn("language-selector", rendered)

    def test_multiple_template_tags_in_same_template(self):
        """Test multiple template tags work together."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector style="dropdown" %}
            <hr>
            {% language_selector style="inline" %}
            <hr>
            Current: {% if 'en'|is_current_language:request %}English{% endif %}
            Switch: {% switch_language_url 'ko' %}
        """
        )

        request = self.create_request_with_session(language="en")
        context = Context({"request": request})

        rendered = template.render(context)

        # All components should be present
        self.assertIn("language-selector-dropdown", rendered)
        self.assertIn("language-selector-inline", rendered)
        self.assertIn("Current: English", rendered)
        self.assertIn("/i18n/set-language/ko/", rendered)

    def test_template_tag_with_ajax_attribute(self):
        """Test template tags with AJAX functionality."""
        template = Template(
            """
            {% load i18n_noprefix %}
            {% language_selector style="dropdown" ajax=True %}
        """
        )

        request = self.create_request_with_session()
        context = Context({"request": request})

        rendered = template.render(context)

        # Should include AJAX data attributes
        self.assertIn('data-ajax="true"', rendered)
        self.assertIn("/i18n/set-language-ajax/", rendered)
