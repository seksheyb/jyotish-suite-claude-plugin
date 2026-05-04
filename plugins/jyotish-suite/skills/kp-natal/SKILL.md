---
name: kp-natal
description: >
  Trigger this skill immediately and exclusively when the user types "/kp-natal" anywhere in their
  message. This skill performs Krishnamurti Paddhati (KP) natal astrology — life readings and event-
  timing predictions from a pre-computed natal KP chart. The user provides the chart as a markdown
  file (cuspal positions with sign/star/sub/sub-sub lords, planetary positions with full lord chain,
  significators, dasha sequence). The skill echoes back the parsed chart, asks conversationally
  whether the user wants a life reading or event timing (and which area + horizon if event), computes
  current Ruling Planets with full calculation shown, computes Sookshma dasha (4th level) for the
  relevant window, and delivers a structured KP reading with cuspal sub-lord analysis, significators,
  and timing window. Always use this skill — never attempt KP natal work without it. Also trigger
  when user says "KP reading", "KP chart analysis", "read my KP chart", "when will I get married —
  KP", "KP timing for [event]".
---

# KP Natal Astrology Skill

## Overview
This skill performs full KP natal readings — both life readings and event-timing predictions — from a pre-computed natal chart provided by the user.

1. Accept the natal KP chart as a markdown file or pasted block
2. Echo back the parsed chart for verification
3. Ask conversationally: life reading or event timing? If event, which area + time horizon?
4. Compute current Ruling Planets at moment of reading (show calculation)
5. Compute Sookshma dasha (4th level — skill computes this; chart only provides MD/BD/AD)
6. Apply KP methodology: significators, cuspal sub-lord analysis, RP cross-check, DBA timing
7. Deliver verdict / life reading

**Reference files — load before every reading:**
| File | Load When |
|------|-----------|
| `references/methodology.md` | Always — full KP natal analysis framework |
| `references/house-combinations.md` | When event timing question is asked |
| `references/ruling-planets.md` | When computing and interpreting RP |
| `references/significators-rules.md` | When listing significators |

**Computation scripts:**
| File | Purpose |
|------|---------|
| `scripts/compute_ruling_planets.py` | RP at moment of reading + place |
| `scripts/compute_sookshma.py` | Compute 4th-level Sookshma dasha within current Antara |

---

## PHASE 1 — Chart Collection

When `/kp-natal` is triggered:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KP Natal Reading

Please share your natal KP chart. Either:
  • Upload a markdown file with the chart data
  • Or paste it directly

Required data:
  • Birth details (date, time, place, lat/long)
  • Ayanamsa used (e.g. KP New / Krishnamurti)
  • All 12 cuspal positions with: degree, sign-lord, star-lord, sub-lord, sub-sub-lord
  • All 9 planets (Sun through Ketu) + optionally outer planets:
    longitude, sign, star-lord, sub-lord, sub-sub-lord, retrograde flag
  • Significators of houses (which planets signify each house)
  • Vimshottari dasha sequence (MD-BD-AD with start dates)

If you don't have the significator table, I can derive it from planet positions.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PHASE 2 — Verification Echo

Display the parsed chart back in clean tables:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHART VERIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Native: [name]
Born: [date] at [time] [tz]
Place: [city] ([lat], [lon])
Ayanamsa: [type] = [value]
Lagna: [sign] [degree]
Moon: [sign] [degree] in [nakshatra]

CUSPAL POSITIONS
| Cusp | Degree     | Sign  | Star  | Sub   | SS    |
|------|------------|-------|-------|-------|-------|
|  1   | ddd-mm-ss  | XXX   | XXX   | XXX   | XXX   |
| ...  |            |       |       |       |       |

PLANETARY POSITIONS
| Planet  | Degree     | Sign  | Star  | Sub   | SS    | Retro |
|---------|------------|-------|-------|-------|-------|-------|
| Sun     | ...                                                   |
| ...     |                                                       |

SIGNIFICATORS OF HOUSES
| House | Planets                          |
|-------|----------------------------------|
|   1   | XX, XX                           |
| ...   |                                  |

CURRENT DASHA (as per chart):
[MD] Mahadasha — running [start] to [end]
  [BD] Bhukti — running [start] to [end]
    [AD] Antara — running [start] to [end]

Confirm this matches your records before I proceed?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

After confirmation, proceed to Phase 3.

---

## PHASE 3 — Mode Selection (Conversational)

```
What kind of reading?

  A. Life reading — comprehensive analysis of all 12 houses,
     declaring which life areas will fructify and which won't
     (uses cuspal sub-lords across all houses)

  B. Event timing — specific question about WHEN something
     will happen (e.g. marriage, job change, child, property,
     health recovery). Tell me:
        • What event?
        • Time horizon (next 1 year / 3 years / open-ended)?
```

