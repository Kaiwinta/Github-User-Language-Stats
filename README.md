# Github.User.Language.Stats

Compute a GitHub user language distribution with options to reduce noise from forked repositories and external contributors.

## Why raw totals can be misleading

GitHub's repository language endpoint reports bytes for the whole repository. That includes:

- code from forks
- code from other contributors
- generated or vendored code present in the repository

So raw language totals are repository-level, not strictly "code written by this user".

## Inputs

- `token` (required): GitHub token with repo access
- `output` (default: `languages.json`): Output path
- `owned_only` (default: `true`): Only include repositories owned by the current user
- `include_forks` (default: `false`): Include forked repositories
- `attribution_mode` (default: `raw`):
	- `raw`: sum full repository language bytes
	- `commit_ratio`: weight repository language bytes by owner commit share in that repository
- `timeout_seconds` (default: `20`): HTTP timeout for API calls

## Recommended settings for "what this user wrote"

Use:

- `owned_only: true`
- `include_forks: false`
- `attribution_mode: commit_ratio`

This is still an approximation, but it usually gets closer to personal authorship than raw totals.

## Privacy & Security

This action accesses private repositories only to compute aggregated
language statistics.

- Repository names and URLs are never logged or stored
- Per-repository language data is discarded immediately
- Only global language totals are written to the output file
