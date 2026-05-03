# Contributing to Dift

Thanks for your interest in contributing to Dift.

We welcome thoughtful contributions that improve the project for real users.

## Our Goal

Dift is an open-source tool for comparing datasets and building trust in data changes.

We value contributions that improve usability, reliability, performance, documentation clarity, test coverage, and developer experience.

## Ways to Contribute

### Code
- Bug fixes
- New comparison features
- Performance improvements
- File format support
- Better CLI UX
- Better reports

### Documentation
- Improve README clarity
- Add examples
- Improve installation guides
- Fix incorrect docs

### Quality
- Add tests
- Improve CI workflows
- Refactor maintainable code

---

## How to Contribute to Dift

- Fork the repository
- Clone your fork
- Create a new branch
- Set up the project (venv + install)
- Make your changes
- Test your changes (pytest, ruff)
- Commit your work
- Push to your fork
- Open a Pull Request

---

## Keep Your Branch Up-to-Date

Before opening a Pull Request, make sure your branch is up-to-date with the latest version of `main`.

This helps prevent merge conflicts and ensures your changes work with the current codebase.

```bash
git checkout main
git pull upstream main

git checkout your-branch
git rebase upstream/main
```

If you forked the repository, add the original repo as `upstream`:

```bash
git remote add upstream https://github.com/ReginaldErzoah/Dift.git
```

> Pull requests that are significantly behind `main` may be requested to update before review.

---

## Development Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pip install -e .
pytest
ruff check .
```

---

## Spam / Low-Value Pull Requests Policy

The following pull requests may be closed without merge:

- whitespace-only changes
- empty formatting edits
- punctuation-only changes with no value
- unrelated drive-by edits
- automated changes without context
- AI-generated PRs with no verification
- duplicate pull requests
- issue farming / contribution farming
- no-op changes

---

## Pull Request Requirements

Please explain:

- What changed
- Why it changed
- How it was tested

---

## Thank You
Meaningful contributions help make Dift the standard open-source dataset diff tool.