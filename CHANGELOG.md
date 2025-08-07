# Changelog

All notable changes to django-i18n-noprefix will be documented in this file.

## [Unreleased]

### Added
- Initial implementation of NoPrefixLocaleMiddleware
- Language detection from session, cookie, and Accept-Language header
- Template tags for language switching (switch_language_url, is_current_language, language_selector)
- Three language selector styles (dropdown, list, inline)
- CSS framework support (Bootstrap 5, Tailwind CSS, Vanilla CSS)
- Complete example Django project with translations
- Comprehensive test suite with 93% code coverage
- System checks for configuration validation
- Django 4.2 LTS and 5.0+ support

### Fixed
- Session key attribute check for compatibility with mock sessions in tests

### Documentation
- Complete README with installation and usage instructions
- Example project with Korean and Japanese translations
- Task tracking document (TASKS.md) for development roadmap