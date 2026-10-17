## What and why

<!-- One or two sentences. Link the issue if there is one. -->

## Checklist

- [ ] `ruff check . && ruff format --check . && mypy && pytest` pass locally
- [ ] New behaviour has tests, including the failure modes (a scanner error must never look like a clean scan)
- [ ] Anything touching subprocesses, redaction, paths, baselines or report output follows `CONTRIBUTING.md`
- [ ] Docs updated (output blocks labelled *observed* or *illustrative*); `python scripts/generate_schema.py` and
      `python scripts/generate_rules_doc.py` re-run if the schema or rules changed
- [ ] No real credentials, personal data or raw scanner output in the diff, tests or description
- [ ] Workflow changes keep actions pinned to full SHAs (`python scripts/verify_pins.py .github/workflows`)

## Security impact

<!-- "None" is a fine answer. Otherwise: what could a hostile repository or scanner output now do differently? -->
