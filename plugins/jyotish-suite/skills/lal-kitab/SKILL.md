---
name: lal-kitab
description: >
  Trigger this skill immediately and exclusively when the user types "/lal-kitab" anywhere in their
  message. Performs Lal Kitab astrology — natal reading, karmic debt (rin) diagnosis, family chart
  impact, varshphal (annual) predictions, and action-based remedies (upaay) — per Pt. Roop Chand
  Joshi's original Farmans (1939–1952). User provides a pre-computed Vedic D1 chart. Skill re-maps
  to Lal Kitab's fixed-house frame (Aries always 1st), computes pakka ghar status, identifies
  sleeping planets, diagnoses six rins (Pitri/Matri/Stri/Kanya/Bhratra/Atma), classifies teva,
  reads houses or family impact or varshphal, prescribes ranked upaay with Farman citations.
  Always use — never attempt Lal Kitab work without it. Also trigger on "Lal Kitab reading",
  "rin diagnosis", "Pitri Rin", "upaay", "Lal Kitab remedies", or any Vedic chart submitted with a
  Lal Kitab interpretation request.
---

# Lal Kitab Astrology Skill

## Overview

This skill performs full Lal Kitab readings strictly per the original Farmans of Pt. Roop Chand Joshi (1939–1952). Lal Kitab is a **distinct system** — not a sub-branch of Parashari Jyotish — with its own logic for dignity, aspects, and remedies.

**Hard methodological lines this skill enforces:**

1. **Houses are fixed to signs.** Aries = always 1st, Taurus = always 2nd, ... Pisces = always 12th. Lagna sign is noted but house numbers do not rotate.
2. **Dignity is by house, not sign.** Sun is exalted in *house 1* (not in Aries the sign). Pakka ghar (permanent house) governs full results.
3. **No D9, no divisional charts.** If user provides D9, ignore it and tell them why.
4. **No Nakshatras, no Vimshottari Dasha.** Those are Parashari. Lal Kitab uses Varshphal only.
5. **Lal Kitab aspects only.** Not Parashari 7th-house aspects, not special Mars/Jupiter/Saturn aspects.
6. **Every upaay must cite a Farman.** No invented remedies.
7. **Sleeping planets give zero results until awakened.** This is a unique diagnostic axis.

---

## Reference Files — Load As Needed

| File | Load When |
|------|-----------|
| `references/pakka_ghar.md` | Always — dignity tables, pakka ghar, exaltation/debilitation by house |
| `references/aspects.md` | Always — Lal Kitab drishti rules per planet |
| `references/rin_diagnosis.md` | Phase 5 — debt detection rules with Farman citations |
| `references/teva_types.md` | Phase 6 — chart classification rules |
| `references/upaay_catalog.md` | Phase 9 — full remedy catalog with Farman citations |
| `references/varshphal.md` | Phase 8 — year-rulership and annual prediction rules |
| `references/family_chart.md` | Phase 7 — father/mother/spouse/children impact analysis |

---

## PHASE 1 — Chart Collection

When `/lal-kitab` is triggered, prompt the user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAL KITAB READING

Please share your Vedic D1 chart. Either:
  • Upload a markdown file with the chart data
  • Or paste it directly

Required data:
  • Birth details (date, time, place, lat/long)
  • Ayanamsa used (Lahiri preferred; KP New acceptable)
  • Lagna sign + degree
  • All 9 planets (Sun through Ketu) with:
      sign, house number (1–12), degree, retrograde flag
  • Current age (for Varshphal)

NOT used by this skill:
  • D9 (Navamsa) — Lal Kitab is a single-chart system
  • Nakshatras / Vimshottari Dasha — these are Parashari
  • Outer planets (Uranus/Neptune/Pluto)

If you provide D9 or these elements, I will display them but
will not factor them into the reading. Lal Kitab's logic
breaks if mixed with sign-based or divisional methods.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PHASE 2 — Re-map to Lal Kitab Frame

Take the Vedic D1 and re-render in the Lal Kitab fixed-house frame.

**Re-mapping rule:** In the Vedic chart, the user's planets are placed in houses 1–12 relative to their Lagna. In Lal Kitab, we discard that and place each planet by its **sign-as-house**:

