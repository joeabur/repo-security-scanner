"""Static checks on the bundled Semgrep rules (no Semgrep needed) and their test fixtures."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from ..helpers import REPO_ROOT

RULES_FILE = REPO_ROOT / "src" / "reposcan" / "data" / "semgrep-rules.yml"
TEST_DIR = REPO_ROOT / "tests" / "semgrep"
RULES = yaml.safe_load(RULES_FILE.read_text(encoding="utf-8"))["rules"]
TEST_TEXT = "\n".join(p.read_text(encoding="utf-8") for p in sorted(TEST_DIR.glob("semgrep-rules.*")))
ALLOWED_LANGUAGES = {"python", "javascript", "typescript", "go", "java"}


def test_there_are_rules_for_each_supported_language() -> None:
    languages = {lang for rule in RULES for lang in rule["languages"]}
    assert languages == ALLOWED_LANGUAGES
    assert len(RULES) >= 25


def test_rule_ids_are_unique_and_namespaced() -> None:
    ids = [rule["id"] for rule in RULES]
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"reposcan\.(python|js|go|java)\.[a-z0-9\-]+", i) for i in ids), ids


@pytest.mark.parametrize("rule", RULES, ids=[r["id"] for r in RULES])
def test_every_rule_has_metadata_and_both_kinds_of_test_case(rule: dict) -> None:
    assert rule["severity"] in {"ERROR", "WARNING", "INFO"}
    assert set(rule["languages"]) <= ALLOWED_LANGUAGES
    assert rule["message"].strip() and rule["metadata"]["category"] == "security"
    assert re.match(r"CWE-\d+", rule["metadata"]["cwe"][0]), rule["metadata"]
    positives = re.findall(rf"(?:#|//)\s*ruleid:\s*{re.escape(rule['id'])}\b", TEST_TEXT)
    negatives = re.findall(rf"(?:#|//)\s*ok:\s*{re.escape(rule['id'])}\b", TEST_TEXT)
    assert positives, f"{rule['id']} has no `ruleid:` (must-match) test case"
    assert negatives, f"{rule['id']} has no `ok:` (must-not-match) test case"


def test_test_annotations_only_reference_existing_rules() -> None:
    known = {rule["id"] for rule in RULES}
    referenced = set(re.findall(r"(?:#|//)\s*(?:ruleid|ok):\s*(reposcan\.[\w.\-]+)", TEST_TEXT))
    assert referenced <= known, referenced - known


def test_no_remote_or_telemetry_references_in_the_rules() -> None:
    body = RULES_FILE.read_text(encoding="utf-8").split("\nrules:", 1)[1]  # the header comment may mention it
    assert "semgrep.dev" not in body and not re.search(r"https?://", body)


def test_rules_reference_page_is_current() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "generate_rules_doc", REPO_ROOT / "scripts" / "generate_rules_doc.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert (REPO_ROOT / "docs" / "semgrep-rules.md").read_text(encoding="utf-8") == module.render(), (
        "run: python scripts/generate_rules_doc.py"
    )


def test_fixture_directory_contains_only_the_four_language_files(tmp_path: Path) -> None:
    assert {p.name for p in TEST_DIR.iterdir()} == {f"semgrep-rules.{e}" for e in ("py", "js", "go", "java")}
