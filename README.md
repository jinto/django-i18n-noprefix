# Django i18n No-Prefix

Django의 i18n(국제화) 기능을 URL prefix 없이 사용할 수 있게 해주는 패키지입니다.

**중요**: 이 패키지는 Django의 기본 i18n 기능을 대체하는 것이 아니라 **보완**합니다. Django의 i18n 기능과 함께 사용하도록 설계되었습니다.

## 🎯 목적

Django의 기본 i18n 설정은 URL에 언어 코드 prefix(`/ko/`, `/en/` 등)를 자동으로 추가합니다. 이 패키지는 URL prefix 없이도 다국어를 지원할 수 있게 해줍니다.

## 📚 문서

- [PRD.md](PRD.md) - 제품 요구사항 문서
- [PLAN.md](PLAN.md) - 개발 계획서
- [TASKS.md](TASKS.md) - 상세 작업 목록

## 📦 설치 (예정)

```bash
pip install django-i18n-noprefix
```

## 🚀 빠른 시작

### 1. 설정

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_i18n_noprefix',
]

MIDDLEWARE = [
    # ...
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',  # 제거!
    'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',  # 추가
    # ...
]

# i18n 설정
USE_I18N = True
LANGUAGES = [
    ('ko', 'Korean'),
    ('en', 'English'),
    ('ja', 'Japanese'),
]
LANGUAGE_CODE = 'en'
```

### 2. URL 설정

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path('i18n/', include('django_i18n_noprefix.urls')),
]
```

### 3. 템플릿에서 사용

```django
{% load i18n %}  {# Django 기본 i18n #}
{% load i18n_noprefix %}  {# 우리 패키지 #}

{# Django 기본 태그 사용 #}
{% get_current_language as LANGUAGE_CODE %}
{% get_available_languages as LANGUAGES %}

{# 언어 선택기 렌더링 #}
{% language_selector %}

{# 커스텀 언어 스위처 #}
<ul>
{% for lang_code, lang_name in LANGUAGES %}
    <li class="{% if lang_code|is_current_language %}active{% endif %}">
        <a href="{% switch_language_url lang_code %}">{{ lang_name }}</a>
    </li>
{% endfor %}
</ul>
```

## 🔧 Django i18n과의 협력

이 패키지는 Django의 기본 i18n 기능과 함께 동작합니다:

- **Django i18n 사용**: 
  - `{% get_current_language %}` - 현재 언어
  - `{% get_available_languages %}` - 사용 가능한 언어
  - `{% trans %}`, `{% blocktrans %}` - 번역
  - `translation.get_language()` - Python에서 현재 언어

- **우리 패키지 제공**:
  - URL prefix 제거
  - 언어 전환 뷰
  - 언어 선택기 UI 컴포넌트

## 🚧 개발 상태

현재 핵심 기능 구현 단계입니다. (16/49 작업 완료)

### 개발 일정
- Phase 0: 프로젝트 초기 설정 (67% 진행중)
- Phase 1: 핵심 기능 구현 (67% 진행중)
- Phase 2: 테스트 구현 (40% 진행중)
- Phase 3: 문서화
- Phase 4: CI/CD 구축
- Phase 5: 배포 준비

## 📄 라이선스

MIT License

## 🤝 기여

기여를 환영합니다! 자세한 내용은 CONTRIBUTING.md에서 확인하실 수 있습니다.