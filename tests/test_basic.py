"""Basic tests that do not require network access."""

from osmt.release_notes import classify_commit
from osmt.utils import format_age


def test_classify_commit_conventional():
    ctype, subject = classify_commit("feat(cli): add stale command")
    assert ctype == "feat"
    assert "stale" in subject


def test_classify_commit_breaking():
    ctype, _ = classify_commit("fix!: drop support for Python 3.8")
    assert ctype == "breaking"


def test_classify_commit_fallback():
    ctype, subject = classify_commit("Fix the login bug on Safari")
    assert ctype == "fix"
    assert "login" in subject.lower()


def test_format_age():
    assert format_age(0) == "today"
    assert format_age(1) == "1 day"
    assert format_age(5) == "5 days"
    assert format_age(None) == "?"
