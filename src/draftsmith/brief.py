"""Brief parsing and validation.

A brief is a small TOML file — no YAML dependency, no schema server::

    title = "Hybrid Retrieval, Explained"
    audience = "backend engineers"
    tone = "practical"
    target_words = 1200
    primary_keyword = "hybrid retrieval"
    format = "tutorial"
    tags = ["rag", "search"]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import tomllib

FORMATS = ("tutorial", "explainer", "listicle", "comparison")
MIN_WORDS = 200
MAX_WORDS = 5000


class BriefError(ValueError):
    """Raised when a brief file is missing required or usable values."""


@dataclass(frozen=True)
class Brief:
    title: str
    primary_keyword: str
    audience: str = "software engineers"
    tone: str = "practical"
    target_words: int = 1200
    format: str = "tutorial"
    tags: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Brief:
        title = str(data.get("title", "")).strip()
        keyword = str(data.get("primary_keyword", "")).strip()
        if not title:
            raise BriefError("brief needs a non-empty 'title'")
        if not keyword:
            raise BriefError("brief needs a non-empty 'primary_keyword'")

        try:
            target = int(data.get("target_words", 1200))
        except (TypeError, ValueError) as exc:
            raise BriefError("'target_words' must be a number") from exc
        if not MIN_WORDS <= target <= MAX_WORDS:
            raise BriefError(f"'target_words' must be between {MIN_WORDS} and {MAX_WORDS}")

        fmt = str(data.get("format", "tutorial")).lower()
        if fmt not in FORMATS:
            raise BriefError(f"'format' must be one of {', '.join(FORMATS)}")

        tags = data.get("tags", [])
        if not isinstance(tags, list):
            raise BriefError("'tags' must be a list of strings")

        return cls(
            title=title,
            primary_keyword=keyword,
            audience=str(data.get("audience", "software engineers")).strip(),
            tone=str(data.get("tone", "practical")).strip(),
            target_words=target,
            format=fmt,
            tags=tuple(str(tag).strip() for tag in tags if str(tag).strip()),
            description=str(data.get("description", "")).strip(),
        )

    @classmethod
    def from_toml(cls, path: Path | str) -> Brief:
        source = Path(path)
        try:
            data = tomllib.loads(source.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise BriefError(f"brief not found: {source}") from exc
        except tomllib.TOMLDecodeError as exc:
            raise BriefError(f"{source.name} is not valid TOML: {exc}") from exc
        return cls.from_dict(data)

    def summary(self) -> str:
        return (
            f"{self.title} · {self.format} · {self.target_words} words · "
            f"keyword: {self.primary_keyword}"
        )
