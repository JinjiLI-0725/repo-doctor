---
name: repo-doctor
description: Audit a Git repository before public release. Check for secret exposure, missing documentation, installability, repository hygiene, and portfolio presentation, then produce a prioritized release-readiness report.
---

# Repo Doctor

Use this skill when a user wants to publish, open-source, showcase, or clean up a Git repository.

## Goal

Determine whether the repository is safe and understandable enough to publish publicly.

Evaluate the repository from four perspectives:

1. Security
2. Reproducibility
3. GitHub presentation
4. Recruiter/user comprehension

## Workflow

### 1. Security

Check:
- `.env` or credentials accidentally tracked
- suspicious secret/API-key patterns
- private keys
- credentials in Git history when history is available
- sensitive config files
- `.gitignore` coverage

Never print detected secret values. Report only filenames and categories.

### 2. Repository hygiene

Check:
- clean working tree
- valid Git remote
- dependency lockfiles
- generated files excluded
- build artifacts excluded
- tests present
- sensible repository structure

### 3. Documentation

Check whether README explains:
- what the project does
- why it exists
- how to install it
- how to run it
- major technologies
- configuration
- API/environment setup

### 4. Portfolio readiness

A recruiter should understand the project in under 30 seconds.

Check for:
- one-sentence value proposition
- live demo URL when applicable
- screenshots or demo media
- clear feature list
- technology stack
- skills demonstrated
- public-safe setup instructions

### 5. Prioritize

Classify findings:

- **BLOCKER** — must fix before public release
- **IMPORTANT** — strongly recommended
- **POLISH** — improves presentation

## Output format

### Release verdict

READY / READY WITH FIXES / NOT READY

### Blockers

Security or release issues that must be fixed.

### Important improvements

Documentation, installation, or usability issues.

### Portfolio improvements

Changes that improve GitHub presentation.

### Recommended next actions

A short ordered checklist.

When a local shell is available, run:

```bash
python3 scripts/audit_repo.py <repo-path>
```

Use the script output as evidence, then add any qualitative observations the script cannot infer.
