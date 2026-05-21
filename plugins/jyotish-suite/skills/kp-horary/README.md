# KP Horary Skill — Install

This skill is part of the **jyotish-suite** plugin. Deterministic computation is
shared across all six skills — there is no per-skill `scripts/` directory.

## Layout
```
plugins/jyotish-suite/
├── lib/                        # shared: jyotish_primitives.py, ephemeris.py
├── scripts/
│   └── compute_kp_horary_baseline.py   # horary chart, cusps, CSL, RP, significators
├── agents/                     # chart-calculator, baseline-runner, chart-verifier,
│                               # unit-analyzer, synthesizer
└── skills/kp-horary/
    ├── SKILL.md                # wave orchestrator
    └── references/
        ├── methodology.md
        ├── house-combinations.md
        ├── 249-table.md
        ├── ruling-planets.md
        └── orchestration-notes.md
```

## Dependencies
- `pyswisseph` (Swiss Ephemeris)
- `pytz`

Install once: `pip install pyswisseph pytz --break-system-packages`

## How to invoke
Type `/kp-horary` and provide:
1. Your question (specific, time-bound, single-issue)
2. A horary number (1-249)
3. The location of the questioner
4. The time the question is taken

`compute_kp_horary_baseline.py` builds the entire horary chart from the 1-249
number, plus the Ruling Planets (from the real rising sign at question time —
kept separate from the number-derived chart Lagna), cusps, CSL and
significators, in one deterministic pass.

## Validation
Chart computation was validated against AstroSage output for a reference
nativity (30 July 1991, 10:20 IST, Phagwara) — all 9 planet sign/star/sub/
sub-sub lord chains match, degree precision within 1-2 arc-minutes.
