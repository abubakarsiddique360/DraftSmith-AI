"""Editorial checks: structure, readability and keyword hygiene.

Everything here is deterministic and explainable — a writer can see exactly which
rule failed and why. No model is involved.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

ERROR = "error"
WARNING = "warning"
INFO = "info"

SEVERITY_PENALTY = {ERROR: 15, WARNING: 5, INFO: 1}

BANNED_PHRASES = (
    "in today's fast-paced world",
    "in the ever-evolving landscape",
    "delve into",
    "game-changer",
    "unlock the power",
    "revolutionize",
    "seamlessly integrate",
    "at the end of the day",
)

_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
_SENTENCE_RE = re.compile(r"[.!?]+(?:\s|$)")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")
_FENCE_RE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)


@dataclass(frozen=True)
class Issue:
    rule: str
    severity: str
    message: str


@dataclass
class Report:
    metrics: dict[str, float] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)

    @property
    def score(self) -> int:
        penalty = sum(SEVERITY_PENALTY.get(issue.severity, 0) for issue in self.issues)
        return max(0, 100 - penalty)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == ERROR]

    @property
    def passed(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict:
        return {
            "score": self.score,
            "passed": self.passed,
            "metrics": self.metrics,
            "issues": [issue.__dict__ for issue in self.issues],
        }


def strip_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    """Split an optional ``---`` block from the body."""

    if not markdown.lstrip().startswith("---"):
        return {}, markdown
    parts = markdown.split("---", 2)
    if len(parts) < 3:
        return {}, markdown
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        key, _, value = line.partition(":")
        if key.strip():
            meta[key.strip().lower()] = value.strip()
    return meta, parts[2].strip()


def count_syllables(word: str) -> int:
    groups = _VOWEL_GROUP_RE.findall(word.lower())
    count = len(groups)
    if word.lower().endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def flesch_reading_ease(words: list[str], sentences: int) -> float:
    if not words or not sentences:
        return 0.0
    syllables = sum(count_syllables(word) for word in words)
    return round(206.835 - 1.015 * (len(words) / sentences) - 84.6 * (syllables / len(words)), 1)


def analyze(markdown: str, keyword: str | None = None) -> Report:
    meta, body = strip_frontmatter(markdown)
    prose = _FENCE_RE.sub(" ", body)
    words = _WORD_RE.findall(prose)
    sentences = max(1, len(_SENTENCE_RE.findall(prose)))
    lower = prose.lower()

    headings = re.findall(r"^(#{1,6})\s+(.*)$", body, flags=re.MULTILINE)
    h1 = [text for level, text in headings if level == "#"]
    h2 = [text for level, text in headings if level == "##"]
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", prose) if p.strip()]
    long_paragraphs = [p for p in paragraphs if len(_WORD_RE.findall(p)) > 120]

    metrics: dict[str, float] = {
        "words": len(words),
        "sentences": sentences,
        "avg_sentence_words": round(len(words) / sentences, 1),
        "flesch_reading_ease": flesch_reading_ease(words, sentences),
        "h1_count": len(h1),
        "h2_count": len(h2),
        "paragraphs": len(paragraphs),
    }

    issues: list[Issue] = []
    title = h1[0] if h1 else meta.get("title", "")
    intro = paragraphs[0].lower() if paragraphs else ""

    if len(h1) != 1:
        issues.append(Issue("single-h1", ERROR, f"expected exactly one H1, found {len(h1)}"))
    if len(h2) < 3:
        issues.append(Issue("h2-count", WARNING, f"only {len(h2)} H2 sections; aim for at least 3"))
    if title and not 30 <= len(title) <= 65:
        issues.append(
            Issue("title-length", WARNING, f"title is {len(title)} characters; 30-65 ranks better")
        )
    if metrics["avg_sentence_words"] > 25:
        issues.append(
            Issue(
                "sentence-length",
                WARNING,
                f"average sentence is {metrics['avg_sentence_words']} words",
            )
        )
    if metrics["flesch_reading_ease"] < 50:
        issues.append(
            Issue(
                "readability",
                WARNING,
                f"Flesch score {metrics['flesch_reading_ease']} is hard to read",
            )
        )
    for paragraph in long_paragraphs:
        count = len(_WORD_RE.findall(paragraph))
        issues.append(Issue("paragraph-length", WARNING, f"paragraph with {count} words; split it"))
    duplicates = {text for text in h2 if h2.count(text) > 1}
    for heading in sorted(duplicates):
        issues.append(Issue("duplicate-heading", WARNING, f"duplicate heading: {heading}"))

    for phrase in BANNED_PHRASES:
        if phrase in lower:
            issues.append(Issue("banned-phrase", WARNING, f'cliche found: "{phrase}"'))

    if keyword:
        needle = keyword.lower()
        occurrences = lower.count(needle)
        density = round(100 * occurrences * len(needle.split()) / max(1, len(words)), 2)
        metrics["keyword_count"] = float(occurrences)
        metrics["keyword_density"] = density
        if needle not in title.lower():
            issues.append(
                Issue("keyword-title", ERROR, f"primary keyword missing from the title: {keyword}")
            )
        if needle not in intro:
            issues.append(
                Issue(
                    "keyword-intro",
                    ERROR,
                    f"primary keyword missing from the opening paragraph: {keyword}",
                )
            )
        if occurrences and not 0.4 <= density <= 2.5:
            issues.append(
                Issue("keyword-density", WARNING, f"keyword density {density}% is outside 0.4-2.5%")
            )
        if occurrences == 0:
            issues.append(
                Issue("keyword-absent", ERROR, f"primary keyword never appears: {keyword}")
            )

    return Report(metrics=metrics, issues=issues)
