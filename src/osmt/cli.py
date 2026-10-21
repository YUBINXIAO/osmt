"""Command-line interface for the Open Source Maintainer Toolkit."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .release_notes import generate_release_notes
from .triage import find_stale, triage
from .utils import github_get

console = Console()


@click.group()
@click.version_option(__version__)
def main() -> None:
    """Open Source Maintainer Toolkit – lighten the load of triage and releases."""


def _parse_repo(repo: str) -> tuple[str, str]:
    if "/" not in repo:
        raise click.BadParameter("Repository must be in owner/repo format")
    owner, name = repo.split("/", 1)
    return owner.strip(), name.strip()


@main.command("triage")
@click.argument("repo")
@click.option("--limit", default=40, show_default=True, help="Max items to fetch and display.")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON instead of a table.")
def triage_cmd(repo: str, limit: int, as_json: bool) -> None:
    """List open issues and PRs sorted by a simple priority score."""
    owner, name = _parse_repo(repo)
    try:
        items = triage(owner, name, limit=limit)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(items, indent=2))
        return

    table = Table(title=f"Triage: {owner}/{name} (top {len(items)})")
    table.add_column("#", justify="right")
    table.add_column("Type", style="cyan")
    table.add_column("Age", style="yellow")
    table.add_column("Comments", justify="right")
    table.add_column("Score", justify="right", style="bold")
    table.add_column("Title")

    for item in items:
        table.add_row(
            str(item["number"]),
            item["type"],
            item["age_display"],
            str(item["comments"]),
            str(item["score"]),
            item["title"][:80],
        )
    console.print(table)
    console.print("\n[dim]Higher score ≈ older + more discussion. Use --json for full details.[/dim]")


@main.command()
@click.argument("repo")
@click.option("--days", default=90, show_default=True, help="Inactivity threshold in days.")
@click.option("--limit", default=100, show_default=True)
@click.option("--json", "as_json", is_flag=True)
def stale(repo: str, days: int, limit: int, as_json: bool) -> None:
    """Show issues and PRs that have been inactive for at least N days."""
    owner, name = _parse_repo(repo)
    try:
        items = find_stale(owner, name, days=days, limit=limit)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(items, indent=2))
        return

    if not items:
        console.print(f"[green]No items inactive for ≥ {days} days.[/green]")
        return

    table = Table(title=f"Stale items in {owner}/{name} (≥ {days} days)")
    table.add_column("#", justify="right")
    table.add_column("Type")
    table.add_column("Age")
    table.add_column("Title")
    for item in items:
        table.add_row(str(item["number"]), item["type"], item["age_display"], item["title"][:90])
    console.print(table)


@main.command("release-notes")
@click.argument("repo")
@click.option("--commits", default=40, show_default=True, help="Number of recent commits to consider.")
@click.option("--output", "-o", type=click.Path(), help="Write markdown to this file instead of stdout.")
def release_notes_cmd(repo: str, commits: int, output: str | None) -> None:
    """Generate a markdown draft of release notes from recent commits."""
    owner, name = _parse_repo(repo)
    try:
        notes = generate_release_notes(owner, name, commit_limit=commits)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    if output:
        Path(output).write_text(notes, encoding="utf-8")
        console.print(f"[green]Wrote release notes to {output}[/green]")
    else:
        click.echo(notes)


@main.command()
@click.argument("repo")
def health(repo: str) -> None:
    """Quick health snapshot of a repository."""
    owner, name = _parse_repo(repo)
    try:
        info = github_get(f"/repos/{owner}/{name}")
        issues = github_get(f"/repos/{owner}/{name}/issues", params={"state": "open", "per_page": 1})
        # Note: the issues endpoint returns both issues and PRs; we also hit pulls for a clearer count when possible
        pulls = github_get(f"/repos/{owner}/{name}/pulls", params={"state": "open", "per_page": 1})
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)

    # The Link header or total count isn't always free; we approximate with the length of a larger fetch if needed.
    # For the health view we show the open_issues_count from the repo object (which includes PRs).
    table = Table(title=f"Health: {owner}/{name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold")

    table.add_row("Description", (info.get("description") or "—")[:80])
    table.add_row("Stars", str(info.get("stargazers_count", 0)))
    table.add_row("Forks", str(info.get("forks_count", 0)))
    table.add_row("Open issues (incl. PRs)", str(info.get("open_issues_count", 0)))
    table.add_row("License", (info.get("license") or {}).get("spdx_id") or "—")
    table.add_row("Default branch", info.get("default_branch", "—"))
    table.add_row("Last push", info.get("pushed_at", "—"))
    table.add_row("Archived", "yes" if info.get("archived") else "no")
    console.print(table)
    console.print("\n[dim]Use `osmt triage` or `osmt stale` for actionable lists.[/dim]")


if __name__ == "__main__":
    main()
