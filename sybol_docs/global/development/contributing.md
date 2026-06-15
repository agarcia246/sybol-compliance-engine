# Contributing to Sybol

## Purpose

This document defines the workflow, standards, and process for contributing code to the Sybol project.

---

## Getting Started

Before contributing:

1. Read [Getting Started](getting-started.md) to set up your environment
2. Review [Coding Standards](coding-standards.md) for code quality requirements
3. Understand [Testing Strategy](testing-strategy.md) for test expectations
4. Review project architecture in `docs/architecture/`

---

## Git Workflow

### Branch Strategy

We follow **Git Flow** with these branch types:

| Branch Type | Naming | Purpose | Base |
|-------------|--------|---------|------|
| Main | `main` | Production-ready code | - |
| Develop | `develop` | Integration branch | `main` |
| Feature | `feature/<description>` | New features | `develop` |
| Bugfix | `bugfix/<description>` | Non-critical fixes | `develop` |
| Hotfix | `hotfix/<description>` | Critical production fixes | `main` |
| Release | `release/<version>` | Release preparation | `develop` |

### Branch Naming Conventions

Use descriptive, kebab-case names:

```bash
# Features
feature/credential-revocation
feature/multi-factor-authentication
feature/dashboard-analytics

# Bugfixes
bugfix/user-email-validation
bugfix/jwt-expiration-check

# Hotfixes
hotfix/security-vulnerability-CVE-2024-1234
hotfix/database-connection-leak
```

### Creating a Feature Branch

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/my-new-feature

# Push branch to remote
git push -u origin feature/my-new-feature
```

### Keeping Branch Updated

```bash
# Regularly sync with develop
git checkout develop
git pull origin develop
git checkout feature/my-new-feature
git merge develop

# Or use rebase (cleaner history)
git rebase develop
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring (no behavior change)
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, tooling

**Scope**: Service or component (optional)

**Subject**: Short description (50 chars max, imperative mood)

**Body**: Detailed explanation (optional)

**Footer**: References to issues (optional)

### Examples

```bash
# Simple commit
git commit -m "feat(backoffice): add user deletion endpoint"

# Detailed commit
git commit -m "fix(businessLogic): prevent duplicate credential creation

When multiple requests arrive simultaneously, credentials were created
multiple times. Added database unique constraint and transaction handling.

Fixes #142"

# More examples
git commit -m "docs: update API documentation for catalog service"
git commit -m "test(propagate): add integration tests for email delivery"
git commit -m "refactor(auth): simplify JWT validation logic"
git commit -m "chore: upgrade express to version 4.18.3"
```

### Atomic Commits

Make small, focused commits:

```bash
# Bad - Multiple unrelated changes
git commit -m "Add feature, fix bug, update docs"

# Good - Separate commits
git commit -m "feat: add user export endpoint"
git commit -m "fix: correct email validation regex"
git commit -m "docs: update user management guide"
```

---

## Pull Request Process

### Before Opening a PR

Complete this checklist:

- [ ] Code follows [Coding Standards](coding-standards.md)
- [ ] All tests pass (`npm test`)
- [ ] New tests added for new features
- [ ] Code coverage maintained (>80%)
- [ ] ESLint passes without errors (`npm run lint`)
- [ ] Commits follow commit message guidelines
- [ ] Branch is up to date with `develop`
- [ ] Documentation updated if needed

