# Repository settings

Settings that GitHub stores outside the repository and that no commit can enable. Everything in this
file has to be switched on by a repository admin. Without them, `.github/CODEOWNERS` and the "protected
`main`" statements elsewhere in these docs describe intent, not enforcement.

> **How to know whether it is working:** push a trivial commit straight to `main` from an account that is
> **not** on the bypass list (or use a throwaway admin-less account). It must be rejected with
> "protected branch hook declined" or "Changes must be made through a pull request". When this project's
> maintainers last tried (2026-10-16/17), the push was **accepted** and the branches API reported
> `protected: false`, so protection was not in force. `GET /repos/{owner}/{repo}/branches/main` →
> `"protected": true` is the quick check; a ruleset with *Active* enforcement sets it.

## 1. Branch ruleset for `main`

Settings → Rules → Rulesets → *New branch ruleset* (free on public repositories).

| Setting | Value |
|---|---|
| Enforcement status | **Active** (not *Disabled*, not *Evaluate*) |
| Target branches | *Include default branch* (or `main`) |
| Bypass list | Empty while you test; afterwards only a break-glass admin role, never an account that also pushes routinely |
| Restrict deletions | on |
| Block force pushes | on |
| Require a pull request before merging | on, 0 or 1 approvals (see the single-maintainer note below) |
| Require status checks to pass | on, with the checks listed below |
| Require branches to be up to date | optional; stricter and slower |
| Require signed commits | **off** unless every contributor (including bots such as Dependabot and Claude Code sessions) can sign |
| Require linear history | optional; matches the squash-merge habit |

### Required status checks

These are the job names GitHub shows for the workflows in `.github/workflows/`:

| Check | Workflow |
|---|---|
| `lint-and-test (3.11)`, `lint-and-test (3.12)`, `lint-and-test (3.13)` | `ci` |
| `unit-macos` | `ci` |
| `integration` | `ci` |
| `container-isolation` | `ci` |
| `dependency-audit` | `ci` |
| `workflow-hygiene` | `ci` |
| `secrets-and-sast` | `security-scan` |

`network-integration` (weekly / manual) and `release` (tags / manual) are intentionally **not** required.
A required check that never reports (for example after renaming a job) blocks every pull request, so update
this list whenever a job is renamed.

### Single-maintainer note

`CODEOWNERS` lists `@joeabur` for every security-critical path. With "Require review from Code Owners" on, GitHub
does not count an author's own approval, so the sole owner cannot merge their own pull request. Pick one:

1. add a second owner or a team to `.github/CODEOWNERS` (recommended for anything beyond a personal project);
2. keep Code Owner review **off** and rely on required status checks only; or
3. put the owner on the ruleset's bypass list **and** accept that this also lets them push to `main` directly,
   which is exactly what the 2026-10-17 test observed.

## 2. Release environment and tags

- Settings → Environments → *New environment* `release`: **Required reviewers** = a maintainer other than the
  person who tags; restrict **Deployment branches and tags** to `v*` tags.
- Settings → Rules → *New tag ruleset*: pattern `v*`, restrict creation and updates to maintainers, block deletion.
- Rehearse before the first real release: Actions → **release** → *Run workflow*. It builds, uploads the artifact,
  downloads it again and verifies the checksums, without publishing anything.

## 3. Security features

| Setting | Why |
|---|---|
| Code security → **Private vulnerability reporting** | `SECURITY.md` tells reporters to use it |
| Code security → **Secret scanning** and **Push protection** | second line of defence next to the Gitleaks self-scan |
| Code security → **Dependabot alerts** and **security updates** | `.github/dependabot.yml` already handles version updates |
| Actions → General → **Fork pull request workflows**: require approval for first-time contributors | untrusted code should not run unattended |
| Actions → General → **Workflow permissions**: *Read repository contents* | matches the `permissions:` blocks; jobs request more only where needed |
| Actions → General → *Allow* only actions pinned by SHA (**Require actions to be pinned to a full-length commit SHA**) | enforces what `scripts/check_workflows.py` checks in CI |

## 4. Verify it, then keep verifying

1. Open a pull request with a deliberately failing check (for example a lint error) and confirm the merge button
   is blocked.
2. Try `git push origin HEAD:main` from a non-bypass account and confirm it is rejected.
3. Try `git push --force origin main` and `git push origin --delete main` from the same account (against a
   scratch fork if you prefer) and confirm both are rejected.
4. Re-run the quick check (`"protected": true`) after any change to the ruleset.

## Further recommendations

- **CodeQL / code scanning**: enable GitHub's default CodeQL setup for Python and Actions as an
  independent second opinion alongside reposcan's own self-scan. This is a repository setting and is not stored here.
- **Release provenance**: when the first real tag is cut, consider build-provenance attestations for the
  published artifacts. `release.yml` has not yet been run on a real tag.
