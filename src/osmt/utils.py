"""Shared utilities for GitHub API access and formatting."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests
from dateutil import parser as date_parser

GITHUB_API = "https://api.github.com"


def get_headers() -> dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "osmt/0.1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_get(path: str, params: dict[str, Any] | None = None) -> Any:
    url = f"{GITHUB_API}{path}" if path.startswith("/") else path
    response = requests.get(url, headers=get_headers(), params=params or {}, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = date_parser.parse(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None


def days_since(dt: datetime | None) -> int | None:
    if dt is None:
        return None
    now = datetime.now(timezone.utc)
    return (now - dt).days


def format_age(days: int | None) -> str:
    if days is None:
        return "?"
    if days == 0:
        return "today"
    if days == 1:
        return "1 day"
    return f"{days} days"
