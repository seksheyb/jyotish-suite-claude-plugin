---
name: bnn-astrology
description: >
  Trigger this skill immediately and exclusively when the user types "/bnn" anywhere in their message.
  This skill accepts a pre-computed Vedic birth chart (D1 + D9), displays it back for verification,
  then performs a deep BNN (Brighu Nadi Nadi) astrological reading using rigorous Nadi methodology —
  natural Karakas, sign fields, flow positions (2nd/12th), trine support (5th/9th), growth positions
  (3rd/11th), opposition (7th), Parashari aspects with degree orbs, degree flags (Mrityu Bhaga,
  Pushkara, Gandanta, Sandhi, Planetary War, combustion), and Vimshottari Dasha timing. Always use
  this skill — never attempt BNN chart work without it. Also trigger when user says "BNN reading",
  "Brighu Nadi", "Nadi reading", or references natural Karaka analysis with chart data already provided.
---

# BNN Nadi Astrology Skill

## Overview
This skill handles the complete BNN reading workflow:
1. Accept chart data from the user (no computation — user provides the chart)
2. Display D1 + D9 in structured format for verification
3. Collect the question
4. Execute the full BNN analysis methodology

**Core BNN principle:** The Sign (Rasi) dictates the field of expression. The Planet dictates the event or actor. Everything is read relative to the natural Karaka planet — not from the Lagna. Lagna is secondary context only.

**Reference files — load when needed:**
| File | Load When |
|------|-----------|
| `references/methodology.md` | Before every reading — full BNN analysis framework |
| `references/karaka-tables.md` | When identifying Karakas, sign fields, natural relationships |
| `references/degree-flags.md` | When checking Mrityu Bhaga, Pushkara, Gandanta, Sandhi, Planetary War, combustion |
| `references/aspects.md` | When computing Graha Drishti aspects, orbs, mutual aspects |

---

## PHASE 1 — Chart Collection

When `/bnn` is triggered, ask the user to provide their chart:

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

Note: BNN reads from natural Karakas (planets), not Lagna houses.
The more complete your chart data (degrees, retrograde flags), the
deeper and more precise the reading.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Accept any format** — tabular, paragraph, software export, or conversational. Parse into internal chart structure.

- If D9 is not provided → ask: *"Do you have your D9 (Navamsa) chart? It enables Vargottama detection and D9-level confirmation. Share it now, or reply 'Skip D9' to proceed with D1 only."* Wait for response.
- If user skips D9 → proceed with D1 only; suppress all D9 analysis; flag once: *"D9 not provided — Vargottama and Navamsa confirmation layer omitted."*
- If Dasha balance is missing but DOB is given → compute Vimshottari Dasha balance from Moon's Nakshatra at birth
- Degrees are critical for BNN — if the user provides only signs without degrees, flag that degree-based analysis (Mrityu Bhaga, Pushkara, aspect orbs, Planetary War) will be unavailable

---

## PHASE 2 — Chart Verification Display

Reformat the provided chart data into the standard display and show it back. User MUST confirm before proceeding.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        BNN BIRTH CHART (D1 — Rashi)
        Ayanamsa: Lahiri | Sidereal Zodiac
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAGNA: [Sign] [Degree]°[Min]'

D1 PLANET POSITIONS:
┌─────────┬──────────┬────────────┬──────┬──────┬─────────────────────────┐
│ Planet  │ Sign     │ Degree     │ House│  R?  │ Flags                   │
├─────────┼──────────┼────────────┼──────┼──────┼─────────────────────────┤
│ Sun     │          │ XX°XX'XX"  │      │      │                         │
│ Moon    │          │ XX°XX'XX"  │      │      │                         │
│ Mars    │          │ XX°XX'XX"  │      │      │                         │
│ Mercury │          │ XX°XX'XX"  │      │      │                         │
│ Jupiter │          │ XX°XX'XX"  │      │      │                         │
│ Venus   │          │ XX°XX'XX"  │      │      │                         │
│ Saturn  │          │ XX°XX'XX"  │      │  R   │                         │
│ Rahu    │          │ XX°XX'XX"  │      │  R   │                         │
│ Ketu    │          │ XX°XX'XX"  │      │  R   │                         │
└─────────┴──────────┴────────────┴──────┴──────┴─────────────────────────┘

Flags: [Ex]=Exalted [Db]=Debilitated [Own]=Own Sign [Cb]=Combust
       [Gd]=Gandanta [MB]=Mrityu Bhaga [PK]=Pushkara [Sd]=Sandhi
       [Vo]=Vargottama [PW]=Planetary War [CC]=Close Contention

SIGN LAYOUT (for BNN flow mapping):
┌───────┬──────────────┬──────────────────────────────────────┐
│ Sign  │ Field        │ Planets                              │
├───────┼──────────────┼──────────────────────────────────────┤
│ Aries │ Self/init    │                                      │
│ Tau   │ Wealth       │                                      │
│ Gem   │ Comm/sibs    │                                      │
│ Can   │ Home/mother  │                                      │
│ Leo   │ Authority    │                                      │
│ Vir   │ Service/hlth │                                      │
│ Lib   │ Partnerships │                                      │
│ Sco   │ Transform    │                                      │
│ Sag   │ Dharma/fort  │                                      │
│ Cap   │ Career/disc  │                                      │
│ Aqu   │ Gains/ntwrk  │                                      │
│ Pis   │ Liberation   │                                      │
└───────┴──────────────┴──────────────────────────────────────┘

