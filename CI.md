# CI Readiness — Pre-push Checklist

Run these checks locally before every push or PR.

## Docs-only shortcut

If your diff only touches `.md` files or `docs/` content, skip code checks.
Verify with:

```bash
git status --short
```

## Required checks (all code changes)

```bash
make check
```

This runs lint → format-check → typecheck → test in sequence. If any step
fails, fix it before pushing.

Or run steps individually:

1. **Clean tree** — no accidental untracked files, no `.env` or secrets

   ```bash
   git status --short
   ```

2. **Lint**

   ```bash
   make lint
   ```

3. **Format**

   ```bash
   make format-check
   ```

   If it fails: `make format && make format-check`

4. **Type check**

   ```bash
   make typecheck
   ```

5. **Test**

   ```bash
   make test
   ```

## When to run full coverage

Run `make test-cov` instead of `make test` when:

- Core modules changed (`models/`, `instrumentation/`, `profiler/`)
- Recommender engine or pipeline changed
- Schema files changed
- New exporters or providers added
- Cross-cutting refactor touching 3+ modules

## CI parity

The GitHub Actions CI workflow runs the same checks across Python 3.10–3.14
using `uv`. If `make check` passes locally, CI should pass too.
