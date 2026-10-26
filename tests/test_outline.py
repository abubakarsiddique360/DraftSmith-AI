from __future__ import annotations

import pytest

from draftsmith.brief import Brief
from draftsmith.draft import render_draft
from draftsmith.editorial import count_syllables, flesch_reading_ease, strip_frontmatter
from draftsmith.outline import TEMPLATES, build_outline, total_words


@pytest.fixture()
def brief() -> Brief:
    return Brief.from_dict(
        {
            "title": "Hybrid Retrieval for Busy Backend Teams",
            "primary_keyword": "hybrid retrieval",
            "format": "tutorial",
            "target_words": 1000,
        }
    )


def test_outline_uses_format_template(brief: Brief) -> None:
    sections = build_outline(brief)
    assert len(sections) == len(TEMPLATES["tutorial"])
    assert sections[0].heading == "Why this matters"
    assert all(section.purpose for section in sections)


def test_outline_word_budget_is_exact(brief: Brief) -> None:
    assert total_words(build_outline(brief)) == brief.target_words


@pytest.mark.parametrize("fmt", ["tutorial", "explainer", "listicle", "comparison"])
def test_outline_budget_exact_for_every_format(fmt: str) -> None:
    brief = Brief.from_dict(
        {
            "title": "A perfectly normal title for testing purposes",
            "primary_keyword": "testing",
            "format": fmt,
            "target_words": 733,
        }
    )
    assert total_words(build_outline(brief)) == 733


def test_draft_contains_frontmatter_and_headings(brief: Brief) -> None:
    draft = render_draft(brief, build_outline(brief))
    assert draft.startswith("---")
    assert "# Hybrid Retrieval for Busy Backend Teams" in draft
    assert "## 1. Why this matters" in draft
    assert "hybrid retrieval" in draft
    meta, body = strip_frontmatter(draft)
    assert meta["primary_keyword"] == "hybrid retrieval"
    assert body


def test_count_syllables() -> None:
    assert count_syllables("cat") == 1
    assert count_syllables("banana") == 3
    assert count_syllables("code") == 1


def test_flesch_on_simple_sentence() -> None:
    words = ["the", "cat", "sat", "on", "the", "mat"]
    assert flesch_reading_ease(words, 1) > 100
