# Lal Kitab Astrology Skill

Performs full Lal Kitab readings strictly per Pt. Roop Chand Joshi's original Farmans (1939–1952). Companion to `vedic-astro`, `kp-natal`, `bnn-astrology`, and `jaimini-astrology`.

## Trigger

`/lal-kitab` anywhere in a message.

Also triggered by phrases like "Lal Kitab reading", "rin diagnosis", "Pitri Rin", "upaay", "Lal Kitab remedies", or providing a Vedic chart with a request for Lal Kitab interpretation.

## What It Does

1. Captures user intent up front (specific question vs. full read) to tilt narration and pre-route the reading mode — baseline always runs in full
2. Accepts a pre-computed Vedic D1 chart
3. Re-maps to Lal Kitab fixed-house frame (Aries always 1st)
4. Computes pakka ghar / dignity / friendship status by **house number, not sign**
5. Identifies sleeping planets via Lal Kitab aspect rules
6. Diagnoses six karmic debts (Pitri / Matri / Stri / Kanya / Bhratra / Atma Rin)
7. Classifies teva (chart type)
8. Reads house-by-house OR family chart impact OR varshphal OR event timing — user's choice
9. Event timing — answers "when will X happen?" via a four-signal convergence engine (maturation + year-ruler + house cycle + Jupiter sanctification) with every window paired to an activating upaay
10. Prescribes ranked upaay with Farman citations

## What It Does NOT Do

- Use D9 / Navamsa or any divisional chart (Lal Kitab is single-chart)
- Use Nakshatras or Vimshottari Dasha (those are Parashari)
- Mix Lal Kitab dignity with sign-based Vedic dignity
- Invent remedies — every upaay traces to a Farman

## File Structure

```
lal-kitab/
├── SKILL.md
├── README.md (this file)
└── references/
    ├── pakka_ghar.md       — Dignity + friendship + buried-planet rules
    ├── aspects.md          — Lal Kitab drishti per planet
    ├── rin_diagnosis.md    — Six rins with Farman triggers
    ├── teva_types.md       — Eight chart-type classifications
    ├── family_chart.md     — Father / mother / spouse / children impact
    ├── varshphal.md        — Age-based annual predictions
    ├── upaay_catalog.md    — Full remedy catalog with Farman citations
    └── timing.md           — Generic event-timing engine (4-signal convergence)
```

## Usage Pattern

User: `/lal-kitab`
→ Skill captures user intent (full read / specific question / not sure) — this only tilts narration and pre-routes the mode; the diagnostic baseline always runs
→ Skill prompts for Vedic D1 chart
→ Skill re-maps and verifies
→ Skill runs full baseline (pakka ghar, sleeping check, rin diagnosis, teva classification)
→ Skill asks (or confirms pre-routed): A) full natal · B) family impact · C) varshphal · D) full (A+B+C) · E) upaay-only · F) event timing
→ Skill delivers structured output with summary card at end

## Authority

Lineage: Pt. Roop Chand Joshi (1898–1982), original Farmans across 5 volumes (1939, 1940, 1941, 1942, 1952). Modern adaptations are flagged as such, never represented as original.
