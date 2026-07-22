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
3. **Wave 1** — analysis. Life reading: 4 trine-group workers (1/5/9, 2/6/10,
   3/7/11, 4/8/12). Event timing: `baseline-runner` first executes
   `find_fruitful_window.py` and `compute_transits.py` (workers can't run
   scripts), then one dense worker runs the full 8-step interpretive chain
   over their outputs (no fan-out — it's a sequential dependency chain).
   Narrow single-house timing questions skip Wave 1 entirely (inline, zero
   workers).
4. **Wave 2** — synthesis (sonnet, effort high) into the final reading.

## Validation
Sookshma computation was cross-validated against AstroSage MD-AD dates —
Mercury MD start 1 Dec 2024, Mercury-Mercury bhukti end 28 Apr 2027.
