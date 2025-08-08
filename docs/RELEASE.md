# Release Process

This document describes the release process for django-i18n-noprefix.

## Prerequisites

### Required Accounts
- PyPI account with upload permissions
- TestPyPI account for testing
- GitHub repository write access

### Required Secrets
Configure these secrets in GitHub repository settings:

1. **PYPI_API_TOKEN**: PyPI upload token
   - Generate at: https://pypi.org/manage/account/token/
   - Scope: Project-specific (recommended)

2. **TEST_PYPI_API_TOKEN**: TestPyPI upload token
   - Generate at: https://test.pypi.org/manage/account/token/
   - Scope: Project-specific

## Release Workflow

### 1. Prepare Release

#### Update Version
```bash
# Edit django_i18n_noprefix/__version__.py
__version__ = "X.Y.Z"
```

#### Update Changelog
Update `CHANGELOG.md`:
- Move items from "Unreleased" to new version section
- Add release date
- Add comparison link

#### Run Local Validation
```bash
./scripts/release.sh
```

This script will:
- Check git status
- Run tests
- Check code quality
- Build package
- Create git tag

### 2. Trigger Release

Push the tag to trigger automated release:
```bash
git push origin main
git push origin vX.Y.Z
```

### 3. Monitor Deployment

#### GitHub Actions
Monitor the release workflow:
https://github.com/jinto/django-i18n-noprefix/actions

Stages:
1. **Test**: Run test matrix
2. **Build**: Create distribution packages
3. **TestPyPI**: Deploy to test environment
4. **PyPI**: Deploy to production (requires manual approval)
5. **Release**: Create GitHub release
6. **Verify**: Test installation from PyPI

#### Manual Approval
The workflow pauses before PyPI deployment:
1. Go to Actions → Release workflow
2. Review TestPyPI deployment
3. Click "Review deployments"
4. Approve "pypi" environment

### 4. Post-Release Verification

#### Check PyPI
- Package page: https://pypi.org/project/django-i18n-noprefix/
- Version specific: https://pypi.org/project/django-i18n-noprefix/X.Y.Z/

#### Test Installation
```bash
pip install django-i18n-noprefix==X.Y.Z
python -c "import django_i18n_noprefix; print(django_i18n_noprefix.__version__)"
```

#### Check GitHub Release
- Releases page: https://github.com/jinto/django-i18n-noprefix/releases
- Verify assets (wheel, sdist)
- Verify release notes

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Pre-releases
- Alpha: `X.Y.Z-alpha.N` (early testing)
- Beta: `X.Y.Z-beta.N` (feature complete, testing)
- RC: `X.Y.Z-rc.N` (release candidate)

## Rollback Procedure

If issues are discovered after release:

### 1. Yank from PyPI (if critical)
```bash
# Cannot delete, but can yank (hide)
pip install twine
twine yank django-i18n-noprefix==X.Y.Z
```

### 2. Fix Issues
1. Create bugfix branch
2. Fix issues
3. Update tests
4. Bump patch version

### 3. Release Patch
Follow normal release process with new version.

## Security Considerations

### Token Management
- Use project-scoped tokens (not account-wide)
- Rotate tokens periodically
- Never commit tokens to repository

### Signed Releases (Optional)
For enhanced security, consider:
- GPG signing git tags
- Sigstore signing for packages

### Supply Chain Security
The workflow includes:
- Dependency pinning
- Build artifact verification
- Multi-stage deployment with validation

## Troubleshooting

### Common Issues

#### TestPyPI Upload Fails
- Check token permissions
- Verify package name availability
- Check version doesn't exist

#### PyPI Upload Fails
- Version may already exist (cannot overwrite)
- Check token scope and permissions
- Verify package metadata

#### GitHub Release Creation Fails
- Check workflow permissions
- Verify tag format (must start with 'v')

### Manual Release (Emergency)

If automated release fails:

```bash
# Build package
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  django-i18n-noprefix

# Upload to PyPI
twine upload dist/*

# Create GitHub release manually
gh release create vX.Y.Z dist/* \
  --title "Version X.Y.Z" \
  --notes "Release notes here"
```

## Checklist

### Pre-release
- [ ] All tests passing
- [ ] Code quality checks passing
- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Example project tested

### Release
- [ ] Tag created and pushed
- [ ] GitHub Actions workflow successful
- [ ] TestPyPI deployment verified
- [ ] PyPI deployment approved
- [ ] GitHub release created

### Post-release
- [ ] Installation from PyPI tested
- [ ] Documentation accessible
- [ ] Announcement made (if major release)

## Contact

For release-related issues:
- GitHub Issues: https://github.com/jinto/django-i18n-noprefix/issues
- Maintainer: @jinto
