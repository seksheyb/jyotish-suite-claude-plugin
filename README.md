# Sekshey's Jyotish Suite — Claude Code Marketplace

A curated marketplace distributing **Jyotish Suite**: a six-system Vedic astrology toolkit for Claude Code.

## What's inside

One plugin — `jyotish-suite` — bundling six rigorous astrology systems, each as a skill with its own slash command:

| Slash command       | System                              | Use it for                                                                 |
| ------------------- | ----------------------------------- | -------------------------------------------------------------------------- |
| `/vedic-astro`      | Classical Vedic (Parashari)         | Multi-layered chart reading: Nakshatras, Padas, aspects, Vimshottari Dasha |
| `/bnn`              | BNN (Brighu Nadi Nadi)              | Natural Karaka + Nadi flow analysis with degree-based timing               |
| `/jaimini`          | Jaimini                             | Chara Karakas, Arudha Padas, Swamsha, Argala, Chara Dasha                  |
| `/lal-kitab`        | Lal Kitab                           | Rin diagnosis, pakka ghar, varshphal, upaay (Farmans 1939–1952)            |
| `/kp-natal`         | Krishnamurti Paddhati — Natal       | Life reading + event timing via Sookshma dasha + Ruling Planets            |
| `/kp-horary`        | Krishnamurti Paddhati — Horary      | Yes/no/timing answers from a 1–249 number + moment + place                 |

Each skill is also auto-triggered by its skill description, so you can use either the slash command or natural language.

## Architecture

Every skill is a **wave orchestrator**, not a monolithic prompt. A reading runs in stages:

1. **Compute** — a chart is built from birth data (via the shared `lib/ephemeris.py`, sidereal, school-appropriate ayanamsa) or parsed from a chart you paste (`lib/chart_io.py`), then verified back to you.
2. **Baseline** — one deterministic Python script per school (`scripts/compute_<school>_baseline.py`) computes every fact that is arithmetic or table lookup: nakshatras, dashas, degree flags, dignities, significators, aspect maps, Karakas, rin/teva triggers, timing signals. Nothing astrological is left to the model to calculate.
3. **Interpret** — parallel `unit-analyzer` subagents read those facts and interpret one unit each (a house, Karaka, cusp, family member, year, or dasha window), scaled to the question.
4. **Synthesize** — a single `synthesizer` subagent weaves the layers into the final reading, resolving contradictions and stating confidence.

The split means the model interprets facts it never has to compute — so the numbers are exact and reproducible. A golden-chart regression harness (`tests/run_golden.py`) snapshot-tests all six baselines on pinned charts, across both the birth-data and pasted-chart paths.

## Install

```bash
# In Claude Code
/plugin marketplace add seksheyb/jyotish-suite-claude-plugin
/plugin install jyotish-suite@sekshey-jyotish
```

To test locally before publishing:

```bash
/plugin marketplace add /path/to/jyotish-suite-claude-plugin
/plugin install jyotish-suite@sekshey-jyotish
```

## Requirements

The compute layer uses [`pyswisseph`](https://pypi.org/project/pyswisseph/) and `pytz` for ephemeris math. These are needed whenever a chart is **computed from birth data** (all six systems support this), and always for the two KP systems:

```bash
pip install pyswisseph pytz
```

If you only ever paste **pre-computed** charts into the four non-KP systems (`/vedic-astro`, `/bnn`, `/jaimini`, `/lal-kitab`), the chart-parsing path (`lib/chart_io.py` + `lib/jyotish_primitives.py`) is dependency-free — but installing the two packages above unlocks birth-data intake everywhere and is recommended.

If you hit `ModuleNotFoundError: No module named 'swisseph'`, that is the cause — install the packages and retry.

## Update

```bash
/plugin marketplace update sekshey-jyotish
```

## Uninstall

```bash
/plugin uninstall jyotish-suite@sekshey-jyotish
/plugin marketplace remove sekshey-jyotish
```

## Repository structure

```
.
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog
├── plugins/
│   └── jyotish-suite/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest
│       ├── skills/               # Six wave-orchestrator SKILL.md files + references
│       ├── commands/             # Six slash-command definitions
│       ├── agents/               # Shared subagents: chart-calculator, chart-verifier,
│       │                         #   baseline-runner, unit-analyzer, synthesizer
│       ├── scripts/              # Per-school baseline scripts + delta scripts
│       │                         #   (transits, fruitful-window, upaay-check)
│       ├── lib/                  # Shared compute layer: jyotish_primitives,
│       │                         #   ephemeris, chart_io
│       └── tests/                # Golden-chart regression harness + per-school tests
└── README.md                     # This file
```

## License

MIT
