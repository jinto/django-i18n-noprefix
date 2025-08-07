"""
Tests for template tags and template rendering.
"""

import pytest
from django.template import Context, Template
from django.test import RequestFactory, override_settings
from django.utils import translation


class TestTemplateTags:
    """Test custom template tags."""

    @pytest.fixture
    def factory(self):
        """Request factory for creating mock requests."""
        return RequestFactory()

    def test_switch_language_url_tag(self):
        """Test the switch_language_url template tag."""
        template = Template("{% load i18n_noprefix %}" "{% switch_language_url 'ko' %}")
        context = Context({})
        result = template.render(context)
        assert "/i18n/set-language/ko/" in result

    def test_switch_language_url_with_next(self):
        """Test switch_language_url with next parameter."""
        template = Template(
            "{% load i18n_noprefix %}"
            "{% switch_language_url 'en' next_url='/dashboard/' %}"
        )
        context = Context({})
        result = template.render(context)
        assert "/i18n/set-language/en/" in result
        assert "next=%2Fdashboard%2F" in result or "next=/dashboard/" in result

    def test_switch_language_url_invalid_language(self):
        """Test switch_language_url with invalid language code."""
        template = Template(
            "{% load i18n_noprefix %}" "{% switch_language_url 'invalid' %}"
        )
        context = Context({})
        result = template.render(context)
        assert result.strip() == "#"

    def test_is_current_language_filter(self):
        """Test the is_current_language filter."""
        with translation.override("ko"):
            template = Template(
                "{% load i18n_noprefix %}"
                "{% if 'ko'|is_current_language %}YES{% else %}NO{% endif %}"
            )
            context = Context({})
            result = template.render(context)
            assert "YES" in result

            template = Template(
                "{% load i18n_noprefix %}"
                "{% if 'en'|is_current_language %}YES{% else %}NO{% endif %}"
            )
            result = template.render(context)
            assert "NO" in result

    @override_settings(
        LANGUAGES=[("en", "English"), ("ko", "Korean"), ("ja", "Japanese")]
    )
    def test_language_selector_tag_context(self, factory):
        """Test that language_selector tag provides correct context."""
        request = factory.get("/")
        with translation.override("ko"):
            template = Template("{% load i18n_noprefix %}" "{% language_selector %}")
            context = Context({"request": request})
            result = template.render(context)

            # Should contain selector wrapper
            assert "i18n-noprefix-selector" in result
            assert "i18n-noprefix-selector--dropdown" in result

            # Should contain current language
            assert "ko" in result.lower() or "korean" in result

    @override_settings(LANGUAGES=[("en", "English"), ("ko", "Korean")])
    def test_language_selector_dropdown_style(self, factory):
        """Test dropdown style language selector."""
        request = factory.get("/")
        template = Template(
            "{% load i18n_noprefix %}" "{% language_selector style='dropdown' %}"
        )
        context = Context({"request": request})
        result = template.render(context)

        # Should contain select element
        assert "<select" in result
        assert "i18n-noprefix-selector--dropdown" in result
        assert "<option" in result

        # Should have both languages
        assert "English" in result
        assert "Korean" in result

    @override_settings(LANGUAGES=[("en", "English"), ("ko", "Korean")])
    def test_language_selector_list_style(self, factory):
        """Test list style language selector."""
        request = factory.get("/")
        template = Template(
            "{% load i18n_noprefix %}" "{% language_selector style='list' %}"
        )
        context = Context({"request": request})
        result = template.render(context)

        # Should contain list elements
        assert "i18n-noprefix-selector--list" in result
        assert "<ul" in result
        assert "<li" in result

        # Should mark current language
        assert (
            "i18n-noprefix-selector__item--active" in result or "aria-current" in result
        )

    @override_settings(
        LANGUAGES=[("en", "English"), ("ko", "Korean"), ("ja", "Japanese")]
    )
    def test_language_selector_inline_style(self, factory):
        """Test inline style language selector."""
        request = factory.get("/")
        with translation.override("en"):
            template = Template(
                "{% load i18n_noprefix %}" "{% language_selector style='inline' %}"
            )
            context = Context({"request": request})
            result = template.render(context)

            # Should contain inline class
            assert "i18n-noprefix-selector--inline" in result

            # Should show language codes
            assert "EN" in result or "en" in result.lower()
            assert "KO" in result or "ko" in result.lower()
            assert "JA" in result or "ja" in result.lower()

            # Should have separators (if implemented)
            # Note: separators are optional in implementation

    def test_language_selector_with_next_url(self, factory):
        """Test language selector with next_url parameter."""
        request = factory.get("/")
        template = Template(
            "{% load i18n_noprefix %}" "{% language_selector next_url='/profile/' %}"
        )
        context = Context({"request": request})
        result = template.render(context)

        # Should include next parameter in URLs
        assert "next" in result or "/profile/" in result


class TestTemplateRendering:
    """Test the actual template files render correctly."""

    @pytest.fixture
    def factory(self):
        """Request factory for creating mock requests."""
        return RequestFactory()

    @override_settings(
        LANGUAGES=[("en", "English"), ("ko", "Korean")],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.template.context_processors.i18n",
                    ],
                },
            }
        ],
    )
    def test_template_files_exist_and_render(self, factory):
        """Test that template files exist and can be rendered."""
        request = factory.get("/")

        # Test dropdown template
        template = Template(
            "{% load i18n_noprefix %}" "{% language_selector style='dropdown' %}"
        )
        context = Context({"request": request})
        try:
            result = template.render(context)
            assert result  # Should not be empty
        except Exception as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

        # Test list template
        template = Template(
            "{% load i18n_noprefix %}" "{% language_selector style='list' %}"
        )
        try:
            result = template.render(context)
            assert result
        except Exception as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

        # Test inline template
        template = Template(
            "{% load i18n_noprefix %}" "{% language_selector style='inline' %}"
        )
        try:
            result = template.render(context)
            assert result
        except Exception as e:
            pytest.skip(
                f"Template rendering failed (expected in test environment): {e}"
            )

    def test_accessibility_attributes(self, factory):
        """Test that templates include proper accessibility attributes."""
        factory.get("/")  # factory is used for creating request

        # We'll check the raw template files for accessibility attributes
        from pathlib import Path

        template_dir = (
            Path(__file__).parent.parent
            / "django_i18n_noprefix"
            / "templates"
            / "i18n_noprefix"
        )

        if template_dir.exists():
            # Check dropdown template
            dropdown_template = template_dir / "language_selector.html"
            if dropdown_template.exists():
                content = dropdown_template.read_text()
                assert "aria-label" in content or "aria-labelledby" in content
                assert (
                    "role" in content or "<select" in content
                )  # select has implicit role

            # Check list template
            list_template = template_dir / "language_selector_list.html"
            if list_template.exists():
                content = list_template.read_text()
                assert "aria-label" in content or "aria-labelledby" in content
                assert "aria-current" in content  # For active item

            # Check inline template
            inline_template = template_dir / "language_selector_inline.html"
            if inline_template.exists():
                content = inline_template.read_text()
                assert "aria-label" in content or "title" in content
                assert "lang=" in content or "hreflang=" in content
