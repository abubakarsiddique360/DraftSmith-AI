# DraftSmith AI

**Brief in, structured draft out — then a deterministic editorial review.**

DraftSmith turns a short TOML brief into a sectioned markdown draft with word
budgets and evidence prompts, then lints any article for structure, readability
and keyword hygiene. It runs offline, has **zero dependencies**, and never
invents prose: the generator produces a scaffold, and every check is explainable.

[![CI](https://github.com/abubakarsiddique360/DraftSmith-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/abubakarsiddique360/DraftSmith-AI/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](pyproject.toml)

## Why

Most "AI blog writer" demos jump straight to generated paragraphs. That makes two
problems invisible: the structure is whatever the model felt like, and review
happens by vibes. DraftSmith separates them:

1. **Structure is derived from the brief** — format → fixed section template →
   exact word budget.
2. **Review is rule-based** — the same draft always gets the same score.

Use the scaffold yourself, or hand it to any model as a strict outline. The linter
still works on whatever comes back.

## Install

Requires Python 3.11 or newer ? briefs are parsed with the standard library `tomllib`.

```bash
git clone https://github.com/abubakarsiddique360/DraftSmith-AI.git
cd DraftSmith-AI
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
draftsmith build examples/briefs/hybrid-retrieval.toml -o draft.md
draftsmith lint draft.md --keyword "hybrid retrieval"
draftsmith score draft.md --keyword "hybrid retrieval"
```

`build` prints the scaffold to stdout (or writes `-o`). `lint` exits `1` when an
error-level rule fails, so it drops straight into CI. `score` prints JSON metrics.

## The brief

```toml
title = "Hybrid Retrieval, Explained"
description = "When keyword search stops being enough."
primary_keyword = "hybrid retrieval"
audience = "backend engineers who already ship search"
tone = "practical"
target_words = 1400          # 200 - 5000
format = "tutorial"          # tutorial | explainer | listicle | comparison
tags = ["retrieval", "search", "rag"]
```

Required: `title`, `primary_keyword`. Everything else has a default.

## What `build` produces

- YAML frontmatter (`title`, `description`, `date`, `tags`, `status: draft`)
- One `#` title, then `##` sections from the format template
- Per-section word budget and purpose, three prompt bullets, and an
  `> Evidence needed:` line
- An editorial checklist at the end

Word budgets always add up to `target_words` exactly — the rounding remainder goes
to the largest section.

## What `lint` checks

| Rule | Severity | Meaning |
| --- | --- | --- |
| `single-h1` | error | exactly one `#` heading |
| `h2-count` | warning | at least three `##` sections |
| `title-length` | warning | 30–65 characters |
| `keyword-title` / `keyword-intro` / `keyword-absent` | error | primary keyword placement |
| `keyword-density` | warning | 0.4–2.5 % of words |
| `sentence-length` | warning | average ≤ 25 words |
| `readability` | warning | Flesch Reading Ease ≥ 50 |
| `paragraph-length` | warning | no paragraph over 120 words |
| `duplicate-heading` | warning | repeated `##` text |
| `banned-phrase` | warning | a small list of clichés |

Score = `100 − 15×errors − 5×warnings`. Metrics include word/sentence counts,
average sentence length, Flesch score, heading counts, keyword count and density.
Code fences are excluded from the prose metrics.

## Project layout

```text
src/draftsmith/
├── brief.py       TOML brief parsing + validation
├── outline.py     format templates, word-budget allocation
├── draft.py       markdown scaffold rendering
├── editorial.py   metrics + rule checks
└── cli.py         build · lint · score
tests/             30 pytest cases
examples/briefs/   a ready-to-run brief
```

## Design notes

- **No prose generation.** A scaffold cannot fabricate a statistic, and a reviewer
  knows exactly which sentence they wrote.
- **Deterministic scoring.** Same input, same score — usable as a CI gate.
- **Flesch, not "AI readability".** A 1948 formula is boring, documented, and easy
  to verify by hand.
- **No YAML parser.** Briefs are TOML, parsed with the standard library.

## Roadmap

- [ ] `draftsmith compare draft.md brief.toml` to diff budgets against reality
- [ ] Reading-level targets (grade 8 / grade 12) as first-class config
- [ ] Optional outline export to JSON for downstream tools

## License

[MIT](LICENSE) © 2026 **ABU BAKAR SIDDIQUE**
