# Django i18n No-Prefix 패키지 개발 계획

## 📋 개요
Django의 i18n 기능을 URL prefix 없이 사용할 수 있게 해주는 패키지 개발 전체 계획서.

### 핵심 목표
- URL에서 언어 코드 prefix (`/ko/`, `/en/`) 완전 제거
- Django 표준 i18n 기능과 100% 호환
- 간단한 설정으로 기존 프로젝트에 즉시 적용 가능

### 지원 버전
- Django: 4.2 LTS, 5.0+
- Python: 3.8+

---

## 🏗️ Part 1: 구현 계획

### 1.1 패키지 구조
```
django-i18n-noprefix/
├── django_i18n_noprefix/
│   ├── __init__.py
│   ├── middleware.py      # 핵심 미들웨어
│   ├── utils.py           # 유틸리티 함수
│   ├── views.py           # 언어 변경 뷰
│   ├── urls.py            # URL 패턴
│   └── templatetags/
│       └── i18n_noprefix.py  # 템플릿 태그
├── tests/                 # 테스트
│   ├── conftest.py
│   ├── test_middleware.py
│   ├── test_utils.py
│   └── test_views.py
├── example_project/       # 예제 프로젝트
├── docs/                  # 문서
├── pyproject.toml
├── README.md
├── LICENSE
└── tox.ini
```

### 1.2 핵심 컴포넌트

#### 미들웨어 (NoPrefixLocaleMiddleware)
```python
class NoPrefixLocaleMiddleware:
    """
    URL prefix 없이 다국어를 지원하는 미들웨어
    
    언어 감지 우선순위:
    1. 세션 (django_language)
    2. 쿠키 (django_language)  
    3. Accept-Language 헤더
    4. 기본 언어 (LANGUAGE_CODE)
    """
```

**주요 기능:**
- URL에 언어 prefix 추가하지 않음
- 표준 Django i18n API와 완벽 호환
- 언어 변경 시 세션/쿠키 자동 업데이트

#### 언어 변경 시스템
- **URL 방식**: `/i18n/set-language/<lang_code>/`
- **AJAX 방식**: POST로 언어 코드 전송
- **자동 리다이렉트**: 이전 페이지로 자동 이동

#### 템플릿 태그
- `{% get_current_language %}`: 현재 언어 코드
- `{% get_available_languages %}`: 사용 가능한 언어 목록
- `{% language_selector %}`: 언어 선택 드롭다운

### 1.3 설정 옵션
```python
# settings.py
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_i18n_noprefix.middleware.NoPrefixLocaleMiddleware',  # 이것만 추가
    # 'django.middleware.locale.LocaleMiddleware',  # 제거
]

# 선택적 설정
LANGUAGE_COOKIE_NAME = 'django_language'  # 기본값
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60  # 1년
```

---

## 🧪 Part 2: 테스트 계획

### 2.1 테스트 전략

#### 테스트 레벨
```
1. 설치 테스트 - 패키지 설치 및 import
2. 단위 테스트 - 개별 컴포넌트
3. 통합 테스트 - Django와의 통합
4. E2E 테스트 - 실제 사용 시나리오
5. 호환성 테스트 - 다중 버전 매트릭스
```

#### 테스트 매트릭스
```ini
# tox.ini
[tox]
envlist = 
    py{38,39,310,311}-django42-{sqlite,postgres}
    py{310,311,312}-django50-{sqlite,postgres}
    py{311,312}-django{51,52}-{sqlite,postgres}
```

### 2.2 핵심 테스트 케이스

#### 설치 테스트
```bash
# 깨끗한 환경 설치
pip install django-i18n-noprefix
python -c "import django_i18n_noprefix"

# 기존 Django 프로젝트에 통합
pip install Django==4.2
pip install django-i18n-noprefix
python manage.py check
```

#### 미들웨어 테스트
```python
class TestNoPrefixLocaleMiddleware:
    def test_no_url_prefix(self):
        """URL에 언어 prefix가 없어야 함"""
        response = self.client.get('/about/')
        assert '/en/' not in response.url
        assert '/ko/' not in response.url
    
    def test_language_detection_priority(self):
        """언어 감지 우선순위 검증"""
        # 세션 > 쿠키 > 헤더
    
    def test_language_persistence(self):
        """언어 설정이 유지되는지 확인"""
```

