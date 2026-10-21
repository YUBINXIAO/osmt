# Contributing to osmt

Thank you for considering a contribution. This project exists to reduce the day-to-day burden on open-source maintainers, so we try to keep the contribution process lightweight.

## Development setup

```bash
git clone https://github.com/YUBINXIAO/osmt.git
cd osmt
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running tests

```bash
pytest
```

## Code style

We use Black and Ruff. Please run them before opening a pull request:

```bash
black src tests
ruff check src tests
```

## Pull requests

1. Open an issue first for larger changes so we can discuss the approach.
2. Keep pull requests focused. One logical change per PR is preferred.
3. Update the README if you add a user-facing feature.
4. Add or update tests when practical.

## Maintainer workflow

As the primary maintainer I review PRs, triage issues, and cut releases. Suggestions that further reduce that workload (better defaults, clearer output for AI tools, GitHub Action templates, etc.) are especially welcome.

## License

By contributing you agree that your contributions will be licensed under the MIT License.