D9 (NAVAMSA):
┌─────────┬──────────────────┬───────┬──────────────┐
│ Planet  │ Sign             │ House │ Notes        │
├─────────┼──────────────────┼───────┼──────────────┤
│ Lagna   │                  │  1st  │              │
│ Sun     │                  │       │              │
│ Moon    │                  │       │              │
│ Mars    │                  │       │              │
│ Mercury │                  │       │              │
│ Jupiter │                  │       │              │
│ Venus   │                  │       │              │
│ Saturn  │                  │       │              │
│ Rahu    │                  │       │              │
│ Ketu    │                  │       │              │
└─────────┴──────────────────┴───────┴──────────────┘

VIMSHOTTARI DASHA:
Mahadasha : [Planet] — [start] to [end]
Antardasha: [Planet] — [start] to [end]
Pratyantar: [Planet] — [start] to [end] (if known)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ Does this match your chart?
  Reply "Confirmed" — or — tell me what needs correction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Note the **Sign Layout table** — this is unique to BNN. Because BNN reads relative to Karakas by sign (not by Lagna house), having all 12 signs mapped with their occupying planets is the primary working reference. Fill it completely.

**Do NOT proceed until the user explicitly confirms.**

---

## PHASE 3 — Question Intake *(Mandatory gate before analysis)*

After confirmation, **ask this before any analysis — do not skip:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chart confirmed. Before I begin the BNN reading, tell me:

1. What do you want to explore?
   → "Will I get a promotion this year?" (yes/no — reverse analysis applied)
   → "Read my career and professional growth"
   → "What does BNN say about my marriage prospects?"
   → "Full reading — all life domains"
   → "What is my current Dasha activating in BNN terms?"
   → "Read Venus as the Karaka for relationships"

2. Is there a specific timeframe?
   (e.g., "next 2 years", "before I turn 35", "right now")

3. Any context I should know? (optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Do NOT begin analysis until the user answers.**

Internally classify before proceeding:

| Question Type | How to Handle |
|--------------|---------------|
| Yes/No (binary) | Full methodology + reverse question analysis (opposite Karaka) |
| Domain-specific | Identify primary + secondary Karakas from `references/karaka-tables.md` |
| Specific Karaka | Lead with that Karaka through all Steps A–F |
| Dasha question | Lead with Section 4 Dasha analysis, then BNN position of Dasha lord |
| Full reading | Run all major Karakas: Sun, Moon, Jupiter/Venus (per gender), Saturn, Mars |
| Timing ("when will X happen") | Lead with Dasha activation, identify which period activates the Karaka |

State classification in one line before beginning:
> *"Reading this as a [yes/no / domain / full] question. Primary Karaka: [Planet] as [signification]. Secondary Karaka: [Planet]. Applying [reverse analysis / full BNN methodology]."*

---

## PHASE 4 — Analysis

Load `references/methodology.md` and execute the full BNN methodology without skipping steps.

The methodology covers:

**Section 1 — Reference tables** (load `references/karaka-tables.md`):
- 1A: Natural Karaka table — 9 planets with primary and secondary significations
- 1B: Sign field table — 12 signs with domain definitions
- 1C: Natural planet relationships — friendship/neutral/enemy for all 9 planets
- 1D: Degree and strength flags — combustion, Gandanta, Mrityu Bhaga, Pushkara, Sandhi, Planetary War (load `references/degree-flags.md`)
- 1E: Parashari aspects in BNN — aspect rules, orb framework, mutual aspects, empty sign rule (load `references/aspects.md`)

**Section 2 — BNN Analysis Steps A–F** (relative to the Karaka, not Lagna):
- Step A: Karaka sign field + dignity + retrograde + degree flags + aspects received
- Step B: Conjunctions in Karaka's sign — signification, relationship, degree flags
- Step C: Flow positions (2nd/12th) — occupants + aspects received + degree flags
- Step D: Trine support (5th/9th) — occupants + aspects received + degree flags
- Step E: Growth positions (3rd/11th) — occupants + aspects received + degree flags
- Step F: Opposition (7th) — occupants + aspects received + degree flags + mutual aspect check

**Section 3 — D9 BNN Analysis**: Full Steps A–F within D9; Vargottama flag; D9 confirmation/contradiction logic

**Section 4 — Dasha Timing**: Mahadasha/Antardasha Karaka relationship + degree flags on Dasha lord + BNN position of Dasha lord

**Section 5 — Execution Sequence**: D1 → D9 → Reverse (yes/no only) → Composite (10-level priority) → Confidence level

---

## CONDUCT RULES

1. **Never skip Phase 2 verification** — always confirm chart before analysis
2. **Never skip Phase 3 question intake** — classify the question and state the Karaka before analyzing
3. **Never read from Lagna in BNN steps** — all positions (2nd, 12th, 5th, 9th, etc.) are counted from the Karaka's sign, not from Lagna; if Lagna-based analysis is mentioned, label it "Supplementary (Parashari)" and keep it after BNN analysis
4. **Always load `references/aspects.md`** before computing aspects — never guess aspect rules or omit the empty-sign aspect check
5. **Always load `references/degree-flags.md`** before checking Mrityu Bhaga, Pushkara, combustion — never guess degree values
6. **Degrees are required for full analysis** — if degrees are missing, flag explicitly which steps are unavailable (aspect orbs, Planetary War, Mrityu Bhaga, Pushkara)
7. **D9 gate** — if D9 not provided, suppress all D9 steps; flag once; never conflate D1 and D9
8. **State the Karaka before every step** — BNN is Karaka-relative; always make clear which planet is the reference point
9. **Apply degree flags to every planet encountered** — Karaka, conjuncts, flow positions, trine positions, growth positions, opposition, aspecting planets — none are exempt
10. **Tone** — analytical, structured, formal; use BNN terminology (Karaka, flow position, trine support, sign field, Naisargika significator); define terms on first use; no fatalism, no sensationalism
11. **Cross-check recommendation** — Jagannatha Hora (free, Lahiri ayanamsha) or Astro-Seek Vedic for chart verification
