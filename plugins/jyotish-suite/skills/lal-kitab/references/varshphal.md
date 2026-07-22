# Varshphal — Lal Kitab Annual Predictions

Lal Kitab uses an **age-based year-rulership** system distinct from any other school. Each year of life is ruled by one or more planets. The state of those planets in the natal chart determines that year's themes.

This is **not** Tajaka Varshphal (which casts a new chart for each solar return). Lal Kitab Varshphal works directly off the natal chart.

---

## Year-Ruler Table (Full)

| Age | Ruling Planet(s) | Notes |
|-----|-------------------|-------|
| 1   | Sun-Moon (mixed) | Infant phase |
| 2   | Moon | |
| 3   | Mars | |
| 4   | Mercury | |
| 5   | Jupiter | |
| 6   | Venus | |
| 7   | Saturn (first contact) | First minor Saturn impression |
| 8   | Rahu | |
| 9   | Ketu | |
| 10  | Sun | |
| 11  | Moon | |
| 12  | Mars | |
| 13  | Mercury | |
| 14  | Jupiter | |
| 15  | Venus | |
| 16  | Saturn | |
| 17  | Rahu | |
| 18  | Ketu | |
| 19  | Sun | |
| 20  | Moon | |
| **21** | **Jupiter major** | First major year — direction-setting |
| 22  | Venus | |
| 23  | Saturn | |
| **24** | **Venus major** | Marriage / partnership pivot |
| 25  | Mars | |
| 26  | Mercury | |
| **27** | **Moon major** | Emotional re-set; mother-related events likely |
| **28** | **Mars major** | Energy / conflict / decisive action |
| 29  | Saturn | |
| 30  | Rahu | |
| 31  | Ketu | |
| 32  | Sun | |
| 33  | Moon | |
| 34  | Mars | |
| 35  | Mercury | |
| **36** | **Saturn major (1st)** | First major Saturn year — career test, structural reset |
| 37  | Rahu | |
| 38  | Ketu | |
| 39  | Venus | |
| 40  | Sun | |
| 41  | Moon | |
| **42** | **Saturn + Rahu (severe)** | Most dangerous Lal Kitab year — health, career, family all stressed |
| 43  | Ketu | |
| 44  | Sun | |
| 45  | Mercury | |
| 46  | Jupiter | |
| 47  | Mars | |
| **48** | **Saturn major (3rd)** | Final career-defining Saturn year |
| 49  | Venus | |
| 50  | Sun | |
| 51  | Moon | |
| 52  | Jupiter | |
| 53  | Mercury | |
| **54** | **Mars + Saturn** | Health watch — surgical / structural risk |
| 55  | Venus | |
| 56  | Sun | |
| 57  | Moon | |
| 58  | Jupiter | |
| 59  | Mercury | |
| 60  | Saturn | |
| 61  | Rahu | |
| 62  | Ketu | |
| **63** | **Rahu major** | Final-phase pivot; spiritual / legacy reckoning |
| 64–70 | Cycling (Saturn-Jupiter-Sun-Moon dominant) | |
| 71+ | Jupiter increasingly dominant; Saturn determines longevity completion | |

---

## Major Year Markers (Always Flag These)

The following ages are **structural pivots** for almost every native. Always include these in any Varshphal output even if not in the immediate window:

- **21** — Jupiter — direction-setting; education/career commitment
- **24** — Venus — marriage / partnership formation
- **27–28** — Moon-Mars — emotional + decisive reset
- **36** — Saturn (1st major) — career legitimacy test
- **42** — Saturn + Rahu — most stressed year
- **48** — Saturn (3rd major) — career consolidation
- **54** — Mars + Saturn — health watch
- **63** — Rahu major — legacy phase begins

---

## How to Read a Year

For age **N** with ruler **P**:

### Step 1: Locate P in the natal chart
- Which house?
- What dignity (pakka ghar / exalted / debilitated / friendly / enemy)?
- Sleeping or awake?
- Involved in any rin?