- Aries → house 1
- Taurus → house 2
- Gemini → house 3
- Cancer → house 4
- Leo → house 5
- Virgo → house 6
- Libra → house 7
- Scorpio → house 8
- Sagittarius → house 9
- Capricorn → house 10
- Aquarius → house 11
- Pisces → house 12

So if the Vedic chart shows Sun in Leo (sign) which happens to be the 5th house from Cancer Lagna, in Lal Kitab Sun simply sits in **house 5** (Leo's permanent slot). The Lagna sign is recorded separately as a *flavour* but does not rotate the houses.

Display the re-mapped chart:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAL KITAB CHART (re-mapped)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Native: [name]
Born: [date] at [time]
Place: [city]
Vedic Lagna: [sign] [degree] (recorded only — houses do not rotate)
Current Age: [N] years

PLANETARY HOUSE PLACEMENT (Lal Kitab)
| House | Sign        | Planet(s)     | Degree(s) | Retro |
|-------|-------------|---------------|-----------|-------|
|   1   | Aries       | [planets]     |           |       |
|   2   | Taurus      |               |           |       |
|   3   | Gemini      |               |           |       |
|   4   | Cancer      |               |           |       |
|   5   | Leo         |               |           |       |
|   6   | Virgo       |               |           |       |
|   7   | Libra       |               |           |       |
|   8   | Scorpio     |               |           |       |
|   9   | Sagittarius |               |           |       |
|  10   | Capricorn   |               |           |       |
|  11   | Aquarius    |               |           |       |
|  12   | Pisces      |               |           |       |

Empty houses: [list]
Confirm this matches before I proceed?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

After confirmation, proceed.

---

## PHASE 3 — Pakka Ghar & Dignity Status

Load `references/pakka_ghar.md`.

For each planet, compute:

| Planet | Current House | Pakka Ghar | Status | Dignity |
|--------|---------------|------------|--------|---------|

**Status values:**
- **In Pakka Ghar** — planet sits in its permanent home, gives full results
- **Exalted** — sits in its exaltation house (per LK table, by house number)
- **Debilitated** — sits in its debilitation house
- **Friendly** — sits in a house owned by a friend (per LK friendship table)
- **Enemy** — sits in a house owned by an enemy
- **Neutral** — sits in a house neither friend nor foe

For each planet not in pakka ghar, also note:
- Who owns the pakka ghar of this planet (lord of that house)
- What planet currently sits in this planet's pakka ghar (if any)

This second pair governs how the displaced planet's results manifest.

---

## PHASE 4 — Sleeping vs Awake Planets

A planet is **sleeping (sutela)** if:
- No other planet sits with it in the same house, AND
- No other planet aspects it per Lal Kitab aspect rules

Sleeping planets give **zero results** — neither good nor bad — until awakened by a transit, varshphal trigger, or upaay.

Load `references/aspects.md` to compute aspects correctly. Output:

```
SLEEPING PLANETS: [list]
AWAKE PLANETS:    [list with what aspects/conjuncts them]
```

Sleeping planets are a major diagnostic — if a benefic is sleeping, its promised results never materialize without intervention.

---

## PHASE 5 — Rin (Karmic Debt) Diagnosis

Load `references/rin_diagnosis.md`.

Run all six rin checks systematically:

1. **Pitri Rin** (debt to father / paternal ancestors) — Sun, 9th house, specific Sun-Saturn / Sun-Rahu combinations
2. **Matri Rin** (debt to mother / maternal lineage) — Moon, 4th house, specific Moon-Ketu / Moon-Saturn combinations
3. **Stri Rin** (debt to wife / feminine principle) — Venus, 7th house, specific Venus-Rahu / Venus-Saturn combinations
4. **Kanya Rin** (debt to daughter / sister-in-law) — Mercury or Jupiter in specific afflicted positions
5. **Bhratra Rin** (debt to brother) — Mars and Mercury combinations, 3rd house afflictions
6. **Self / Atma Rin** (debt to one's own soul) — Jupiter afflicted, "blind chart" patterns, no planets in trines

For each rin found, output:

```
RIN: [name]
Trigger Farman: [citation, e.g. "Farman 8, Vol 2 (1940)"]
Configuration in this chart: [explicit reason — which planets, which houses]
Severity: [Mild / Moderate / Severe]
Manifestation in life: [what areas this debt shows up in]
Remedy reference: see Phase 9, upaay #[N]
```

If no rin is detected, state that explicitly and briefly note what configurations would have triggered each.

---

## PHASE 6 — Teva (Chart Type) Classification

Load `references/teva_types.md`.

Classify the chart into one or more teva types based on planetary distribution patterns:

- **Andha Teva** (blind) — both luminaries afflicted, key houses empty
- **Lula Teva** (lame) — Mars/Saturn affliction patterns affecting movement / livelihood
- **Behra Teva** (deaf) — communication / Mercury affliction patterns
- **Sukhi Teva** (happy) — benefics in pakka ghar, no major rin
- **Dukhi Teva** (sorrowful) — multiple rins, multiple sleeping benefics
- **Rajyogi Teva** — specific royal-yoga patterns per Lal Kitab (different from Parashari raja yogas)
- **Pujari Teva** — strong Jupiter + Ketu placement, spiritual life path

Output the dominant teva + any secondary types, with explanation tied to specific configurations.

---

## PHASE 7 — Mode Selection

```
What kind of reading?

  A. Full natal reading — house-by-house life analysis
     for the native (you)

  B. Family chart impact — how this chart affects:
       father, mother, spouse, children, siblings
     Lal Kitab is famous for this — your chart shapes
     your relatives' fortunes too

  C. Varshphal — annual predictions for current age
     and major upcoming year-rulers

  D. Full reading (A + B + C combined)

  E. Upaay focus — skip to remedies based on what's
     already been diagnosed
```

Wait for user's choice. Proceed to corresponding phase(s).

---

## PHASE 8A — Natal House-by-House Reading

For each house 1–12, output:

```
HOUSE [N] — [Lal Kitab significance]
  Sign:        [Aries/Taurus/...]
  Owner:       [planet]
  Planets in:  [list, or "empty"]
  Aspects on:  [planets aspecting this house]

  Key dynamics:
    • [Specific Farman-driven interpretation]
    • [Pakka ghar interaction]
    • [Sleeping/awake status of resident planets]

  Verdict for matters of house [N]:
    [Strong / Mixed / Weak / Blocked]
  Reasoning: [tied to specific configurations]
```

After all 12 houses, deliver synthesis:

```
LAL KITAB SYNTHESIS

Strongest life areas:
  • [House X — domain] — [why]

Blocked / weak areas:
  • [House Y — domain] — [why]

Areas requiring upaay (linked to rin):
  • [House Z] — [which rin → which upaay]
```

---

## PHASE 8B — Family Chart Impact

Load `references/family_chart.md`.

Lal Kitab maps each family member to specific houses and planets:

| Family Member | Primary Houses | Primary Planets |
|---------------|----------------|------------------|
| Father        | 9, 10          | Sun, Saturn      |
| Mother        | 4, 7           | Moon, Venus      |
| Spouse (wife) | 7, 2           | Venus            |
| Spouse (husband for female native) | 7, 9 | Jupiter, Mars |
| Sons          | 5              | Sun, Jupiter     |
| Daughters     | 5, 9           | Mercury, Venus   |
| Elder sibling | 11             | Jupiter          |
| Younger sibling | 3            | Mars, Mercury    |

For each family member, analyze:
- Condition of their primary house(s) in this chart
- Condition of their karaka planet
- Whether the native's chart **supports** or **drags down** that relative's fortune
- Specific Farman rules for life-events of that relative as visible from native's chart

Output structured per relative:

```
FATHER
  Primary house 9: [condition]
  Sun:             [house, status]
  Saturn:          [house, status]

  Reading:
    • Father's longevity: [LK rule → outcome]
    • Father's fortune via this native: [enhancing / draining]
    • Specific events: [from Farman rules]

  Recommended upaay (if drain detected): [reference]
```

---

## PHASE 8C — Varshphal (Annual) Predictions

Load `references/varshphal.md`.

Lal Kitab year-rulership table (by age):

| Age Years | Ruling Planet |
|-----------|----------------|
| 1–2       | Sun-Moon child phase |
| 21        | Jupiter major |
| 24        | Venus  |
| 27        | Moon   |
| 28        | Mars   |
| 36        | Saturn (first major Saturn year) |
| 42        | Saturn + Rahu (severe) |
| 48        | Saturn (third) |
| 54        | Mars + Saturn |
| 63        | Rahu major |
| ...       | (full table in reference) |

For the user's **current age** + **next 5 years** + **next major ruler year**:

```
AGE [N] — Year Ruler: [planet]
  Status of [planet] in chart: [pakka ghar / debilitated / sleeping]
  Relevant houses activated: [list]
  Predicted themes: [tied to planet's chart condition]
  Risks: [if planet is afflicted]
  Upaay for this year: [reference Phase 9]
```

Pay particular attention to the "danger years" — 21, 36, 42, 48, 63 — even if not in current window.

---

## PHASE 9 — Upaay (Remedies)

Load `references/upaay_catalog.md`.

Output remedies in **three priority tiers**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UPAAY — RANKED BY URGENCY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TIER 1 — Critical (rin-related, do first)
─────────────────────────────────────────
1. [Upaay name]
   For:        [which rin / which planet]
   Action:     [specific physical action]
   Frequency:  [daily / weekly / one-time / age-bound]
   Duration:   [how long to perform]
   Timing:     [specific day, time, or astrological window]
   Farman:     [citation]
   Caution:    [contraindications, e.g. who must NOT do this]

TIER 2 — Strengthening (for sleeping benefics, weak houses)
─────────────────────────────────────────
[same structure]

TIER 3 — Maintenance (lifestyle / dietary / behavioral)
─────────────────────────────────────────
[same structure]
```

**Hard upaay rules (enforced):**

1. **Every upaay must cite a Farman.** If a remedy is in modern tradition but not in originals, mark it `[Modern Tradition — not in original Farmans]` and rank it lower.
2. **Conflicting upaay must be flagged.** Some remedies cancel each other (e.g. you cannot do both copper-in-water for Mars and gold-wearing for Sun simultaneously without specific timing).
3. **Age-bound upaay must state the age window.** Some Farmans bind remedies to specific years.
4. **Pregnancy / health contraindications must appear if relevant.**
5. **No mantras, no pujas as primary upaay.** Lal Kitab is action-based; if an upaay sounds like a Vedic puja, it's not Lal Kitab.

---

## PHASE 10 — Final Synthesis

Close with a one-page summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAL KITAB READING — SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chart type (teva):           [primary + secondary]
Active rins:                 [list with severity]
Sleeping planets:            [list]
Strongest houses:            [list]
Weakest houses:              [list]

Top 3 life themes:
  1. [theme]
  2. [theme]
  3. [theme]

Top 3 priority upaay:
  1. [name + Farman ref]
  2. [name + Farman ref]
  3. [name + Farman ref]

Watch-year (next danger year ahead): [age + planet]
Watch-year upaay:                    [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Critical Rules (Hard Enforcement)

1. **Houses NEVER rotate.** Aries = 1, Taurus = 2, ..., Pisces = 12. Always.
2. **Dignity is by HOUSE NUMBER, not by SIGN.** Use Lal Kitab tables only.
3. **Reject D9 / Navamsa input.** Display if provided, exclude from analysis with explicit note.
4. **Reject Nakshatras and Vimshottari Dasha for Lal Kitab analysis.** These are Parashari. Mention only if user asks why.
5. **Lal Kitab aspects only.** Each planet has its own aspect rules per `references/aspects.md`. Do not import Parashari aspects.
6. **Sleeping planet = zero result.** State this clearly, do not "soften" it with Vedic dignity reasoning.
7. **Every upaay cites a Farman.** No exceptions. Modern adaptations get flagged.
8. **No mixing of systems mid-reading.** If the user asks "but in KP / BNN / Jaimini...", redirect to those skills — do not blend.
9. **Be honest about ambiguity.** Where Farmans conflict or are cryptic, say so. Do not fabricate certainty.
10. **Ancestor lineage:** When citing a Farman, cite Pt. Roop Chand Joshi's volumes only. Modern commentaries (Arun Sanhita, U.C. Mahajan, etc.) are flagged as such, not stated as authoritative.

---

## Output Style

- Authoritative, precise, advisory tone (per user's professional output preferences)
- Show every diagnostic step explicitly — pakka ghar status, sleeping check, rin trigger, teva
- Use tables liberally
- Pyramid principle — verdict first in summary, full reasoning underneath
- No hedging unnecessarily; if a rin is present, name it. If a planet is sleeping, declare it.
- Sanskrit/Urdu terms italicized once on first use, then plain text
- Farman citations in `[Farman X, Vol Y (year)]` format
