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
| `references/varshphal.md` | Phase 8C — year-rulership and annual prediction rules |
| `references/family_chart.md` | Phase 8B — father/mother/spouse/children impact analysis |
| `references/timing.md` | Phase 8D — generic event-timing convergence engine (maturation + year-ruler + house cycle + Jupiter sanctification) |

---

## PHASE 0 — Intent Capture (Optional Pre-Filter)

When `/lal-kitab` is triggered, BEFORE asking for the chart, prompt the user:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAL KITAB READING

What brings you here today?

  1. Just read my chart — full diagnostic + house-by-house
     (defaults to Mode D after baseline)

  2. Specific question — tell me what you want answered
     Examples:
       • "When will I change jobs?"          → Mode F (timing)
       • "How is my father affected?"        → Mode B (family)
       • "What about this year ahead?"       → Mode C (varshphal)
       • "Just give me the upaay priorities" → Mode E (remedies)
       • "Do I have Pitri Rin?"              → Mode A + Phase 5 focus

  3. Not sure — show me what's possible after baseline
     (defaults to Phase 7 mode menu)

You can also just answer in your own words. I'll run the full
diagnostic baseline either way — your answer helps me weight
the reading toward what matters to you.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Intent capture rules:**

1. **Store the intent** as `user_intent` for use across all baseline phases (1–6) and the eventual mode routing in Phase 7.
2. **The baseline ALWAYS runs in full.** Intent does not skip phases — it only tilts narration and weights what to emphasize.
3. **Mode pre-routing.** If intent maps cleanly to one of Modes A–F, mark it as the *suggested* mode. Phase 7 then asks for confirmation rather than presenting the full menu:
   ```
   Based on what you asked, I'd run Mode F (event timing for "[event]").
   Confirm, or pick a different mode?
   ```
4. **Ambiguous intent → default behaviour.** If the user picks option 3 or gives unclear input, treat as standard flow and present full Phase 7 menu.
5. **Intent-driven narration tilting.** During baseline phases, emphasize configurations relevant to the user's question:

| User Intent Signals | Baseline Phases Should Emphasize |
|---------------------|----------------------------------|
| Marriage / partnership / relationship | Venus condition, 7th house, 2nd house, Stri Rin (P5), Sukhi vs Dukhi teva (P6) |
| Career / job / promotion | Sun + Saturn condition, 10th & 6th houses, Pitri Rin (P5), Rajyogi vs Lula teva (P6) |
| Father / paternal | Sun condition, 9th house, Pitri Rin (P5), family chart routing (P8B) |
| Mother / maternal / home | Moon condition, 4th house, Matri Rin (P5), family chart routing (P8B) |
| Children | Jupiter condition, 5th house, Kanya Rin (P5) |
| Money / finance / wealth | 2nd, 11th houses, Jupiter & Venus condition |
| Health | 6th, 8th houses, Sun + Mars condition, danger years (P8D) |
| Foreign / travel / settlement | Rahu condition, 12th & 9th houses |
| Spiritual / detachment | Ketu + Jupiter condition, 12th house, Pujari teva (P6) |
| Generic / no question | Standard emphasis across all axes |

6. **Honesty rule.** If intent suggests something the chart can't cleanly answer (e.g. "tell me my exact death date"), state the boundary directly in Phase 0 itself and offer the closest legitimate read.

After capturing intent, proceed to Phase 1.

---

## PHASE 1 — Chart Collection

After Phase 0 captures intent, prompt the user for chart data:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHART INPUT

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

**If Phase 0 captured a clear intent that maps to a specific mode**, present a confirm-or-override prompt instead of the full menu:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MODE ROUTING

You asked: "[user's original question]"

Suggested mode: [A / B / C / D / E / F] — [mode name]
Reason: [why this mode fits the question]

Confirm this mode, or pick a different one:
  • Press confirm → run Mode [X]
  • Or pick from full menu (A–F)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**If Phase 0 intent was ambiguous, skipped, or user picked option 3**, present the full menu:

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

  F. Event timing — when will [X] happen for this chart?
     Specify the event (marriage, career pivot, child,
     property, foreign travel, business launch, etc.)
     Returns probability-weighted age windows + activation
     upaay using the four-signal convergence engine.
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

