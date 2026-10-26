from __future__ import annotations

import json

from draftsmith.cli import main

BRIEF = """
title = "Hybrid Retrieval for Busy Backend Teams"
primary_keyword = "hybrid retrieval"
format = "comparison"
target_words = 800
tags = ["rag"]
"""

GOOD_POST = """# Hybrid Retrieval for Busy Backend Teams

Hybrid retrieval is a blend of keyword and vector search.

## Option one

Keyword search is cheap and explainable.

## Option two

Vector search handles paraphrases.

## The recommendation

Start with keywords, add vectors when recall stalls.
"""


def test_build_writes_file(tmp_path, capsys) -> None:
    brief = tmp_path / "brief.toml"
    brief.write_text(BRIEF, encoding="utf-8")
    out = tmp_path / "draft.md"
    assert main(["build", str(brief), "-o", str(out)]) == 0
    assert out.exists()
    assert "Hybrid Retrieval" in out.read_text(encoding="utf-8")
    assert "sections" in capsys.readouterr().out


def test_build_rejects_bad_brief(tmp_path, capsys) -> None:
    brief = tmp_path / "brief.toml"
    brief.write_text('title = ""\nprimary_keyword = "x"\n', encoding="utf-8")
    assert main(["build", str(brief)]) == 2
    assert "title" in capsys.readouterr().err


def test_lint_passes(tmp_path, capsys) -> None:
    post = tmp_path / "post.md"
    post.write_text(GOOD_POST, encoding="utf-8")
    assert main(["lint", str(post), "--keyword", "hybrid retrieval"]) == 0
    assert "error(s)" in capsys.readouterr().out


def test_lint_fails_with_missing_keyword(tmp_path, capsys) -> None:
    post = tmp_path / "post.md"
    post.write_text(GOOD_POST, encoding="utf-8")
    assert main(["lint", str(post), "--keyword", "quantum knitting"]) == 1
    captured = capsys.readouterr().out
    assert "keyword-absent" in captured


def test_score_outputs_json(tmp_path, capsys) -> None:
    post = tmp_path / "post.md"
    post.write_text(GOOD_POST, encoding="utf-8")
    assert main(["score", str(post), "--keyword", "hybrid retrieval"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["score"] >= 0
    assert payload["metrics"]["h1_count"] == 1


def test_missing_file_is_reported(tmp_path) -> None:
    assert main(["lint", str(tmp_path / "nope.md")]) == 2
