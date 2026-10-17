"""Tests for the helper scripts and packaging metadata."""

from __future__ import annotations

import importlib.util
import subprocess
import tomllib
from pathlib import Path
from types import ModuleType

import pytest

from ..helpers import REPO_ROOT


def load_script(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pinned_actions_are_parsed_from_the_real_workflows() -> None:
    module = load_script("verify_pins")
    pins = module.parse_pins(REPO_ROOT / ".github" / "workflows")
    actions = {repo for _file, repo, _tag, _sha in pins}
    assert {"actions/checkout", "actions/setup-python", "github/codeql-action"} <= actions
    assert all(len(sha) == 40 and tag.startswith("v") for _f, _r, tag, sha in pins)


def test_verify_pins_reports_ok_and_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_script("verify_pins")
    good, bad = "a" * 40, "b" * 40
    (tmp_path / "w.yml").write_text(
        f"steps:\n  - uses: acme/good@{good} # v1.0.0\n  - uses: acme/bad@{bad} # v2.0.0\n"
    )
    monkeypatch.setattr(
        module, "upstream_sha", lambda repo, tag, timeout=60: good if repo == "acme/good" else "c" * 40
    )
    assert module.main(["verify_pins.py", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "OK        w.yml: acme/good@v1.0.0" in out and "MISMATCH  w.yml: acme/bad@v2.0.0" in out


def test_verify_pins_treats_a_missing_tag_as_a_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_script("verify_pins")
    (tmp_path / "w.yml").write_text(f"- uses: acme/x@{'d' * 40} # v9.9.9\n")
    monkeypatch.setattr(module, "upstream_sha", lambda repo, tag, timeout=60: None)
    assert module.main(["verify_pins.py", str(tmp_path)]) == 1
    assert "tag not found" in capsys.readouterr().out


def test_upstream_sha_prefers_the_dereferenced_annotated_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_script("verify_pins")
    listing = f"{'1' * 40}\trefs/tags/v1\n{'2' * 40}\trefs/tags/v1^{{}}\n"
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(a[0], 0, stdout=listing, stderr=""),
    )
    assert module.upstream_sha("acme/x", "v1") == "2" * 40


@pytest.mark.parametrize(
    ("repo", "tag"), [("acme/x;rm -rf", "v1"), ("acme/x", "v1 --upload-pack=evil"), ("../x", "v1")]
)
def test_upstream_sha_rejects_odd_inputs(repo: str, tag: str) -> None:
    module = load_script("verify_pins")
    with pytest.raises(ValueError, match="refusing"):
        module.upstream_sha(repo, tag)


def test_package_ships_the_py_typed_marker_it_claims() -> None:
    meta = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    assert "Typing :: Typed" in meta["project"]["classifiers"]
    assert (REPO_ROOT / "src" / "reposcan" / "py.typed").is_file()


def test_bundled_data_files_are_inside_the_package() -> None:
    from reposcan.config import data_path

    for name in ("gitleaks.toml", "semgrep-rules.yml"):
        assert data_path(name).is_file()
