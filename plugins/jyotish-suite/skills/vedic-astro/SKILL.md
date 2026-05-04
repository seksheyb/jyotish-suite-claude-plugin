---
name: vedic-astro
description: >
  Trigger this skill immediately and exclusively when the user types "/vedic-astro" anywhere in their
  message. This skill accepts a pre-computed Vedic birth chart (D1 + D9), displays it back for
  verification, then performs a deep multi-layered Vedic astrological reading using rigorous methodology
  covering Nakshatras, Padas, degrees, aspects, Dashas, and composite synthesis. Always use this skill —
  never attempt Vedic chart work without it. Also trigger when user says "read my chart", "do my kundli",
  "analyze my birth chart vedic", or references Jyotish analysis with chart data already provided.
---

# Vedic Astrology Skill

## Overview
This skill handles the complete Vedic astrology reading workflow:
1. Accept chart data from the user (no computation — user provides the chart)
2. Display chart back in structured format for verification
3. Collect the question
4. Execute the full Vedic analysis methodology

**Reference files — load when needed:**
| File | Load When |
|------|-----------|
| `references/methodology.md` | Before every reading — full analysis framework |
| `references/nakshatra-table.md` | When identifying Nakshatra, Gana, or Pada Lord |
| `references/navamsa-table.md` | When computing or verifying D9 placements |
| `references/degree-flags.md` | When checking Gandanta, Mrityu Bhaga, Pushkara, Sandhi, Planetary War |
| `references/functional-roles.md` | When determining functional benefic/malefic by Lagna |

---

## PHASE 1 — Chart Collection

When `/vedic-astro` is triggered, ask the user to provide their chart:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Please share your Vedic birth chart data. Include:

D1 (Rashi) Chart:
  • Lagna — sign and degree
  • Each planet — sign, degree, house (retrograde status if known)

D9 (Navamsa) Chart:
  • Lagna sign
  • Each planet — sign and house

Dasha Balance:
  • Current Mahadasha planet and remaining period
    (or date of birth so I can compute it)

Paste from Jagannatha Hora, Astro-Seek, Astro.com (Vedic/Lahiri setting),
or any Vedic software. Any format is fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Accept any format** — tabular, paragraph, software export, or conversational.
Parse it into the internal chart structure. Derive missing Nakshatra data from planet degrees using `references/nakshatra-table.md`.

- If D9 is not provided → ask before proceeding: *"Do you have your D9 (Navamsa) chart? It enables Pada Lord analysis and D9-level confirmation. Share it now, or reply 'Skip D9' to proceed with D1 only."* Wait for response.
- If user skips D9 → proceed with D1 only; suppress all Pada Lord steps and D9 analysis throughout; flag this once in the reading output: *"D9 not provided — Pada Lord and Navamsa analysis omitted."*
- If D9 is provided → Pada Lord is the lord of each planet's D9 sign; derive from the D9 chart directly
- If Dasha balance is missing but DOB is given → compute Vimshottari Dasha balance from Moon's Nakshatra

---

## PHASE 2 — Chart Verification Display

Reformat the provided chart data into the standard display and show it back. User MUST confirm before proceeding.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        VEDIC BIRTH CHART (D1 — Rashi)
        Ayanamsa: Lahiri | Houses: Whole Sign
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAGNA: [Sign] [Degree]°[Min]' — [Nakshatra] Pada [#]

D1 PLANET POSITIONS:
┌─────────┬──────────┬────────────┬──────────────────────┬──────┬──────┬───────┐
│ Planet  │ Sign     │ Degree     │ Nakshatra (Pada)     │ House│  R?  │ Flags │
├─────────┼──────────┼────────────┼──────────────────────┼──────┼──────┼───────┤
│ Sun     │          │ XX°XX'XX"  │                      │      │      │       │
│ Moon    │          │ XX°XX'XX"  │                      │      │      │       │
│ Mars    │          │ XX°XX'XX"  │                      │      │      │       │
│ Mercury │          │ XX°XX'XX"  │                      │      │      │       │
│ Jupiter │          │ XX°XX'XX"  │                      │      │      │       │
│ Venus   │          │ XX°XX'XX"  │                      │      │      │       │
│ Saturn  │          │ XX°XX'XX"  │                      │      │  R   │       │
│ Rahu    │          │ XX°XX'XX"  │                      │      │  R   │       │
│ Ketu    │          │ XX°XX'XX"  │                      │      │  R   │       │
└─────────┴──────────┴────────────┴──────────────────────┴──────┴──────┴───────┘

Flags: [Ex]=Exalted [Db]=Debilitated [Own]=Own Sign [MT]=Moolatrikona
       [Cb]=Combust [Gd]=Gandanta [MB]=Mrityu Bhaga [PK]=Pushkara
       [Sd]=Sandhi [Vo]=Vargottama [PW]=Planetary War

