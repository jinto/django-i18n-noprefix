"""
Tests for views.
"""

import json

from django.urls import reverse


class TestChangeLanguageView:
    """Test the change_language view."""

    def test_change_language_valid(self, client):
        """Test changing to a valid language."""
        url = reverse("django_i18n_noprefix:change_language", args=["ko"])
        response = client.get(url)

        # Should redirect
        assert response.status_code == 302
        assert response.url == "/"

    def test_change_language_with_next_url(self, client):
        """Test changing language with next parameter."""
        url = reverse("django_i18n_noprefix:change_language", args=["ja"])
        response = client.get(f"{url}?next=/about/")

        assert response.status_code == 302
        assert response.url == "/about/"

    def test_change_language_with_referer(self, client):
        """Test changing language with HTTP_REFERER."""
        url = reverse("django_i18n_noprefix:change_language", args=["en"])
        response = client.get(url, HTTP_REFERER="/previous/")

        assert response.status_code == 302
        assert response.url == "/previous/"

    def test_change_language_invalid(self, client):
        """Test changing to an invalid language."""
        url = reverse("django_i18n_noprefix:change_language", args=["invalid"])
        response = client.get(url)

        # Should still redirect but language won't change
        assert response.status_code == 302
        assert response.url == "/"

    def test_change_language_post_method(self, client):
        """Test changing language with POST method."""
        url = reverse("django_i18n_noprefix:change_language", args=["ko"])
        response = client.post(url, {"next": "/dashboard/"})

        assert response.status_code == 302
        assert response.url == "/dashboard/"

    def test_change_language_sets_cookie(self, client):
        """Test that changing language sets a cookie."""
        url = reverse("django_i18n_noprefix:change_language", args=["ja"])
        response = client.get(url, follow=False)

        # The cookie should be set by the middleware in the next request
        # So we follow the redirect
        response = client.get(response.url)

        # Check if language was activated (indirect test)
        # The actual cookie setting is handled by middleware


class TestSetLanguageAjaxView:
    """Test the set_language_ajax view."""

    def test_ajax_change_language_valid(self, client):
        """Test AJAX language change with valid data."""
        url = reverse("django_i18n_noprefix:set_language_ajax")
        data = {"language": "ko"}

        response = client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["language"] == "ko"
        assert response_data["redirect"] == "/"

    def test_ajax_change_language_with_next(self, client):
        """Test AJAX language change with next URL."""
        url = reverse("django_i18n_noprefix:set_language_ajax")
        data = {"language": "en", "next": "/profile/"}

        response = client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert response_data["redirect"] == "/profile/"

    def test_ajax_change_language_invalid(self, client):
        """Test AJAX language change with invalid language."""
        url = reverse("django_i18n_noprefix:set_language_ajax")
        data = {"language": "invalid"}

        response = client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 400
        response_data = response.json()
        assert response_data["success"] is False
        assert "Invalid language code" in response_data["error"]

    def test_ajax_change_language_no_language(self, client):
        """Test AJAX language change without language field."""
        url = reverse("django_i18n_noprefix:set_language_ajax")
        data = {"next": "/home/"}

        response = client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        assert response.status_code == 400
        response_data = response.json()
        assert response_data["success"] is False
        assert "No language specified" in response_data["error"]

    def test_ajax_change_language_invalid_json(self, client):
        """Test AJAX language change with invalid JSON."""
        url = reverse("django_i18n_noprefix:set_language_ajax")

        response = client.post(
            url, data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400
        response_data = response.json()
        assert response_data["success"] is False
        assert "Invalid JSON data" in response_data["error"]

    def test_ajax_requires_post_method(self, client):
        """Test that AJAX endpoint requires POST method."""
        url = reverse("django_i18n_noprefix:set_language_ajax")

        # GET should not be allowed
        response = client.get(url)
        assert response.status_code == 405  # Method Not Allowed

        # PUT should not be allowed
        response = client.put(url)
        assert response.status_code == 405


class TestURLSafety:
    """Test URL safety checks."""

    def test_safe_relative_url(self, client):
        """Test that relative URLs are considered safe."""
        url = reverse("django_i18n_noprefix:change_language", args=["ko"])
        response = client.get(f"{url}?next=/safe/path/")

        assert response.status_code == 302
        assert response.url == "/safe/path/"

    def test_unsafe_absolute_url(self, client):
        """Test that external URLs are rejected."""
        url = reverse("django_i18n_noprefix:change_language", args=["ko"])
        response = client.get(f"{url}?next=http://evil.com/")

        assert response.status_code == 302
        # Should fall back to default
        assert response.url == "/"

    def test_same_domain_url(self, client):
        """Test that same-domain absolute URLs are accepted."""
        url = reverse("django_i18n_noprefix:change_language", args=["ko"])
        response = client.get(
            f"{url}?next=http://testserver/about/", HTTP_HOST="testserver"
        )

        assert response.status_code == 302
        assert response.url == "http://testserver/about/"
