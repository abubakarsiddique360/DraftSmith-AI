"""Outline generation.

Each format is a fixed section template with a share of the word budget, so two
writers get the same skeleton and can argue about content instead of structure.
"""

from __future__ import annotations

from dataclasses import dataclass

from draftsmith.brief import Brief

TEMPLATES: dict[str, tuple[tuple[str, float, str], ...]] = {
    "tutorial": (
        ("Why this matters", 0.10, "state the problem and who it affects"),
        ("Prerequisites and setup", 0.15, "list tools, versions and minimum knowledge"),
        ("Step-by-step build", 0.35, "the main walkthrough, one idea per subsection"),
        ("Verify and test", 0.15, "show how the reader proves it works"),
        ("Common pitfalls", 0.13, "name the mistakes you actually hit"),
        ("Where to go next", 0.12, "one extension and one reference"),
    ),
    "explainer": (
        ("The problem", 0.15, "describe the failure mode in concrete terms"),
        ("The core idea", 0.25, "explain the mechanism without jargon"),
        ("How it works in practice", 0.25, "walk through one realistic example"),
        ("Trade-offs", 0.20, "what it costs, where it breaks"),
        ("When to use it", 0.15, "decision criteria and alternatives"),
    ),
    "listicle": (
        ("Quick summary", 0.10, "who this list is for and what it covers"),
        ("The list", 0.60, "one H3 per item, each with a concrete detail"),
        ("How to choose", 0.20, "selection criteria, not opinions"),
        ("Further reading", 0.10, "two or three sources worth the time"),
    ),
    "comparison": (
        ("The decision", 0.10, "state exactly which choice the reader faces"),
        ("Options at a glance", 0.20, "a table with the dimensions that matter"),
        ("Deep dive A", 0.25, "strengths, limits, operating cost"),
        ("Deep dive B", 0.25, "strengths, limits, operating cost"),
        ("Recommendation", 0.20, "pick by context, not by preference"),
    ),
}


@dataclass(frozen=True)
class Section:
    heading: str
    words: int
    purpose: str

    def as_dict(self) -> dict:
        return {"heading": self.heading, "words": self.words, "purpose": self.purpose}


def build_outline(brief: Brief) -> list[Section]:
    """Split the brief's word budget across the template for its format."""

    template = TEMPLATES[brief.format]
    raw = [share * brief.target_words for _, share, _ in template]
    words = [int(value) for value in raw]
    remainder = brief.target_words - sum(words)
    # give the rounding remainder to the largest section so the total is exact
    if remainder:
        largest = max(range(len(words)), key=lambda i: words[i])
        words[largest] += remainder
    return [
        Section(heading=heading, words=words[index], purpose=purpose)
        for index, (heading, _, purpose) in enumerate(template)
    ]


def total_words(sections: list[Section]) -> int:
    return sum(section.words for section in sections)
