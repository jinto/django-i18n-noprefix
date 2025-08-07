# Django i18n No-Prefix 패키지 작업 목록

## 📋 개요
이 문서는 django-i18n-noprefix 패키지 개발을 위한 구체적인 작업 목록입니다.
각 작업은 독립적으로 완료 가능하며, PR 단위로 관리됩니다.

### 작업 상태
- ⬜ TODO: 시작 전
- 🟨 IN PROGRESS: 진행 중
- ✅ DONE: 완료
- ❌ BLOCKED: 차단됨
- 🔄 REVIEW: 리뷰 중

---

## 🎯 Phase 0: 프로젝트 초기 설정

### 0.1 기본 구조
✅ **TASK-001**: GitHub 저장소 생성
- 저장소 이름: `django-i18n-noprefix`
- 설명: "Django i18n without URL prefixes"
- 라이선스: MIT
- .gitignore: Python 템플릿
- 완료: 2024-08-07 18:43

✅ **TASK-002**: 프로젝트 기본 파일 생성
```
- README.md (기본 템플릿) ✅
- LICENSE (MIT) ✅
- .gitignore ✅
- .editorconfig (생략)
- CONTRIBUTING.md ✅
- CODE_OF_CONDUCT.md (생략)
```
- 완료: 2025-08-07 18:50

✅ **TASK-003**: 패키지 구조 생성
```bash
mkdir -p django_i18n_noprefix/templatetags
mkdir -p tests
mkdir -p docs
mkdir -p example_project
touch django_i18n_noprefix/__init__.py
```
- 완료: 2025-08-07 19:37

### 0.2 개발 환경
✅ **TASK-004**: pyproject.toml 작성
- 참고: pickspage/pyproject.toml
- 최소 의존성: Django>=4.2
- 개발 의존성: pytest, pytest-django, black, ruff, mypy
- 빌드 시스템: hatchling
- 완료: 2025-08-07 19:45

⬜ **TASK-005**: 개발 환경 설정 스크립트
```bash
# scripts/setup-dev.sh
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

⬜ **TASK-006**: Pre-commit 설정
```yaml
# .pre-commit-config.yaml
- black (코드 포맷팅)
- ruff (린팅)
- mypy (타입 체크)
```

---

## 🔧 Phase 1: 핵심 기능 구현

### 1.1 미들웨어 구현
✅ **TASK-101**: NoPrefixLocaleMiddleware 기본 구조
- 파일: `django_i18n_noprefix/middleware.py`
- 참고: pickspage/main/middleware.py
- 클래스: `NoPrefixLocaleMiddleware`
- 메서드: `__init__`, `__call__`
- 완료: 2025-08-07 19:52

✅ **TASK-102**: 언어 감지 로직 구현
```python
def get_language(self, request):
    """
    우선순위:
    1. 세션 (django_language)
    2. 쿠키 (django_language)
    3. Accept-Language 헤더
    4. 기본 언어 (LANGUAGE_CODE)
    """
```
- 완료: 2025-08-07 19:52 (TASK-101과 함께 구현)

✅ **TASK-103**: 언어 저장 로직 구현
```python
def save_language(self, request, response, original_lang):
    """
    - 세션에 저장 (세션이 있는 경우)
    - 쿠키에 저장 (항상)
    """
```
- 완료: 2025-08-07 19:52 (TASK-101과 함께 구현)

⬜ **TASK-104**: Accept-Language 헤더 파싱 개선
- Django의 `get_language_from_request` 활용
- 복잡한 헤더 처리 (q-value 포함)
- 유효하지 않은 언어 코드 처리

### 1.2 유틸리티 함수
✅ **TASK-105**: utils.py 작성
- 참고: pickspage/main/utils.py
- `activate_language(request, lang_code)`
- `get_supported_languages()`
- `get_language_choices()`
- 완료: 2025-08-07 20:15

✅ **TASK-106**: 언어 코드 검증 함수
```python
def is_valid_language(lang_code):
    """언어 코드가 LANGUAGES 설정에 있는지 확인"""
```
- 완료: 2025-08-07 20:15 (TASK-105와 함께 구현)

### 1.3 언어 변경 시스템
✅ **TASK-107**: 언어 변경 뷰 구현
- 파일: `django_i18n_noprefix/views.py`
- `change_language(request, lang_code)` - GET/POST 지원
- `set_language_ajax(request)` - AJAX 전용
- 완료: 2025-08-07 20:18

✅ **TASK-108**: URL 패턴 정의
- 파일: `django_i18n_noprefix/urls.py`
- `/i18n/set-language/<lang_code>/`
- `/i18n/set-language-ajax/`
- 완료: 2025-08-07 20:18 (TASK-107과 함께 구현)

### 1.4 템플릿 태그
⬜ **TASK-109**: 템플릿 태그 라이브러리 생성
- 파일: `django_i18n_noprefix/templatetags/i18n_noprefix.py`
- `{% get_current_language %}`
- `{% get_available_languages %}`

⬜ **TASK-110**: 언어 선택기 템플릿 태그
```python
@register.inclusion_tag('i18n_noprefix/language_selector.html')
def language_selector():
    """언어 선택 드롭다운 생성"""
