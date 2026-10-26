"""Draft skeleton rendering.

The output is deliberately a *scaffold*: headings, word budgets and prompts that
a writer (human or model) fills in. Nothing is generated as finished prose, so
the draft cannot quietly invent facts.
"""

from __future__ import annotations

from datetime import date

from draftsmith.brief import Brief
from draftsmith.outline import Section


def _frontmatter(brief: Brief) -> str:
    tags = ", ".join(brief.tags) if brief.tags else "writing"
    description = (
        brief.description or f"A {brief.tone} {brief.format} about {brief.primary_keyword}."
    )
    return "\n".join(
        [
            "---",
            f"title: {brief.title}",
            f"description: {description}",
            f"date: {date.today().isoformat()}",
            f"tags: [{tags}]",
            f"primary_keyword: {brief.primary_keyword}",
            f"audience: {brief.audience}",
            f"target_words: {brief.target_words}",
            "status: draft",
            "---",
        ]
    )


def render_draft(brief: Brief, sections: list[Section]) -> str:
    parts: list[str] = [_frontmatter(brief), "", f"# {brief.title}", ""]
    parts.append(
        f"> Audience: {brief.audience}. Tone: {brief.tone}. "
        f"Every section has a word budget; keep the whole piece near "
        f"{brief.target_words} words."
    )
    parts.append("")
    parts.append(
        f"**Opening (about 80 words).** Name the problem in one sentence, promise the "
        f'outcome in one sentence, and use the phrase "{brief.primary_keyword}" naturally '
        f"in the first paragraph."
    )
    parts.append("")

    for index, section in enumerate(sections, start=1):
        parts.append(f"## {index}. {section.heading}")
        parts.append("")
        parts.append(f"_Budget: ~{section.words} words · Purpose: {section.purpose}._")
        parts.append("")
        parts.append("- Key point one — the claim, in a full sentence.")
        parts.append("- Key point two — the concrete example or measurement.")
        parts.append("- Key point three — the caveat the reader needs.")
        parts.append("")
        parts.append("> Evidence needed: link, benchmark, or code snippet that proves the claim.")
        parts.append("")

    parts.append("## Editorial checklist")
    parts.append("")
    parts.append(
        f'- [ ] Primary keyword "{brief.primary_keyword}" appears in title, opening and one H2.'
    )
    parts.append("- [ ] Every claim has a source or a reproduction step.")
    parts.append("- [ ] No paragraph longer than 120 words.")
    parts.append("- [ ] Headings read as takeaways, not labels.")
    parts.append("")
    return "\n".join(parts)
