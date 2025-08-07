# TASK-006: Pre-commit 설정 - 작업 계획

## 👥 전문가 팀 구성
1. **DevOps 엔지니어** (13년 경력) - CI/CD 파이프라인 및 자동화 도구 전문
2. **Python 시니어 개발자** (11년 경력) - 코드 품질 도구 및 린터 설정 전문
3. **오픈소스 메인테이너** (12년 경력) - 기여자 워크플로우 및 코드 리뷰 프로세스
4. **QA 리드** (10년 경력) - 품질 게이트 및 테스트 자동화

## 📋 상세 작업 계획

### 1. Pre-commit 프레임워크 분석

**목표**: 프로젝트에 최적화된 pre-commit 설정 구성

**핵심 Hook 선정**:
```yaml
# 필수 Hooks (Phase 1)
- black: 코드 포맷팅
- ruff: 빠른 린팅 (flake8 대체)
- mypy: 타입 체크

# 추가 Hooks (Phase 2)
- check-yaml: YAML 파일 검증
- check-json: JSON 파일 검증
- check-toml: TOML 파일 검증
- end-of-file-fixer: 파일 끝 개행 문자
- trailing-whitespace: 공백 제거
- check-added-large-files: 큰 파일 방지
- check-merge-conflict: 머지 충돌 마커 검사

# Django 특화 (Phase 3)
- django-upgrade: Django 코드 현대화
- check-django-migrations: 마이그레이션 검증
```

### 2. 성능 최적화 전략

**병렬 실행 설정**:
- `require_serial: false` - 병렬 실행 활성화
- 파일별 캐싱으로 재실행 최소화
- 증분 검사만 수행

**단계별 실행**:
```yaml
# Stage 1: 빠른 검사 (구문, 포맷)
# Stage 2: 린팅
# Stage 3: 타입 체크 (느림)
```

### 3. 개발자 경험 최적화

**자동 수정 가능한 항목**:
- black: 자동 포맷팅
- ruff: `--fix` 옵션으로 자동 수정
- end-of-file-fixer: 자동 수정
- trailing-whitespace: 자동 수정

**건너뛰기 옵션**:
```bash
# 긴급 커밋 시
git commit --no-verify -m "hotfix: critical bug"

# 특정 hook만 실행
pre-commit run black --all-files
```

### 4. 프로젝트별 커스터마이징

**Django 프로젝트 특성 고려**:
- migrations 폴더 제외
- static/media 폴더 제외
- 템플릿 파일 특별 처리
- settings 파일 민감 정보 체크

**파일 패턴 설정**:
```yaml
files: ^django_i18n_noprefix/
exclude: |
    (?x)^(
        .*\.(pyc|pyo|egg-info)|
        \.git|
        \.tox|
        migrations/|
        static/|
        media/
    )
```

### 5. 통합 및 문서화

**기존 도구와 통합**:
- Makefile에 pre-commit 명령어 추가
- CI/CD에서 pre-commit 실행
- IDE 설정과 일치시키기

**문서 업데이트**:
- CONTRIBUTING.md에 pre-commit 가이드 추가
- 첫 기여자를 위한 설정 가이드
- 문제 해결 가이드

## 🎯 구현 계획

### Phase 1: 기본 설정 (10분)
1. `.pre-commit-config.yaml` 생성
2. 필수 hooks 설정 (black, ruff, mypy)
3. 프로젝트별 설정 적용

### Phase 2: 확장 설정 (5분)
1. 추가 유용한 hooks 설정
2. 성능 최적화
3. 제외 패턴 설정

### Phase 3: 통합 (5분)
1. Makefile 업데이트
2. 개발 문서 업데이트
3. 설치 스크립트 업데이트

### Phase 4: 검증 (5분)
1. 모든 파일에 대해 테스트
2. 자동 수정 동작 확인
3. 성능 측정

## 🔍 고려사항

### 호환성
- Python 3.8+ 지원
- Django 4.2+ 호환
- 크로스 플랫폼 (Windows, Mac, Linux)

### 성능
- 대용량 코드베이스에서도 빠른 실행
- 증분 검사로 효율성 극대화
- CI에서는 전체 검사, 로컬에서는 변경분만

### 유연성
- 프로젝트별 커스터마이징 가능
- 단계별 도입 가능
- 기존 워크플로우 방해 최소화

## 📊 예상 결과

### 1. 코드 품질 향상
- 일관된 코드 스타일
- 타입 안정성 향상
- 일반적인 실수 방지

### 2. 개발 속도 향상
- 코드 리뷰 시간 단축
- 자동 수정으로 수동 작업 감소
- CI 실패 감소

### 3. 팀 협업 개선
- 스타일 논쟁 제거
- 자동화된 품질 게이트
- 일관된 코드베이스

## ✅ 체크리스트

- [ ] `.pre-commit-config.yaml` 파일 생성
- [ ] 필수 hooks 설정 (black, ruff, mypy)
- [ ] 추가 유틸리티 hooks 설정
- [ ] Django 특화 hooks 설정
- [ ] 파일 제외 패턴 설정
- [ ] Makefile 통합
- [ ] setup-dev.sh 스크립트 업데이트
- [ ] 개발 문서 업데이트
- [ ] 모든 파일에 대해 테스트 실행
- [ ] CI/CD 통합 준비

---

*작성일: 2025-08-08*
*작업 예상 시간: 25분*
