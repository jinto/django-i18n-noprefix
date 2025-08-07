"""
Demo views for django-i18n-noprefix example project.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.translation import gettext as _


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Welcome')
        context['welcome_message'] = _('Welcome to Django i18n No-Prefix Demo')
        context['description'] = _('This demo shows how to use Django internationalization without URL prefixes.')
        return context


class AboutView(TemplateView):
    """About page view."""
    template_name = 'about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('About')
        context['features'] = [
            {
                'title': _('No URL Prefixes'),
                'description': _('Clean URLs without language codes like /en/ or /ko/')
            },
            {
                'title': _('Session & Cookie Support'),
                'description': _('Language preference is saved and remembered')
            },
            {
                'title': _('Multiple Styles'),
                'description': _('Dropdown, list, and inline language selectors')
            },
            {
                'title': _('Framework Support'),
                'description': _('Works with Bootstrap, Tailwind, or vanilla CSS')
            },
        ]
        return context


class FeaturesView(TemplateView):
    """Features demo page."""
    template_name = 'features.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Features')
        context['demo_text'] = {
            'short': _('Hello World'),
            'medium': _('This is a medium length text to demonstrate translation.'),
            'long': _('This is a longer text that shows how the translation system handles '
                     'more complex content. It can include multiple sentences and paragraphs '
                     'to give you a better idea of how your multilingual content will look.'),
        }
        context['demo_items'] = [
            _('First item'),
            _('Second item'),
            _('Third item'),
            _('Fourth item'),
            _('Fifth item'),
        ]
        return context


class StyleBootstrapView(TemplateView):
    """Bootstrap style demo."""
    template_name = 'styles/bootstrap.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Bootstrap Style')
        context['style_name'] = 'Bootstrap 5'
        return context


class StyleTailwindView(TemplateView):
    """Tailwind style demo."""
    template_name = 'styles/tailwind.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Tailwind Style')
        context['style_name'] = 'Tailwind CSS'
        return context


class StyleVanillaView(TemplateView):
    """Vanilla CSS style demo."""
    template_name = 'styles/vanilla.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Vanilla CSS Style')
        context['style_name'] = 'Vanilla CSS'
        return context


class SettingsView(TemplateView):
    """Settings page with language preferences."""
    template_name = 'settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Settings')
        context['language_section'] = {
            'title': _('Language Preferences'),
            'description': _('Choose your preferred language for the interface'),
            'current_language': _('Current Language'),
            'change_language': _('Change Language'),
        }
        return context