## PHASE 8D — Lal Kitab Timing Synthesis (Generic Event-Timing Engine)

Load `references/timing.md`.

This phase answers "when will [event] happen?" for **any** life event — marriage, career pivot, child, property, foreign travel, business launch, health, recognition, loss. It is event-agnostic; only the significator mapping changes.

**Invoke this phase when:**
- User selected Mode F in Phase 7
- User asks a "when" question after any other reading mode
- Mode D (full reading) — run this for the top 2–3 events user flags as relevant

**Required input from user:** the specific event being timed. Do not assume. If the user says "tell me about my career," ask whether they want career *condition* (Phase 8A house 10 read) or career *timing* (this phase).

### Step-by-step protocol

Follow Part D of `references/timing.md` literally. Summary:

1. **Map the event** to primary houses, primary planet(s), secondary planets using the table in Part B of `timing.md`. If the event is not in the table, derive from `pakka_ghar.md` and karaka logic — and state the derivation.

2. **Build the signal timeline** across the relevant age window (default: current age to current age + 15 years; extend if user asks for full-life).

3. **Score each candidate year** by counting how many of the four signals fire:
   - Signal 1: Planetary maturation age of primary significator
   - Signal 2: Year-ruler matches event's planets
   - Signal 3: Primary house in active period (35-year cycle)
   - Signal 4: Jupiter year-ruler OR Jupiter aspect on primary house

4. **Apply Filter 1 (sleeping significator).** If primary planet is sleeping, demote unless an awakening trigger fires that year.

5. **Apply Filter 2 (rin overlay).** Push windows if event-relevant rin is active.

6. **Apply Filter 3 (danger year).** Invert probability for positive vs. negative events.

7. **Rank and output** using the template in Part E of `timing.md`.

### Output requirements

- Always 2–3 windows ranked by probability — never a single date
- Each window must show *why* it scored (which signals fired)
- Each window must be paired with the upaay that activates or stabilizes it
- Caveats block must appear: probabilistic-not-deterministic, year-not-date, upaay-can-pull-or-collapse

### Hard rules for this phase

1. **Never give specific dates.** Lal Kitab gives years and probability tiers. For date-precision, redirect to KP horary.
2. **Never time-call from one signal.** A single-signal year is weak evidence. Minimum two signals for a "moderate window," three for "strong."
3. **Always pair timing with upaay.** Lal Kitab refuses prediction without prescription. If no upaay is needed, state that explicitly.
4. **Never use Vimshottari Mahadasha logic.** Even if the user asks for it, refuse and explain — Lal Kitab's four-signal system is the complete toolkit.
5. **State derivations.** If you map an event using non-table karaka logic, show the derivation so the user can audit it.

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
11. **Timing is probabilistic, never deterministic.** Phase 8D outputs year-windows with probability tiers, never specific dates. Use the four-signal convergence engine (maturation + year-ruler + house cycle + Jupiter sanctification). Single-signal timing calls are prohibited. Every timing window must be paired with the upaay that activates or stabilizes it.
12. **Intent capture is pre-baseline, not pre-diagnostic.** Phase 0 captures user intent BEFORE chart collection but the full baseline (Phases 1–6) always runs. Intent only *tilts narration emphasis* and *pre-routes Phase 7* — it never skips diagnostic steps. A user asking "when will I marry" still receives full pakka ghar, sleeping, rin, and teva diagnostics; what changes is which configurations get highlighted in the narration.

---

## Output Style

- Authoritative, precise, advisory tone (per user's professional output preferences)
- Show every diagnostic step explicitly — pakka ghar status, sleeping check, rin trigger, teva
- Use tables liberally
- Pyramid principle — verdict first in summary, full reasoning underneath
- No hedging unnecessarily; if a rin is present, name it. If a planet is sleeping, declare it.
- Sanskrit/Urdu terms italicized once on first use, then plain text
- Farman citations in `[Farman X, Vol Y (year)]` format
