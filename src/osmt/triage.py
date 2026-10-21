"""Issue and PR triage helpers."""

from __future__ import annotations

from typing import Any

from .utils import days_since, format_age, github_get, parse_datetime


def fetch_issues(owner: str, repo: str, state: str = "open", per_page: int = 50, limit: int = 100) -> list[dict]:
    """Fetch issues (includes PRs) from a public repository."""
    items: list[dict] = []
    page = 1
    while len(items) < limit:
        data = github_get(
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": min(per_page, limit - len(items)), "page": page, "sort": "updated"},
        )
        if not data:
            break
        items.extend(data)
        if len(data) < per_page:
            break
        page += 1
    return items[:limit]


def score_item(item: dict) -> int:
    """Simple priority score: older + more comments = higher score."""
    updated = parse_datetime(item.get("updated_at"))
    age = days_since(updated) or 0
    comments = item.get("comments", 0) or 0
    # Weight age a bit more than raw comment count
    return age * 2 + comments * 3


def enrich_item(item: dict) -> dict:
    updated = parse_datetime(item.get("updated_at"))
    created = parse_datetime(item.get("created_at"))
    is_pr = "pull_request" in item
    return {
        "number": item.get("number"),
        "title": item.get("title", ""),
        "url": item.get("html_url"),
        "is_pr": is_pr,
        "type": "PR" if is_pr else "Issue",
        "state": item.get("state"),
        "labels": [lbl.get("name") for lbl in item.get("labels", []) if isinstance(lbl, dict)],
        "comments": item.get("comments", 0),
        "author": (item.get("user") or {}).get("login"),
        "created_at": created.isoformat() if created else None,
        "updated_at": updated.isoformat() if updated else None,
        "age_days": days_since(updated),
        "age_display": format_age(days_since(updated)),
        "score": score_item(item),
    }


def triage(owner: str, repo: str, limit: int = 50) -> list[dict]:
    raw = fetch_issues(owner, repo, limit=limit)
    enriched = [enrich_item(item) for item in raw]
    enriched.sort(key=lambda x: x["score"], reverse=True)
    return enriched


def find_stale(owner: str, repo: str, days: int = 90, limit: int = 100) -> list[dict]:
    items = triage(owner, repo, limit=limit)
    return [item for item in items if (item.get("age_days") or 0) >= days]
