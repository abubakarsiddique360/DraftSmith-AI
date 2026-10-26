from __future__ import annotations

from draftsmith.editorial import ERROR, WARNING, analyze, strip_frontmatter

GOOD = """---
title: Hybrid Retrieval for Busy Backend Teams
---

# Hybrid Retrieval for Busy Backend Teams

Hybrid retrieval blends keyword search with vectors. It is simple to run.

## Why keyword search is not enough

Keyword search misses synonyms. Users type words that never appear in the document.

## How vectors help

Vectors capture meaning. A vector search finds paraphrases that keywords miss.

## How to combine both

Blend the scores after normalising them. Tune one weight instead of two thresholds.

## What to measure

Track recall at ten results. Compare against the keyword baseline every release.
"""


def test_clean_article_passes() -> None:
    report = analyze(GOOD, keyword="hybrid retrieval")
    assert report.passed, report.as_dict()
    assert report.score >= 85


def test_metrics_are_reported() -> None:
    metrics = analyze(GOOD).metrics
    assert metrics["words"] > 40
    assert metrics["h1_count"] == 1
    assert metrics["h2_count"] == 4
    assert "flesch_reading_ease" in metrics


def test_missing_keyword_in_title_is_an_error() -> None:
    report = analyze(GOOD, keyword="semantic caching")
    rules = {issue.rule for issue in report.errors}
    assert "keyword-title" in rules
    assert "keyword-intro" in rules
    assert "keyword-absent" in rules


def test_banned_phrase_is_flagged() -> None:
    text = GOOD.replace("It is simple to run.", "In today's fast-paced world, it is simple to run.")
    report = analyze(text)
    assert any(issue.rule == "banned-phrase" for issue in report.issues)


def test_long_paragraph_is_flagged() -> None:
    filler = " ".join(["word"] * 130)
    text = GOOD.replace("Vectors capture meaning.", f"{filler}.")
    report = analyze(text)
    assert any(issue.rule == "paragraph-length" for issue in report.issues)


def test_duplicate_heading_is_flagged() -> None:
    text = GOOD.replace("## What to measure", "## How vectors help")
    report = analyze(text)
    assert any(issue.rule == "duplicate-heading" for issue in report.issues)


def test_multiple_h1_is_an_error() -> None:
    text = GOOD.replace("## How vectors help", "# Another top-level heading")
    report = analyze(text)
    assert any(issue.rule == "single-h1" and issue.severity == ERROR for issue in report.issues)


def test_score_drops_with_issues() -> None:
    clean = analyze(GOOD)
    messy = analyze(GOOD + "\n\n**Game-changer.**\n")
    assert messy.score < clean.score


def test_severity_levels_present() -> None:
    report = analyze("# Only a title\n\nShort body.", keyword="missing keyword")
    severities = {issue.severity for issue in report.issues}
    assert ERROR in severities
    assert WARNING in severities


def test_strip_frontmatter_without_block() -> None:
    meta, body = strip_frontmatter("# Title\n\nBody")
    assert meta == {}
    assert body.startswith("# Title")