```

### 1.5 Django 앱 설정
⬜ **TASK-111**: apps.py 작성
```python
class I18nNoPrefixConfig(AppConfig):
    name = 'django_i18n_noprefix'
    verbose_name = 'Django i18n No-Prefix'
```

⬜ **TASK-112**: 기본 템플릿 제공
- `templates/i18n_noprefix/language_selector.html`
- Bootstrap/Tailwind 호환 버전

---

## 🧪 Phase 2: 테스트 구현

### 2.1 테스트 설정
✅ **TASK-201**: pytest 설정
- 파일: `tests/conftest.py`
- Django 테스트 설정
- 픽스처 정의
- 완료: 2025-08-07 19:48

⬜ **TASK-202**: 테스트용 Django 프로젝트 설정
```python
# tests/test_project/settings.py
INSTALLED_APPS = ['django_i18n_noprefix']
MIDDLEWARE = ['django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware']
```

### 2.2 단위 테스트
✅ **TASK-203**: 미들웨어 테스트
- 파일: `tests/test_middleware.py`
- URL prefix 없음 확인
- 언어 감지 우선순위
- 언어 저장 로직
- 완료: 2025-08-07 19:52 (TASK-101과 함께 작성)

✅ **TASK-204**: 유틸리티 함수 테스트
- 파일: `tests/test_utils.py`
- 언어 활성화
- 언어 검증
- 완료: 2025-08-07 20:16 (TASK-105와 함께 작성)

✅ **TASK-205**: 뷰 테스트
- 파일: `tests/test_views.py`
- 언어 변경 뷰
- AJAX 뷰
- 리다이렉션
- 완료: 2025-08-07 20:19 (TASK-107과 함께 작성)

### 2.3 통합 테스트
⬜ **TASK-206**: Django 통합 테스트
- reverse() 함수 동작
- 템플릿 태그 동작
- i18n 번역 동작

⬜ **TASK-207**: 엣지 케이스 테스트
- 잘못된 언어 코드
- 복잡한 Accept-Language 헤더
- 세션 없는 사용자

### 2.4 성능 테스트
⬜ **TASK-208**: 성능 벤치마크
- 미들웨어 오버헤드 측정
- 메모리 사용량 측정
- 대량 요청 처리

### 2.5 호환성 테스트
⬜ **TASK-209**: tox 설정
```ini
# tox.ini
envlist = 
    py{38,39,310,311}-django42
    py{310,311,312}-django50
