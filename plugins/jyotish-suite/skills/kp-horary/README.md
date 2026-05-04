# KP Horary Skill — Install

## Place at:
```
/mnt/skills/user/kp-horary/
├── SKILL.md
├── references/
│   ├── methodology.md
│   ├── house-combinations.md
│   ├── 249-table.md
│   └── ruling-planets.md
└── scripts/
    ├── compute_horary_chart.py
    └── compute_ruling_planets.py
```

## Dependencies
The Python scripts require:
- `pyswisseph` (Swiss Ephemeris)
- `pytz`

The skill execution environment must `pip install pyswisseph pytz --break-system-packages` before first use. Add this to bash setup if not already present.

## How to invoke
Type `/kp-horary` and follow the prompts. Provide:
1. Your question
2. Horary number (1-249)
3. Location of the questioner
4. Time of question (defaults to "now")

## Validation
The chart computation logic was validated against AstroSage natal chart output for Sekshey Bakhshi (30 July 1991, 10:20 IST, Phagwara) — all 9 planet sign/star/sub/sub-sub lord chains match 100%, with degree precision within 1-2 arc-minutes.