#### URL 처리 테스트
```python
class TestURLHandling:
    def test_reverse_without_prefix(self):
        """reverse() 함수가 prefix 없는 URL 생성"""
        url = reverse('about')
        assert url == '/about/'  # not '/en/about/'
    
    def test_url_patterns_work(self):
        """기존 URL 패턴이 정상 동작"""
```

#### 엣지 케이스
```python
class TestEdgeCases:
    def test_malformed_accept_language(self):
        """잘못된 Accept-Language 헤더 처리"""
        
    def test_concurrent_language_changes(self):
        """동시 다발적 언어 변경"""
        
    def test_invalid_language_codes(self):
        """유효하지 않은 언어 코드 처리"""
```

### 2.3 성능 테스트
```python
class TestPerformance:
    def test_middleware_overhead(self):
        """미들웨어 오버헤드 < 1ms"""
        
    def test_no_memory_leak(self):
        """메모리 누수 없음"""
        
    def test_no_extra_queries(self):
        """추가 DB 쿼리 없음"""
```

### 2.4 보안 테스트
```python
class TestSecurity:
    def test_language_injection(self):
        """언어 코드 인젝션 방어"""
        
    def test_csrf_protection(self):
        """CSRF 보호 유지"""
```

---

## 🚀 Part 3: 개발 워크플로우

### 3.1 로컬 개발
```bash
# 개발 환경 설정
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# 테스트 실행
pytest                    # 빠른 테스트
pytest --cov             # 커버리지 포함
tox                      # 전체 매트릭스

# 코드 품질
black .                  # 포맷팅
ruff check .            # 린팅
mypy .                  # 타입 체크
```

### 3.2 CI/CD Pipeline
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        python: ['3.8', '3.9', '3.10', '3.11', '3.12']
        django: ['4.2', '5.0']
        
    steps:
      - uses: actions/checkout@v3
      - name: Test
        run: |
          pip install Django~=${{ matrix.django }}
          pip install -e ".[test]"
          pytest --cov
      
      - name: Coverage
        uses: codecov/codecov-action@v3
```

### 3.3 배포 프로세스
```bash
# 1. 버전 업데이트
# pyproject.toml에서 version 수정

# 2. 빌드
python -m build

# 3. TestPyPI 테스트
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ django-i18n-noprefix

