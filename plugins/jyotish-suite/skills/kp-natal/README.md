# KP Natal Skill — Install

This skill is part of the **jyotish-suite** plugin. Deterministic computation is
shared across all six skills — there is no per-skill `scripts/` directory.

## Layout
```
plugins/jyotish-suite/
├── lib/                       # shared: jyotish_primitives.py, ephemeris.py
├── scripts/
│   └── compute_kp_natal_baseline.py   # cusps, CSL, significators, RP, Sookshma
├── agents/                    # chart-calculator, baseline-runner, chart-verifier,
│                              # unit-analyzer, synthesizer
└── skills/kp-natal/
    ├── SKILL.md               # wave orchestrator
    └── references/
        ├── methodology.md
        ├── house-combinations.md
        ├── ruling-planets.md
        ├── significators-rules.md
        └── orchestration-notes.md
```

## Dependencies
- `pyswisseph` (Swiss Ephemeris — Ruling Planets, Sookshma, chart computation)
- `pytz`

Install once: `pip install pyswisseph pytz --break-system-packages`

## How to invoke
Type `/kp-natal` and either upload/paste your KP natal chart, or give birth
data (date, time, place) for the chart to be computed.

The skill runs as a wave orchestrator:
1. **Intake** — chart or birth data; mode (life reading vs event timing).
2. **Wave 0** — compute/verify the chart, then `compute_kp_natal_baseline.py`
   produces all deterministic data (12 cusps + CSL, 4-level significators,
   Ruling Planets, Sookshma dasha) in one pass.
3. **Wave 1** — parallel per-cusp analysis (12 workers in life-reading mode).
4. **Wave 2** — synthesis into the final reading.

## Validation
Sookshma computation was cross-validated against AstroSage MD-AD dates —
Mercury MD start 1 Dec 2024, Mercury-Mercury bhukti end 28 Apr 2027.