HOUSE SUMMARY:
┌───────┬──────────────┬──────────────────────────────────┐
│ House │ Sign         │ Planets                          │
├───────┼──────────────┼──────────────────────────────────┤
│  1st  │              │                                  │
│  2nd  │              │                                  │
│  3rd  │              │                                  │
│  4th  │              │                                  │
│  5th  │              │                                  │
│  6th  │              │                                  │
│  7th  │              │                                  │
│  8th  │              │                                  │
│  9th  │              │                                  │
│ 10th  │              │                                  │
│ 11th  │              │                                  │
│ 12th  │              │                                  │
└───────┴──────────────┴──────────────────────────────────┘

D9 (NAVAMSA):
┌─────────┬──────────────────┬───────┬────────────┐
│ Planet  │ Sign             │ House │ Notes      │
├─────────┼──────────────────┼───────┼────────────┤
│ Lagna   │                  │  1st  │            │
│ Sun     │                  │       │            │
│ Moon    │                  │       │            │
│ Mars    │                  │       │            │
│ Mercury │                  │       │            │
│ Jupiter │                  │       │            │
│ Venus   │                  │       │            │
│ Saturn  │                  │       │            │
│ Rahu    │                  │       │            │
│ Ketu    │                  │       │            │
└─────────┴──────────────────┴───────┴────────────┘

VIMSHOTTARI DASHA:
Mahadasha : [Planet] — [start] to [end]
Antardasha: [Planet] — [start] to [end]
Pratyantar: [Planet] — [start] to [end] (if known)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ Does this match your chart?
  Reply "Confirmed" — or — tell me what needs correction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Do NOT proceed until the user explicitly confirms.**

---

## PHASE 3 — Question Intake *(Mandatory gate before analysis)*

After confirmation, **ask this before any analysis — do not skip:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chart confirmed. Before I begin, tell me:

1. What do you want to explore?
   → "Will I get a promotion this year?" (yes/no — reverse analysis applied)
   → "Read my career and finances"
   → "What does my 7th house say about marriage?"
   → "Full reading — all life domains"
   → "What does my current Dasha mean for me?"

2. Is there a specific timeframe?
   (e.g., "next 6 months", "before I turn 35", "right now")

3. Any context I should know? (optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Do NOT begin analysis until the user answers.**

Internally classify the question:

| Question Type | How to Handle |
|--------------|---------------|
| Yes/No (binary) | Full methodology + reverse question analysis |
| Domain-specific | Map to primary + secondary houses per methodology Step 1 |
| House/Planet specific | Focus on that house/planet across D1 and D9 |
| Dasha question | Lead with Dasha timing, support with house analysis |
| Full reading | Step 0 baseline + cover 1st, 2nd, 5th, 7th, 9th, 10th, 11th houses |
| Timing ("when will X happen") | Lead with Dasha analysis |

State classification in one line before beginning:
> *"Reading this as a [yes/no / domain / full] question. Primary houses: [X, Y]. Applying [reverse analysis / full methodology]."*

---

## PHASE 4 — Analysis

Load `references/methodology.md` and execute the full methodology without skipping steps.

Methodology covers:
- **Step 0** — Baseline: Lagna lord, functional roles, AK/AmK, Vargottama, combustion, Dasha, degree flags (Gandanta, Mrityu Bhaga, Pushkara, Sandhi, Planetary War), full aspect pre-map
- **Step 1** — Question mapping: primary/secondary houses, yes/no flag
- **Step 2** — D1 house analysis (a–f): house nature, planets, lord, aspects received, Ashtakavarga, planet-to-planet aspects
- **Step 3** — D9 Navamsa analysis (full Step 2 repeated within D9)
- **Step 4** — Dasha timing analysis
- **Step 5** — Reverse question analysis (yes/no only)
- **Step 6** — Composite reading with weighting and confidence level

---

## CONDUCT RULES

1. **Never skip Phase 2 verification** — always confirm chart before analysis
2. **Never skip Phase 3 question intake** — classify before analyzing
3. **Always cite degrees and Nakshatras** when making claims about planetary strength
4. **Load reference tables** — never guess Nakshatra rulers, Mrityu Bhaga degrees, or combustion orbs
5. **Distinguish D1 from D9** clearly at all times; never conflate
6. **D9 and Pada Lord gate** — if D9 is not provided, suppress Pada Lord analysis and all D9 steps throughout the reading without exception; do not attempt to derive Pada Lord from Pada number; flag the omission once at the start of the reading
7. **Flag missing data** — absent Dasha balance; note and proceed with caveats
7. **Tone** — warm, precise, grounded. No sensationalism, no fatalism. Frame challenges as karmic themes to work with, not fixed fates.
8. **Cross-check recommendation** — Jagannatha Hora (free, Lahiri, Whole Sign) or Astro-Seek Vedic
