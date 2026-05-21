# KP Natal — Orchestration & Reading Notes

Interpretive guidance preserved from the pre-orchestrator SKILL.md. Workers and
the synthesizer load this alongside `methodology.md`.

## Chart Intake Format (for Phase A)

Use this prompt to ask the user for a chart:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KP Natal Reading — share your natal KP chart, or birth data and I'll
compute it.

Option 1 — paste a pre-computed KP chart:
  • Birth details (date, time, place, lat/long) and ayanamsa (KP New)
  • All 12 cuspal positions — degree, sign-lord, star-lord, sub-lord,
    sub-sub-lord
  • All 9 planets (Sun–Ketu) — longitude, sign, star-lord, sub-lord,
    sub-sub-lord, retrograde
  • Vimshottari dasha sequence (MD-BD-AD with start dates)
  • Significator table if you have it — if not, it is derived from the
    planet positions

Option 2 — give birth data:
  • Date, exact time, place — a KP chart (KP-New ayanamsa, Placidus
    cusps) is computed for you

Upload a markdown file or paste directly. Any format is fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

`chart-verifier` parses a pasted chart (via `chart_io.py`, mode `kp`) or renders
a computed one, then produces the verification display below.

## Mode Selection Prompt (for Phase A)

Ask which reading the user wants:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What kind of KP reading?

  A. Life reading — comprehensive analysis of all 12 houses, declaring
     which life areas will fructify and which won't (cuspal sub-lords
     across every house).

  B. Event timing — a specific WHEN question (marriage, job change,
     child, property, health recovery…). Tell me:
       • What event?
       • Time horizon — next 1 year / 3 years / open-ended?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Wait for the user's choice before Wave 1.

## Critical rules (apply throughout every reading)

1. **Never guess significators.** Use the baseline's pre-computed 4-level
   significator table; if a chart was user-supplied without one, it was derived
   explicitly in the baseline — never invent.
2. **Always show the RP calculation.** The user wants to see the work. The
   baseline emits the full Ruling Planets derivation; surface it verbatim.
3. **Sookshma is non-negotiable for event timing.** Antara alone is too coarse
   for date-level prediction. The baseline computes the 4th-level Sookshma
   divisions; the timing verdict must cite DBA-SD, not DBA alone.
4. **CSL of the primary house is final.** If the cuspal sub-lord says no, it is
   no — do not override with "but Jupiter is exalted" or any dignity argument.
5. **Retrograde rule.** A retrograde planet (except the nodes) gives the result
   of its star-lord, not its own. Apply consistently in significator analysis.
6. **No mixing with Parashari.** This is KP. Do not import Parashari aspects,
   yogas, or classical benefic/malefic logic — KP uses signification only.
7. **Outer planets (Uranus/Neptune/Pluto).** Display if provided, but never use
   them in core KP analysis — KP is a 9-graha system.

## Reading-mode parallelism

- **Life Reading** walks all 12 cuspal sub-lords. The 12 cusps are mutually
  independent units — fan out 12 `unit-analyzer` workers, one per cusp.
- **Event Timing** is the 8-step KP read (see `methodology.md`). The steps are
  largely sequential: each feeds the next (house combination -> primary CSL
  verdict -> significators -> RP cross-check -> DBA-Sookshma window -> transit
  -> verdict). Only Step 3 (listing significators of each positive-set house)
  fans out — 2-4 workers, one per relevant house. The real speed win for timing
  comes from the baseline sidecar pre-computing CSL chains, significators, RP
  and Sookshma, not from fan-out.

## Output style

- Authoritative, precise, advisory tone.
- Show calculations explicitly; use tables liberally.
- Pyramid principle — verdict first in the summary, then the full reasoning.
- Do not hedge unnecessarily; if the chart says no, say no.

## Verification Display Format

`chart-verifier` renders the confirmed KP chart into exactly this layout. The
orchestrator shows it and waits for the user to reply "Confirmed". KP natal
uses no D9 — do not render one.

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
| ...  |            |       |       |       |       |   (one row per cusp, 1..12)

PLANETARY POSITIONS
| Planet  | Degree     | Sign  | Star  | Sub   | SS    | Retro |
|---------|------------|-------|-------|-------|-------|-------|
| Sun     | ddd-mm-ss  | XXX   | XXX   | XXX   | XXX   |  R/—  |
| ...     |            |       |       |       |       |       |   (one row per planet, Sun..Ketu; outer planets optional)

SIGNIFICATORS OF HOUSES
| House | Planets                          |
|-------|----------------------------------|
|   1   | XX, XX                           |
| ...   |                                  |   (one row per house, 1..12)

CURRENT DASHA (as per chart):
[MD] Mahadasha — running [start] to [end]
  [BD] Bhukti — running [start] to [end]
    [AD] Antara — running [start] to [end]

Confirm this matches your records before I proceed?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The baseline extends the supplied MD/BD/AD dasha to the 4th-level Sookshma.

Do not proceed until the user explicitly confirms.
