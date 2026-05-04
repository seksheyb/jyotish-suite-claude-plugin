# KP Natal Skill — Install

## Place at:
```
/mnt/skills/user/kp-natal/
├── SKILL.md
├── references/
│   ├── methodology.md
│   ├── house-combinations.md
│   ├── ruling-planets.md
│   └── significators-rules.md
└── scripts/
    ├── compute_ruling_planets.py
    └── compute_sookshma.py
```

## Dependencies
- `pyswisseph` (for Ruling Planets script — Moon/Lagna at moment of reading)
- `pytz`

## How to invoke
Type `/kp-natal` and either:
- Upload your KP natal chart as a markdown file (e.g. `sekshey-kp-natal.md`)
- Or paste the chart contents

The skill will:
1. Echo back the chart for verification
2. Ask: life reading or event timing?
3. If event timing — ask which area + horizon
4. Compute current Ruling Planets at moment of reading + your location (default New Delhi)
5. Compute Sookshma dasha if needed for timing
6. Deliver the reading

## Companion data file
`sekshey-kp-natal.md` is provided separately — the parsed natal chart from AstroSage Vedic Report PDF. This is the chart input you paste/upload when running `/kp-natal`.

## Validation
Sookshma computation was cross-validated against AstroSage's MD-AD dates for Sekshey's chart — Mercury MD start 1 Dec 2024 ✓, Mercury-Mercury bhukti end 28 Apr 2027 ✓.