### Creating a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/my-new-feature
   ```

2. **Open PR on GitHub**:
   - Go to repository
   - Click "Pull requests" → "New pull request"
   - Base: `develop`, Compare: `feature/my-new-feature`
   - Fill in PR template

3. **PR Title Format**:
   ```
   [Type] Brief description
   ```
   
   Examples:
   - `[Feature] Add credential revocation endpoint`
   - `[Bugfix] Fix JWT expiration validation`
   - `[Hotfix] Resolve database connection pool leak`

4. **PR Description Template**:

   ```markdown
   ## Description
   Brief summary of changes.

   ## Type of Change
   - [ ] Bug fix (non-breaking change fixing an issue)
   - [ ] New feature (non-breaking change adding functionality)
   - [ ] Breaking change (fix or feature causing existing functionality to change)
   - [ ] Documentation update

   ## Changes Made
   - Added credential revocation endpoint
   - Updated database schema
   - Added unit and integration tests

   ## Testing
   - Tested manually with Postman
   - All unit tests pass
   - Integration tests added and passing

   ## Screenshots (if applicable)
   Attach screenshots of UI changes.

   ## Related Issues
   Closes #123, Relates to #456

   ## Checklist
   - [x] Code follows coding standards
   - [x] Self-review completed
   - [x] Tests added/updated
   - [x] Documentation updated
   - [x] No breaking changes (or documented)
   ```

---

## Code Review Process

### Requesting Review

1. Assign reviewers (at least 2 team members)
2. Add relevant labels (`feature`, `bugfix`, `needs-review`)
3. Link related issues
4. Ensure CI checks pass

### Reviewer Responsibilities

Reviewers check:

- **Functionality**: Does it work as intended?
- **Code Quality**: Follows standards and best practices?
- **Tests**: Adequate coverage and quality?
- **Security**: No vulnerabilities introduced?
- **Performance**: No obvious performance issues?
- **Documentation**: README, API docs updated?

### Review Comments

Be constructive and specific:

```markdown
# Good comments
❌ Suggestion: Consider using async/await here instead of .then() for consistency
❓ Question: Why are we using setTimeout here? Could this cause race conditions?
💡 Nitpick: This variable could be renamed to `activeUsers` for clarity
✅ Looks good!

# Avoid
❌ This is wrong
❌ Don't do this
```

### Addressing Feedback

1. **Read all comments** before responding
2. **Respond to each comment**:
   - "Fixed in commit abc123"
   - "Good point, I changed it to X"
   - "I kept it as-is because Y"
3. **Push updates**:
   ```bash
   git add .
   git commit -m "refactor: address PR feedback"
   git push
   ```
4. **Request re-review** after changes
5. **Resolve conversations** when addressed

---

## Code Review Checklist

### For Authors

Before requesting review:

- [ ] Self-review completed (review your own diff)
- [ ] All CI checks passing
- [ ] Tests added for new code
- [ ] No debug code (console.log, commented code)
- [ ] No merge conflicts
- [ ] Branch up to date with base
- [ ] Commits are clean and logical

### For Reviewers

When reviewing:

- [ ] Understand the context (read linked issues)
- [ ] Test locally if needed
- [ ] Check for security issues
- [ ] Verify test coverage
- [ ] Ensure documentation is updated
- [ ] Check for code duplication
- [ ] Verify error handling
- [ ] Look for edge cases
- [ ] Approve only if confident

---

## Merging

### Merge Requirements

PR can be merged when:

- ✅ At least 2 approvals from reviewers
- ✅ All CI checks pass
- ✅ No unresolved conversations
- ✅ Branch is up to date with base
- ✅ No merge conflicts

### Merge Strategy

**Squash and Merge** (preferred for feature branches):

```bash
# GitHub UI: "Squash and merge"
# Combines all commits into one clean commit
```

**Merge Commit** (for release branches):

```bash
# GitHub UI: "Create a merge commit"
# Preserves branch history
```

**Rebase and Merge** (for simple changes):

```bash
# GitHub UI: "Rebase and merge"
# Linear history
```

### After Merge

1. Delete feature branch (GitHub offers this automatically)
2. Update your local repository:
   ```bash
   git checkout develop
   git pull origin develop
   git branch -d feature/my-new-feature
   ```
3. Close related issues if not auto-closed

---

## Definition of Done

A task is complete when:

- [ ] Code written and follows standards
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests added (if applicable)
- [ ] Manual testing completed
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] CI/CD pipeline passes
- [ ] Deployed to development environment
- [ ] Verified in development
- [ ] No known bugs or issues
- [ ] PR merged and branch deleted

---

## Release Process

### 1. Prepare Release Branch

```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0
```

### 2. Update Version Numbers

Update `package.json` in all services:

```json
{
  "version": "1.2.0"
}
```

### 3. Update CHANGELOG.md

```markdown
## [1.2.0] - 2024-03-15

