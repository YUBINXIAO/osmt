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


def test_classify_commit_breaking_footer():
    message = "feat(api): rename endpoint\n\nBREAKING CHANGE: /v1/foo is now /v1/bar"
    ctype, subject = classify_commit(message)
    assert ctype == "breaking"
    assert subject == "rename endpoint"


def test_classify_commit_breaking_hyphen_footer():
    message = "feat(api): rename endpoint\n\nBREAKING-CHANGE: /v1/foo is now /v1/bar"
    ctype, subject = classify_commit(message)
    assert ctype == "breaking"
    assert subject == "rename endpoint"


def test_classify_commit_breaking_footer_after_body():
    message = (
        "feat(api): rename endpoint\n"
        "\n"
        "Clients must move to the new path.\n"
        "\n"
        "BREAKING CHANGE: /v1/foo is now /v1/bar"
    )
    ctype, subject = classify_commit(message)
    assert ctype == "breaking"
    assert subject == "rename endpoint"


def test_classify_commit_breaking_mention_is_not_a_footer():
    message = "feat(api): rename endpoint\n\nThis is not a breaking change."
    ctype, subject = classify_commit(message)
    assert ctype == "feat"
    assert subject == "rename endpoint"


def test_classify_commit_fallback():
    ctype, subject = classify_commit("Fix the login bug on Safari")
    assert ctype == "fix"
    assert "login" in subject.lower()


def test_classify_commit_heuristic_ignores_unrelated_words():
    assert classify_commit("Update address parsing")[0] == "other"
    assert classify_commit("Rename prefix option")[0] == "other"
    assert classify_commit("Renew certificates")[0] == "other"


def test_classify_commit_heuristic_matches_whole_words():
    assert classify_commit("Add a widget")[0] == "feat"
    assert classify_commit("Adds a widget")[0] == "feat"
    assert classify_commit("Added a widget")[0] == "feat"
    assert classify_commit("Update the docs")[0] == "docs"
    assert classify_commit("Update documentation")[0] == "docs"
    assert classify_commit("Clean up the parser")[0] == "refactor"
    assert classify_commit("cleanup the parser")[0] == "refactor"


def test_format_age():
    assert format_age(0) == "today"
    assert format_age(1) == "1 day"
    assert format_age(5) == "5 days"
    assert format_age(None) == "?"
