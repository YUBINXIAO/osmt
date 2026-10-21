# Open Source Maintainer Toolkit (osmt)

**Reduce the invisible work of maintaining open-source projects.**

osmt is a lightweight CLI toolkit designed for GitHub maintainers. It helps with the most time-consuming parts of project stewardship: issue triage, spotting stale items, preparing release notes, and generating a quick health overview of a repository.

It works with the public GitHub API (no token required for public repos, though a token raises rate limits). The output is structured and human-readable so you can act quickly or feed it into an AI coding assistant (Codex, Cursor, Cline, etc.) for deeper analysis or automated suggestions.

## Why this exists

Maintainers spend a large fraction of their time on non-coding work: reading issues, deciding what to close, writing release notes, and keeping the project healthy. Small tools that surface the right information at the right time reduce that load. osmt focuses on that surface area.

## Features

- **Triage** – List open issues and pull requests with age, comment count, labels, and a simple priority score.
- **Stale detection** – Highlight issues/PRs that have been inactive for a configurable number of days.
- **Release notes** – Generate a markdown release-notes draft from recent commits (grouped by conventional commit type when possible).
- **Repo health** – Quick snapshot of open issues, open PRs, recent activity, and basic metadata.
- Rich terminal output and optional JSON/markdown export for further processing.

## Installation

```bash
# From source (recommended while the package is young)
git clone https://github.com/YUBINXIAO/osmt.git
cd osmt
pip install -e ".[dev]"
```

Or install the latest release once published:

```bash
pip install osmt
```

## Quick start

```bash
# Health overview of a popular repository
osmt health openai/codex

# Triage open issues (limit to 30 most relevant)
osmt triage openai/codex --limit 30

# Find items inactive for more than 60 days
osmt stale openai/codex --days 60

# Draft release notes from the last 50 commits
osmt release-notes openai/codex --commits 50 --output notes.md
```

### Example output (triage)

Running `osmt triage openai/codex --limit 5` produces a priority-sorted table you can immediately act on or paste into an AI coding session:

```
Triage: openai/codex (top 5)
┌─────┬──────┬─────────┬──────────┬───────┬───────────────────────────────────────────────┐
│   # │ Type │ Age      │ Comments │ Score │ Title                              │
├─────┼──────┼─────────┼──────────┼───────┼───────────────────────────────────────────────┤
│  87 │ PR   │ 12 days  │        5 │    39 │ Fix stale detection for draft PRs │
│ 142 │ Issue│ 45 days  │       12 │   126 │ Add support for monorepo detection│
└─────┴──────┴─────────┴──────────┴───────┴───────────────────────────────────────────────┘
```

Higher scores surface items that have been open longer and have more discussion — the ones that usually need attention first.

### Using a GitHub token (recommended)

Create a classic personal access token with `public_repo` scope and export it:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

The tool automatically uses `GITHUB_TOKEN` or `GH_TOKEN` when present.

## How it helps maintainers (and AI tools)

- Output is designed to be copy-paste friendly into an AI coding session.
- You can pipe or save reports and ask Codex / your preferred agent to:
  - Suggest labels or assignees
  - Draft reply templates
  - Propose which issues to close as stale
  - Improve the generated release notes
- The codebase itself is small and well-structured so that AI coding tools can easily extend it (new commands, better heuristics, GitHub Action integration, etc.).

## Development

```bash
# Run tests
pytest

# Format and lint
black src tests
ruff check src tests
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

If you are an open-source maintainer using this tool and have ideas for reducing maintainer burden further, please open an issue. This project is intentionally small so that suggestions can be implemented quickly.

## Roadmap

- [ ] GitHub Action that posts a weekly triage summary as an issue or discussion
- [ ] Conventional Commit parsing improvements
- [ ] Optional integration with AI APIs for automatic summary generation (opt-in, user-provided key)
- [ ] Support for more Git forges
- [ ] Configurable priority scoring

## License

MIT. See [LICENSE](LICENSE).

---

Built to make the unglamorous parts of open-source maintenance a little lighter.