# 4. PyPI 배포
twine upload dist/*
```

---

## 📅 Part 4: 개발 일정

> 📌 **상세 작업 목록은 [TASKS.md](TASKS.md)를 참조하세요.**

### Phase 0: 프로젝트 초기 설정 (Day 1-2)
- [ ] GitHub 저장소 및 기본 구조 (TASK-001~006)
- [ ] 개발 환경 설정

### Phase 1: 핵심 기능 구현 (Week 1)
- [ ] 미들웨어 구현 (TASK-101~104)
- [ ] 유틸리티 함수 (TASK-105~106)
- [ ] 언어 변경 시스템 (TASK-107~108)
- [ ] 템플릿 태그 (TASK-109~112)

### Phase 2: 테스트 구현 (Week 2)
- [ ] 테스트 설정 (TASK-201~202)
- [ ] 단위 테스트 (TASK-203~205)
- [ ] 통합 테스트 (TASK-206~207)
- [ ] 성능/호환성 테스트 (TASK-208~210)

### Phase 3: 문서화 (Week 3)
- [ ] 사용자 문서 (TASK-301~302)
- [ ] 예제 프로젝트 (TASK-303~304)
- [ ] 개발자 문서 (TASK-305~306)

### Phase 4: CI/CD 및 배포 (Week 4)
- [ ] GitHub Actions 설정 (TASK-401~403)
- [ ] 품질 도구 연동 (TASK-404~405)
- [ ] 배포 준비 (TASK-501~506)

### Phase 5: 유지보수 체계 구축 (Week 5)
- [ ] 커뮤니티 관리 (TASK-601~604)

---

## ✅ Part 5: 체크리스트

### 개발 체크리스트
- [ ] 미들웨어 구현 완료
- [ ] 언어 변경 시스템 구현
- [ ] 템플릿 태그 구현
- [ ] Django admin 통합
- [ ] 예제 프로젝트 작성

### 테스트 체크리스트
- [ ] 단위 테스트 작성 (>95% 커버리지)
- [ ] 통합 테스트 작성
- [ ] 성능 테스트 통과
- [ ] 보안 테스트 통과
- [ ] 다중 버전 테스트 통과

### 문서 체크리스트
- [ ] README 완성
- [ ] 설치 가이드
- [ ] 설정 가이드
- [ ] API 레퍼런스
- [ ] 마이그레이션 가이드
- [ ] 예제 코드

### 배포 체크리스트
- [ ] pyproject.toml 메타데이터 완성
- [ ] LICENSE 파일
- [ ] CHANGELOG 작성
- [ ] GitHub Actions CI/CD
- [ ] TestPyPI 테스트 성공
- [ ] PyPI 배포 완료

---

## 🎯 Part 6: 성공 지표

### 기능적 성공
- ✅ URL에 언어 prefix 완전 제거
- ✅ Django 표준 i18n 기능 정상 동작
- ✅ 모든 지원 버전에서 동작
- ✅ 5분 내 설치 및 설정 가능

### 품질 지표
- 📊 테스트 커버리지 > 95%
- ⚡ 성능 오버헤드 < 1ms
- 🔒 보안 취약점 0개
- 📦 패키지 크기 < 100KB

### 사용성 지표
- 📖 완전한 문서화
- 💡 명확한 에러 메시지
- 🔧 제로 설정으로 기본 동작
- 🎨 직관적인 API

---

## 📚 Part 7: 참고 자료

### pickspage 구현 분석
- **CustomLocaleMiddleware**: URL prefix 없는 미들웨어 구현
- **언어 감지**: 세션 → 쿠키 → 헤더 우선순위
- **언어 변경**: `/lang/<code>/` URL 패턴
- **핵심 특징**: Django 표준과 완벽 호환

### 기술 문서
- [Django i18n 문서](https://docs.djangoproject.com/en/4.2/topics/i18n/)
- [Python 패키징 가이드](https://packaging.python.org/)
- [Django 패키지 개발 가이드](https://djangopackages.org/)

### 유사 프로젝트
- django-localeurl (deprecated)
- django-solid-i18n-urls
- 차별점: 최신 Django 지원, 간단한 설정, 활발한 유지보수

---

## 🔄 Part 8: 유지보수 계획

### 버전 관리
- **Major**: Django 메이저 버전 변경 시
- **Minor**: 새 기능 추가
- **Patch**: 버그 수정, 문서 개선

### 지원 정책
- Django LTS 버전 최소 2개 지원
- 새 Django 버전 출시 후 3개월 내 지원
- 보안 패치는 즉시 대응

### 커뮤니티 관리
- GitHub Issues로 버그 리포트
- Pull Request 환영
- 분기별 릴리즈 계획

---

## 💡 Part 9: 위험 요소 및 대응

### 기술적 위험
| 위험 | 영향 | 대응 |
|-----|------|------|
| Django 내부 API 변경 | 높음 | 버전별 호환성 레이어 |
| 성능 저하 | 중간 | 프로파일링 및 최적화 |
| 보안 취약점 | 높음 | 정기 보안 감사 |

### 대응 전략
1. **호환성**: Django 베타 버전 사전 테스트
2. **성능**: 벤치마크 자동화 및 모니터링
3. **보안**: OWASP 가이드라인 준수

---

## 📝 Part 10: 다음 단계

### 즉시 실행 (Day 1)
1. TASK-001: GitHub 저장소 생성
2. TASK-002: 기본 파일 생성
3. TASK-003: 패키지 구조 생성

### 첫 주 목표
1. Phase 0 완료 (프로젝트 설정)
2. Phase 1 완료 (핵심 기능 구현)
3. Phase 2 시작 (테스트 작성)

### 첫 달 목표
1. MVP 기능 완성 (Phase 1-2)
2. 문서화 완료 (Phase 3)
3. TestPyPI 배포 (Phase 4-5)

### 작업 추적
- 진행 상황: [TASKS.md](TASKS.md) 참조
- 전체 작업: 49개
- 예상 시간: 52시간

---

## 📄 관련 문서

- [PRD.md](PRD.md) - 제품 요구사항 문서
- [TASKS.md](TASKS.md) - 상세 작업 목록
- [README.md](README.md) - 프로젝트 소개

---

*이 문서는 Django i18n No-Prefix 패키지의 전체 개발 과정을 담은 통합 계획서입니다.*