### Added
- Credential revocation endpoint
- Multi-factor authentication

### Changed
- Improved credential validation logic

### Fixed
- JWT expiration check bug
- Email validation regex

### Security
- Updated dependencies with security vulnerabilities
```

### 4. Create Release PR

Open PR from `release/v1.2.0` to `main`:

- Title: `Release v1.2.0`
- Description: Highlight major changes
- Tag reviewers
- Ensure all tests pass

### 5. Merge to Main

After approval:

```bash
# Merge release branch to main
git checkout main
git merge --no-ff release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags
```

### 6. Merge Back to Develop

```bash
git checkout develop
git merge --no-ff release/v1.2.0
git push origin develop
```

### 7. Deploy to Production

Follow deployment procedures in `docs/operations/`.

### 8. Cleanup

```bash
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

---

## Hotfix Process

For critical production issues:

### 1. Create Hotfix Branch

```bash
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix
```

### 2. Implement Fix

Make minimal changes to fix the issue:

```bash
# Fix the issue
git add .
git commit -m "fix: resolve critical security vulnerability"
```

### 3. Test Thoroughly

```bash
npm test
npm run lint
# Manual testing
```

### 4. Create Hotfix PR

Open PR to `main`:

- Title: `[Hotfix] Critical security vulnerability`
- Mark as urgent
- Request immediate review

### 5. Deploy After Merge

```bash
git checkout main
git pull origin main
git tag -a v1.2.1 -m "Hotfix: Security vulnerability"
git push origin main --tags

# Merge to develop
git checkout develop
git merge main
git push origin develop
```

---

## Best Practices

### Communication

- Comment on issues before starting work
- Ask questions early
- Update team on progress
- Notify of blockers immediately

### Code Quality

- Write self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Remove dead code

### Testing

- Write tests before or alongside code (TDD encouraged)
- Test edge cases and error scenarios
- Maintain or improve coverage

### Documentation

- Update README for significant changes
- Document API changes
- Add inline comments for complex logic

---

## Common Scenarios

### Fixing a Bug

1. Create issue describing bug
2. Create `bugfix/` branch from `develop`
3. Write failing test reproducing bug
4. Fix bug
5. Ensure test passes
6. Open PR with "Fixes #issue-number"

### Adding a Feature

1. Discuss feature in issue
2. Get approval from team lead
3. Create `feature/` branch from `develop`
4. Implement with tests
5. Update documentation
6. Open PR for review

### Updating Dependencies

1. Create `chore/update-dependencies` branch
2. Update `package.json`
3. Run `npm install`
4. Test thoroughly
5. Check for breaking changes
6. Open PR with details

---

## Getting Help

- **Questions**: Open issue with `question` label
- **Bugs**: Open issue with `bug` label
- **Discussions**: Use team chat channel
- **Urgent**: Contact team lead directly

---

## See Also

- [Getting Started](getting-started.md) - Initial setup
- [Coding Standards](coding-standards.md) - Code quality
- [Testing Strategy](testing-strategy.md) - Testing approach
- [Repository Structure](repository-structure.md) - Codebase organization

---

## Quick Reference

```bash
# Create feature branch
git checkout -b feature/my-feature develop

# Commit with message
git commit -m "feat(service): add new endpoint"

# Update branch from develop
git checkout develop && git pull
git checkout feature/my-feature
git merge develop

# Push branch
git push -u origin feature/my-feature

# After PR merge, cleanup
git checkout develop && git pull
git branch -d feature/my-feature
```