### Step 2: Apply the year-template
The year's themes come from **the houses P signifies** in the chart:
- The house P sits in (primary domain of the year)
- The houses P aspects (secondary domains touched)
- The houses P owns (lord-houses) — matters of these houses also activate

### Step 3: Modulate by P's condition
| P's condition | Year quality |
|---------------|---------------|
| In pakka ghar | Year delivers full promised themes |
| Exalted | Strongly favorable in P's domains |
| Debilitated | Year stressed in P's domains |
| Sleeping | Year passes "muted" — neither big wins nor losses; opportunities missed |
| Friendly placement | Smooth themes, modest gains |
| Enemy placement | Friction, requires extra effort |
| Involved in rin | Themes carry karmic weight; requires upaay during this year |

### Step 4: Cross-check with major year status
If age N is a major year (21, 36, 42, 48, 63...), the planet's condition has **outsized impact**. A debilitated Saturn in a 36-year native produces structural career trauma; a strong Saturn in 36 produces breakthrough.

### Step 5: Identify the year's upaay
For any year where the ruler is afflicted or sleeping, prescribe the upaay associated with that planet (see `upaay_catalog.md`). Run the upaay for the **full year**, ideally starting 2–3 months before the birthday.

---

## Output Format Per Year

```
AGE [N] — Year Ruler: [planet name]
  Major year: [Yes/No — if Yes, which marker]

  Planet's condition in chart:
    House:           [N] ([sign])
    Pakka ghar:      [Yes/No]
    Dignity:         [exalted/deb/friendly/enemy/neutral]
    Sleep status:    [awake/sleeping]
    Aspects:         [list]
    Rin involvement: [if any]

  Houses activated this year:
    Primary:    [house planet sits in] → [theme]
    Aspects:    [houses aspected] → [themes]
    Owned:      [houses owned by planet] → [themes]

  Predicted themes:
    • [Specific theme tied to chart configuration]
    • [Specific theme]

  Risks:
    • [If planet is afflicted, specific risk areas]

  Recommended upaay for this year:
    [Reference to Phase 9 upaay #N]
    Duration: [12 months from age birthday, or 18 months if major year]
```

---

## Multi-Planet Year Handling

For ages with two rulers (1, 42, 54 — per the Year-Ruler Table above; age 28
is Mars alone, single-ruler), read **both planets** and weight by:

- The more afflicted planet dominates the year's challenges
- The stronger planet shows where opportunities lie
- The combination's mutual aspect (if any) creates a "lock pattern" — both planets must be addressed via upaay simultaneously

Example: Age 42 (Saturn + Rahu). If both are well-placed and not afflicting each other, year is intense but productive. If they aspect each other or are conjunct in the natal chart, year is the "classic 42-crisis" — health, career, marriage all under simultaneous stress. Upaay for 42 is non-negotiable in this case.

---

## Output for Sekshey's Reading Window

Skill should output, by default:

1. **Current age** — full reading
2. **Next 5 years** — brief reading each (3–5 lines)
3. **Next major year** (if not in next 5) — full reading
4. **Any 42 / 48 / 63 within the next 25 years** — full reading with upaay timing

This gives the user actionable awareness without overwhelming them.

---

## Caveats

1. **The age-rulership table is universal** — it doesn't change by chart. What changes is how **each planet plays out** based on its natal condition.

2. **Lal Kitab Varshphal does not predict specific dates within the year.** It tells you the year's quality and the upaay window. For date-level prediction, use KP (different skill).

3. **Multi-rin charts compound year-stress.** If two rins are active and the year-ruler is involved in one of them, severity escalates one tier.

4. **Upaay timing within a year:** Most year-upaay should start 60–90 days before the birthday and continue through the full year. Some Saturn-year upaay (especially 42, 48) should start at age birthday minus 6 months.
