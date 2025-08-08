#!/bin/bash

# django-i18n-noprefix 릴리즈 헬퍼 스크립트
# 로컬에서 릴리즈 준비 및 검증을 수행합니다.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수: 메시지 출력
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 함수: 확인 프롬프트
confirm() {
    read -p "$1 (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    return 0
}

# 헤더 출력
echo "======================================"
echo "  Django i18n No-Prefix Release Tool"
echo "======================================"
echo

# 1. Git 상태 확인
print_info "Git 상태 확인 중..."

# 커밋되지 않은 변경사항 확인
if [[ -n $(git status -s) ]]; then
    print_error "커밋되지 않은 변경사항이 있습니다!"
    git status -s
    echo
    if ! confirm "계속 진행하시겠습니까?"; then
        exit 1
    fi
fi

# 현재 브랜치 확인
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    print_warning "현재 브랜치가 main이 아닙니다: $CURRENT_BRANCH"
    if ! confirm "계속 진행하시겠습니까?"; then
        exit 1
    fi
fi

print_success "Git 상태 정상"
echo

# 2. 버전 확인
print_info "버전 정보 확인 중..."

# __version__.py에서 버전 읽기
VERSION_FILE="django_i18n_noprefix/__version__.py"
if [[ ! -f "$VERSION_FILE" ]]; then
    print_error "$VERSION_FILE 파일을 찾을 수 없습니다!"
    exit 1
fi

CURRENT_VERSION=$(python -c "exec(open('$VERSION_FILE').read()); print(__version__)")
print_info "현재 버전: $CURRENT_VERSION"

# 새 버전 입력 받기
read -p "새 버전 번호 (현재: $CURRENT_VERSION): " NEW_VERSION

if [[ -z "$NEW_VERSION" ]]; then
    print_error "버전 번호를 입력해주세요!"
    exit 1
fi

# 버전 형식 검증 (SemVer)
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9\.]+)?(\+[a-zA-Z0-9\.]+)?$ ]]; then
    print_error "잘못된 버전 형식입니다! (예: 1.0.0, 1.0.0-beta.1)"
    exit 1
fi

print_success "새 버전: $NEW_VERSION"
echo

# 3. 테스트 실행
print_info "테스트 실행 중..."

if command -v pytest &> /dev/null; then
    echo "pytest 실행..."
    if ! pytest tests/ -q; then
        print_error "테스트 실패!"
        if ! confirm "테스트 실패에도 계속 진행하시겠습니까?"; then
            exit 1
        fi
    else
        print_success "모든 테스트 통과"
    fi
else
    print_warning "pytest가 설치되지 않았습니다. 테스트를 건너뜁니다."
fi
echo

# 4. 코드 품질 검사
print_info "코드 품질 검사 중..."

# Black 검사
if command -v black &> /dev/null; then
    echo "Black 포맷 검사..."
    if ! black --check . > /dev/null 2>&1; then
        print_warning "코드 포맷이 맞지 않습니다!"
        if confirm "Black으로 자동 포맷을 적용하시겠습니까?"; then
            black .
            print_success "코드 포맷 적용 완료"
        fi
    else
        print_success "코드 포맷 정상"
    fi
fi

# Ruff 검사
if command -v ruff &> /dev/null; then
    echo "Ruff 린트 검사..."
    if ! ruff check . > /dev/null 2>&1; then
        print_warning "린트 오류가 있습니다!"
        ruff check .
        if ! confirm "린트 오류에도 계속 진행하시겠습니까?"; then
            exit 1
        fi
    else
        print_success "린트 검사 통과"
    fi
fi
echo

# 5. 버전 업데이트
print_info "버전 파일 업데이트 중..."

# __version__.py 업데이트
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" "$VERSION_FILE"
rm -f "${VERSION_FILE}.bak"
print_success "__version__.py 업데이트 완료"

# CHANGELOG 업데이트 확인
if [[ -f "CHANGELOG.md" ]]; then
    print_warning "CHANGELOG.md를 업데이트하는 것을 잊지 마세요!"
fi
echo

# 6. 빌드 테스트
print_info "패키지 빌드 테스트 중..."

# 기존 빌드 제거
rm -rf dist/ build/ *.egg-info

# 빌드
if command -v python &> /dev/null; then
    python -m pip install --quiet build
    python -m build > /dev/null 2>&1

    if [[ -d "dist" ]] && [[ -n $(ls -A dist/) ]]; then
        print_success "패키지 빌드 성공"
        ls -lh dist/
    else
        print_error "패키지 빌드 실패!"
        exit 1
    fi
else
    print_error "Python을 찾을 수 없습니다!"
    exit 1
fi
echo

# 7. 체크리스트
print_info "릴리즈 전 체크리스트:"
echo

CHECKLIST=(
    "CHANGELOG.md가 업데이트되었나요?"
    "README.md가 최신 상태인가요?"
    "문서가 새 버전을 반영하나요?"
    "모든 테스트가 통과했나요?"
    "GitHub Issues가 정리되었나요?"
)

ALL_CHECKED=true
for item in "${CHECKLIST[@]}"; do
    if confirm "  ✓ $item"; then
        print_success "확인됨"
    else
        print_warning "확인 필요"
        ALL_CHECKED=false
    fi
done
echo

if [[ "$ALL_CHECKED" = false ]]; then
    print_warning "체크리스트를 모두 확인해주세요!"
    if ! confirm "그래도 계속 진행하시겠습니까?"; then
        exit 1
    fi
fi

# 8. Git 커밋 및 태그
print_info "Git 커밋 및 태그 생성 준비..."

# 변경사항 커밋
if [[ -n $(git status -s) ]]; then
    echo "변경사항을 커밋합니다..."
    git add .
    git commit -m "Release version $NEW_VERSION"
    print_success "커밋 완료"
fi

# 태그 생성
TAG_NAME="v$NEW_VERSION"
if git tag | grep -q "^${TAG_NAME}$"; then
    print_error "태그 $TAG_NAME가 이미 존재합니다!"
    exit 1
fi

if confirm "태그 $TAG_NAME를 생성하시겠습니까?"; then
    git tag -a "$TAG_NAME" -m "Release version $NEW_VERSION"
    print_success "태그 생성 완료: $TAG_NAME"
else
    print_warning "태그 생성을 건너뛰었습니다."
fi
echo

# 9. 최종 확인
echo "======================================"
echo "  릴리즈 준비 완료!"
echo "======================================"
echo
print_info "다음 단계:"
echo "  1. 변경사항 푸시: git push origin main"
echo "  2. 태그 푸시: git push origin $TAG_NAME"
echo "  3. GitHub Actions가 자동으로 배포를 진행합니다"
echo
print_warning "주의: 태그를 푸시하면 자동으로 배포가 시작됩니다!"
echo

# 자동 푸시 옵션
if confirm "지금 푸시하시겠습니까?"; then
    git push origin main
    git push origin "$TAG_NAME"
    print_success "푸시 완료! GitHub Actions에서 배포 진행 상황을 확인하세요."
    echo "https://github.com/jinto/django-i18n-noprefix/actions"
else
    print_info "수동으로 푸시해주세요:"
    echo "  git push origin main"
    echo "  git push origin $TAG_NAME"
fi

echo
print_success "릴리즈 준비가 완료되었습니다!"
