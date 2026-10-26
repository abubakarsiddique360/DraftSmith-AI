from __future__ import annotations

import pytest

from draftsmith.brief import Brief, BriefError

VALID = {
    "title": "Hybrid Retrieval for Busy Backend Teams",
    "primary_keyword": "hybrid retrieval",
    "format": "tutorial",
    "target_words": 900,
}


def test_from_dict_applies_defaults() -> None:
    brief = Brief.from_dict(VALID)
    assert brief.audience == "software engineers"
    assert brief.tone == "practical"
    assert brief.tags == ()
    assert brief.format == "tutorial"


def test_from_dict_rejects_missing_title() -> None:
    with pytest.raises(BriefError, match="title"):
        Brief.from_dict({**VALID, "title": "  "})


def test_from_dict_rejects_missing_keyword() -> None:
    with pytest.raises(BriefError, match="primary_keyword"):
        Brief.from_dict({**VALID, "primary_keyword": ""})


def test_from_dict_rejects_unknown_format() -> None:
    with pytest.raises(BriefError, match="format"):
        Brief.from_dict({**VALID, "format": "podcast"})


@pytest.mark.parametrize("words", [10, 9000])
def test_target_words_bounds(words: int) -> None:
    with pytest.raises(BriefError, match="between"):
        Brief.from_dict({**VALID, "target_words": words})


def test_tags_must_be_list() -> None:
    with pytest.raises(BriefError, match="tags"):
        Brief.from_dict({**VALID, "tags": "rag"})


def test_from_toml_file(tmp_path) -> None:
    path = tmp_path / "brief.toml"
    path.write_text(
        "\n".join(
            [
                'title = "Hybrid Retrieval for Busy Backend Teams"',
                'primary_keyword = "hybrid retrieval"',
                'tags = ["rag", "search"]',
                "target_words = 1500",
            ]
        ),
        encoding="utf-8",
    )
    brief = Brief.from_toml(path)
    assert brief.tags == ("rag", "search")
    assert "hybrid retrieval" in brief.summary()


def test_from_toml_reports_invalid_file(tmp_path) -> None:
    path = tmp_path / "broken.toml"
    path.write_text("title = ", encoding="utf-8")
    with pytest.raises(BriefError, match="valid TOML"):
        Brief.from_toml(path)