```

⬜ **TASK-210**: Django 버전별 테스트
- Django 4.2 LTS
- Django 5.0+
- Django 5.1, 5.2 (미래 버전)

---

## 📝 Phase 3: 문서화

### 3.1 사용자 문서
⬜ **TASK-301**: README.md 작성
- 설치 방법
- 빠른 시작 가이드
- 설정 옵션
- 예제 코드

⬜ **TASK-302**: 상세 문서 작성
- `docs/installation.md`
- `docs/configuration.md`
- `docs/api-reference.md`
- `docs/migration-guide.md`

### 3.2 예제 프로젝트
⬜ **TASK-303**: 예제 Django 프로젝트 생성
- `example_project/`
- 3개 언어 지원 (en, ko, ja)
- 언어 선택기 포함

⬜ **TASK-304**: 예제 프로젝트 문서
- 실행 방법
- 테스트 시나리오
- 스크린샷

### 3.3 개발자 문서
⬜ **TASK-305**: CONTRIBUTING.md 작성
- 개발 환경 설정
- 코드 스타일
- PR 가이드라인
- 테스트 실행 방법

⬜ **TASK-306**: API 문서 자동 생성
- Sphinx 설정
- autodoc 활용
- ReadTheDocs 연동

---

## 🚀 Phase 4: CI/CD 구축

### 4.1 GitHub Actions
⬜ **TASK-401**: 테스트 워크플로우
```yaml
# .github/workflows/test.yml
- Python 3.8-3.12
- Django 4.2, 5.0+
- pytest 실행
- 커버리지 리포트
```

⬜ **TASK-402**: 코드 품질 워크플로우
```yaml
# .github/workflows/quality.yml
- black 체크
- ruff 체크
- mypy 체크
```

⬜ **TASK-403**: 릴리즈 워크플로우
```yaml
# .github/workflows/release.yml
- 태그 푸시 시 자동 빌드
- TestPyPI 업로드
- PyPI 업로드
```

### 4.2 품질 도구
⬜ **TASK-404**: Codecov 연동
- 커버리지 배지
- PR 커버리지 리포트

⬜ **TASK-405**: Dependabot 설정
- 의존성 자동 업데이트
- 보안 패치

---

## 📦 Phase 5: 배포 준비

### 5.1 패키지 메타데이터
⬜ **TASK-501**: pyproject.toml 완성
- 모든 메타데이터 확인
- 분류자(Classifiers) 추가
- 키워드 추가

⬜ **TASK-502**: CHANGELOG.md 작성
- 버전별 변경사항
- 마이그레이션 가이드

### 5.2 배포 테스트
⬜ **TASK-503**: TestPyPI 배포 테스트
```bash
python -m build
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ django-i18n-noprefix
```

⬜ **TASK-504**: 설치 테스트
- 새 가상환경에서 설치
- 기존 Django 프로젝트에 통합
- 의존성 충돌 확인

### 5.3 정식 배포
⬜ **TASK-505**: PyPI 배포
```bash
twine upload dist/*
```

⬜ **TASK-506**: 배포 후 검증
- PyPI 페이지 확인
- 설치 테스트
- 문서 링크 확인

---

## 🔄 Phase 6: 유지보수

### 6.1 피드백 대응
⬜ **TASK-601**: Issue 템플릿 생성
- 버그 리포트
- 기능 요청
- 질문

⬜ **TASK-602**: PR 템플릿 생성
- 체크리스트
- 테스트 요구사항

### 6.2 커뮤니티
⬜ **TASK-603**: 릴리즈 노트 작성
- v0.1.0 초기 릴리즈

⬜ **TASK-604**: 프로모션
- Django 포럼 공유
- Reddit r/django
- Twitter/X 발표

---

## 📊 진행 상황 대시보드

### 전체 진행률
```
Phase 0: [✅✅✅✅⬜⬜] 67% (4/6)
Phase 1: [✅✅✅✅✅✅✅⬜⬜⬜⬜⬜] 58% (7/12)
Phase 2: [✅✅✅✅⬜⬜⬜⬜⬜⬜] 40% (4/10)
Phase 3: [⬜⬜⬜⬜⬜⬜] 0% (0/6)
Phase 4: [⬜⬜⬜⬜⬜] 0% (0/5)
Phase 5: [⬜⬜⬜⬜⬜⬜] 0% (0/6)
Phase 6: [⬜⬜⬜⬜] 0% (0/4)

전체: 15/49 작업 완료 (31%)
```

### 우선순위별 분류
- 🔴 **Critical** (즉시): TASK-001~006, 101~103
- 🟡 **High** (이번 주): TASK-104~112, 201~203
- 🟢 **Medium** (이번 달): TASK-204~210, 301~306
- 🔵 **Low** (나중에): TASK-401~606

### 예상 소요 시간
| Phase | 작업 수 | 예상 시간 | 누적 시간 |
|-------|---------|-----------|-----------|
| 0 | 6 | 4h | 4h |
| 1 | 12 | 16h | 20h |
| 2 | 10 | 12h | 32h |
| 3 | 6 | 8h | 40h |
| 4 | 5 | 6h | 46h |
| 5 | 6 | 4h | 50h |
| 6 | 4 | 2h | 52h |

**총 예상 시간**: 52시간 (약 1.5주 풀타임)

---

## 🎯 다음 작업

### 즉시 시작 (Today)
1. ⬜ TASK-001: GitHub 저장소 생성
2. ⬜ TASK-002: 기본 파일 생성
3. ⬜ TASK-003: 패키지 구조 생성

### 내일 목표 (Tomorrow)
1. ⬜ TASK-004: pyproject.toml 작성
2. ⬜ TASK-101: 미들웨어 기본 구조

### 이번 주 목표 (This Week)
1. Phase 0 완료 (프로젝트 설정)
2. Phase 1의 50% 완료 (핵심 기능)

---

## 📝 참고사항

### pickspage 분석 결과
- `main/middleware.py`: CustomLocaleMiddleware 구현 참고
- `main/utils.py`: set_language 함수 참고
- `main/views.py`: change_language 뷰 참고
- `config/settings/base.py`: 미들웨어 설정 참고

### 주의사항
1. **하드코딩 제거**: pickspage는 'ko'가 기본값이지만, 패키지는 설정 가능해야 함
2. **유연성**: 언어 감지 순서를 설정으로 변경 가능하게
3. **호환성**: Django의 기존 i18n 기능과 충돌하지 않도록 주의
4. **테스트**: 각 기능마다 테스트 먼저 작성 (TDD)

### 완료 기준
- ✅ 코드 작성 완료
- ✅ 테스트 통과
- ✅ 문서 작성
- ✅ PR 머지

---

*이 문서는 작업 진행에 따라 지속적으로 업데이트됩니다.*
*최종 수정: 2024-12-XX*