Wait for user's choice.

---

## PHASE 4A — Life Reading Mode

Walk through all 12 cuspal sub-lords. For each:

```
HOUSE [N] — [significance]
  Cuspal Sub Lord: [planet]
    • In star of: [planet] → which signifies houses [...]
    • Itself: occupies [house], owns [houses]
    • Total signification: houses [...]
    • Retrograde: [yes/no, with implication]

  Verdict for matters of house [N]:
    [Will fructify / Partial / Will not fructify]
    Reasoning: [explanation tied to positive/negative house combo]
```

After all 12 cusps, deliver a synthesis:

```
LIFE THEMES — KP SYNTHESIS

Strong areas (CSL connected to positive combinations):
  • [House X — life theme] — [why]

Weak / blocked areas (CSL connected to negative set):
  • [House Y — life theme] — [why]

Mixed / conditional:
  • [House Z] — [conditions for fructification]

Top 3 dominant themes for this lifetime: [...]
Top 3 areas that need conscious work: [...]
```

---

## PHASE 4B — Event Timing Mode

### Step 1: Identify house combination
Load `references/house-combinations.md`. Identify positive set + negative set + primary house for the event.

### Step 2: Examine primary CSL
```
Primary house: [N] ([significance])
Cuspal Sub Lord: [planet]
  • Star-lord chain signifies: houses [...]
  • Own signification: houses [...]
  • Connection to positive set: [yes/no]
  • Connection to negative set: [yes/no]
  • Verdict: [will fructify / will not / mixed → check sub-sub]
```

If CSL signifies negative set only → matter denied. Stop here, deliver "will not fructify in this life" verdict.

### Step 3: Significators of relevant houses
For each house in the positive combination, list significators in 4 levels:
- L1: Planets in star of planet occupying the house
- L2: Planets occupying the house
- L3: Planets in star of the lord of the house
- L4: Lord of the house itself

### Step 4: Compute current Ruling Planets
Run `scripts/compute_ruling_planets.py` for **moment of this reading + user's location**.

Show full RP calculation (per `references/ruling-planets.md`).

### Step 5: RP cross-check with significators
Identify which planets are BOTH significators of the positive set AND Ruling Planets. These are the **strongest activation candidates** for fructification.

### Step 6: Identify fructification window
Examine the user's current and upcoming Vimshottari periods. Find the DBA-Sookshma where:
- MD lord is a significator (or is in star of one) of positive set
- BD lord same
- AD lord same
- SD lord narrows to days

Run `scripts/compute_sookshma.py` to compute Sookshma divisions inside current/relevant Antara periods.

### Step 7: Transit confirmation
Note key transit triggers — Jupiter and Sun transiting through significator stars at the timing window add confirmation.

### Step 8: Verdict
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERDICT — [event]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Outcome: [WILL FRUCTIFY / WILL NOT / CONDITIONAL]

Confidence: [HIGH / MEDIUM / LOW]

Primary timing window:
  [MD]-[BD]-[AD]-[SD]
  [start date] to [end date]

Reasoning:
  • CSL of house [N]: [verdict]
  • Significators activated: [planets, with houses they signify]
  • Ruling Planet alignment: [planets in both sets]
  • Dasha alignment: [running periods supporting]
  • Transit triggers: [Jupiter/Sun transit windows in this period]

Caveats:
  • [degree-sensitive flags — sandhi, gandanta]
  • [retrograde considerations]
  • [sub-sub-lord conflicts if any]

Action recommendation:
  [specific, actionable]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Critical Rules

1. **Never guess significators.** Use the chart's pre-computed table; if not provided, derive from planet positions explicitly.
2. **Always show RP calculation.** User wants to see the work.
3. **Sookshma is non-negotiable for event timing.** Antara alone is too coarse for date-level prediction.
4. **CSL of primary house is final.** If it says no, it's no — don't override with "but Jupiter is exalted."
5. **Retrograde rule:** Retrograde planet (except nodes) gives result of star-lord, not own. Apply consistently.
6. **No mixing with Parashari.** This is KP. Don't bring in Vimshottari Parashari rules like aspects or yogas — KP uses signification only.
7. **Outer planets (Uranus/Neptune/Pluto)** — display if provided but do not use in core KP analysis.

---

## Output Style
- Authoritative, precise, advisory tone (per user's professional output preferences)
- Show calculations explicitly
- Use tables liberally
- Pyramid principle — verdict first in summary, then full reasoning
- Don't hedge unnecessarily; if chart says no, say no
