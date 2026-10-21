"""Release notes generation from recent commits."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from .utils import github_get


CONVENTIONAL_RE = re.compile(
    r"^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?: (?P<subject>.+)$",
    re.IGNORECASE,
)


def fetch_commits(owner: str, repo: str, limit: int = 50) -> list[dict]:
    data = github_get(
        f"/repos/{owner}/{repo}/commits",
        params={"per_page": min(limit, 100)},
    )
    return data[:limit]


def classify_commit(message: str) -> tuple[str, str]:
    first_line = message.split("\n", 1)[0].strip()
    match = CONVENTIONAL_RE.match(first_line)
    if match:
        ctype = match.group("type").lower()
        subject = match.group("subject").strip()
        if match.group("breaking"):
            ctype = "breaking"
        return ctype, subject
    # Fallback heuristics
    lower = first_line.lower()
    if any(k in lower for k in ("fix", "bug", "hotfix")):
        return "fix", first_line
    if any(k in lower for k in ("feat", "feature", "add", "new")):
        return "feat", first_line
    if any(k in lower for k in ("doc", "readme", "typo")):
        return "docs", first_line
    if any(k in lower for k in ("refactor", "clean", "simplify")):
        return "refactor", first_line
    return "other", first_line


def generate_release_notes(owner: str, repo: str, commit_limit: int = 50) -> str:
    commits = fetch_commits(owner, repo, limit=commit_limit)
    groups: dict[str, list[str]] = defaultdict(list)

    type_titles = {
        "breaking": "Breaking Changes",
        "feat": "Features",
        "fix": "Bug Fixes",
        "docs": "Documentation",
        "refactor": "Refactoring",
        "perf": "Performance",
        "test": "Tests",
        "chore": "Chores",
        "ci": "CI",
        "build": "Build",
        "other": "Other Changes",
    }

    for commit in commits:
        sha = commit.get("sha", "")[:7]
        message = (commit.get("commit") or {}).get("message", "")
        author = ((commit.get("commit") or {}).get("author") or {}).get("name", "unknown")
        ctype, subject = classify_commit(message)
        groups[ctype].append(f"- {subject} ({sha}) by {author}")

    lines = [f"# Release notes draft for {owner}/{repo}", "", f"_Based on the last {len(commits)} commits._", ""]

    order = ["breaking", "feat", "fix", "perf", "refactor", "docs", "test", "ci", "build", "chore", "other"]
    for key in order:
        if key in groups and groups[key]:
            lines.append(f"## {type_titles.get(key, key.title())}")
            lines.extend(groups[key])
            lines.append("")

    if not any(groups.values()):
        lines.append("_No commits found._")

    return "\n".join(lines).strip() + "\n"
