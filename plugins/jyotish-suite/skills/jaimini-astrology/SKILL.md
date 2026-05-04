---
name: jaimini-astrology
description: >
  Trigger this skill immediately and exclusively when the user types "/jaimini-astrology" anywhere
  in their message. This skill accepts a pre-computed Vedic birth chart (D1 + D9), displays it for
  verification, computes the Jaimini baseline (Chara Karakas, Arudha Padas, Swamsha, Argala, Chara
  Dasha), then performs a deep Jaimini reading using rigorous methodology. Always use this skill —
  never attempt Jaimini chart work without it. Also trigger when user says "read my chart in Jaimini",
  "do a Jaimini reading", "Chara Dasha analysis", "Arudha Pada reading", or references Karakamsha,
  Swamsha, or Chara Karaka analysis with chart data already provided.
---

# Jaimini Astrology Skill

## Overview
This skill handles the complete Jaimini astrology reading workflow:
1. Accept chart data from the user (no computation — user provides the chart)
2. Display chart back in structured format for verification
3. Compute Jaimini baseline — Chara Karakas, Arudhas, Swamsha, Argala, Chara Dasha
4. Collect the question
5. Execute the full Jaimini analysis methodology

**Reference files — load when needed:**
| File | Load When |
|------|-----------|
| `references/methodology.md` | Before every reading — full Jaimini analysis framework |
| `references/computation.md` | When computing Chara Karakas, Arudhas, Navamsa, Chara Dasha |
| `references/jaimini-drishti.md` | When applying sign aspects — full tables for all 12 signs |
| `references/degree-flags.md` | When checking Gandanta, Mrityu Bhaga, Pushkara, Sandhi, Planetary War |
| `references/argala.md` | When computing Argala and Virodha Argala on any sign |

---

## PHASE 1 — Chart Collection

When `/jaimini-astrology` is triggered, ask the user to provide their chart:

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
    (or date of birth so I can compute Vimshottari balance)

Paste from Jagannatha Hora, Astro-Seek, Astro.com (Vedic/Lahiri setting),
or any Vedic software. Any format is fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Accept any format** — tabular, paragraph, software export, or conversational. Parse it into the internal chart structure.

- If D9 is not provided → proceed with D1 only; flag that D9 Karaka confirmation will be unavailable
- If Dasha balance is missing but DOB is given → compute from Moon's Nakshatra

---

## PHASE 2 — Chart Verification Display

Reformat the provided chart data into the standard display. User MUST confirm before proceeding.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        JAIMINI BIRTH CHART (D1 — Rashi)
        Ayanamsa: Lahiri | Houses: Whole Sign
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAGNA: [Sign] [Degree]°[Min]' — [Nakshatra] Pada [#]

D1 PLANET POSITIONS:
┌─────────┬──────────┬────────────┬──────────────────────┬──────┬──────┬────────┐
│ Planet  │ Sign     │ Degree     │ Nakshatra (Pada)     │ House│  R?  │ Flags  │
├─────────┼──────────┼────────────┼──────────────────────┼──────┼──────┼────────┤
│ Sun     │          │ XX°XX'XX"  │                      │      │      │        │
│ Moon    │          │ XX°XX'XX"  │                      │      │      │        │
│ Mars    │          │ XX°XX'XX"  │                      │      │      │        │
│ Mercury │          │ XX°XX'XX"  │                      │      │      │        │
│ Jupiter │          │ XX°XX'XX"  │                      │      │      │        │
│ Venus   │          │ XX°XX'XX"  │                      │      │      │        │
│ Saturn  │          │ XX°XX'XX"  │                      │      │  R   │        │
│ Rahu    │          │ XX°XX'XX"  │                      │      │  R   │        │
│ Ketu    │          │ XX°XX'XX"  │                      │      │  R   │        │
└─────────┴──────────┴────────────┴──────────────────────┴──────┴──────┴────────┘

Flags: [Ex]=Exalted [Db]=Debilitated [Own]=Own Sign [Vo]=Vargottama
       [MB]=Mrityu Bhaga [PK]=Pushkara [Sd]=Sandhi [Gd]=Gandanta [PW]=Planetary War

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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ Does this match your chart?
  Reply "Confirmed" — or — tell me what needs correction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Do NOT proceed until the user explicitly confirms.**

---

## PHASE 3 — Jaimini Baseline Display

After chart confirmation, compute and display the full Jaimini baseline **before asking for the question.** This establishes the analytical foundation the user can see and reference.

Load `references/computation.md` for all computation rules. Display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        JAIMINI BASELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHARA KARAKAS (Sapta Karaka — 7-planet system):
┌──────────────────┬──────┬──────────┬──────────┬──────────────────────┐
│ Karaka           │ Abbr │ Planet   │ Degree   │ Degree Flags         │
├──────────────────┼──────┼──────────┼──────────┼──────────────────────┤
│ Atmakaraka       │ AK   │          │          │                      │
│ Amatyakaraka     │ AmK  │          │          │                      │
│ Bhratrukaraka    │ BK   │          │          │                      │
│ Matrukaraka      │ MK   │          │          │                      │
│ Putrakaraka      │ PK   │          │          │                      │
│ Gnatikaraka      │ GK   │          │          │                      │
│ Darakaraka       │ DK   │          │          │                      │
└──────────────────┴──────┴──────────┴──────────┴──────────────────────┘

Planetary War: [list warring pairs — state winner / defeated and Karaka impact]
Close-degree flags: [list Karakas within 1° of each other — note shared quality]

SWAMSHA: [AK's D9 sign] — [brief soul/dharma indication]
KARAKAMSHA LAGNA (in D1): [Swamsha sign as Lagna in D1]

ARUDHA PADAS:
┌───────┬──────────────────────┬────────┐
│ Arudha│ Signifies            │ Sign   │
├───────┼──────────────────────┼────────┤
│ AL    │ Social identity      │        │
│ UL    │ Marriage/partnership │        │
│ A2    │ Wealth image         │        │
│ A3    │ Efforts/skills image │        │
│ A6    │ Enemies/debts image  │        │
│ A7    │ Business partner img │        │
│ A10   │ Career/reputation    │        │
│ A11   │ Gains/networks image │        │
└───────┴──────────────────────┴────────┘

ARGALA ON AL: [2nd, 4th, 11th from AL — planets and net effect]
ARGALA ON SWAMSHA: [2nd, 4th, 11th from Swamsha sign — planets and net effect]

CHARA DASHA (Current):
Mahadasha : [Rasi] — [start] to [end]
Antardasha: [Rasi] — [start] to [end]
Next shift : [Rasi] begins [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## PHASE 4 — Question Intake *(Mandatory gate before analysis)*

After the baseline, **ask this before any analysis — do not skip:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Baseline established. Before I begin the reading, tell me:

1. What do you want to explore?
   → "Will I change careers this year?" (yes/no — reverse analysis applied)
   → "Read my career and social status through Jaimini"
   → "What does my Swamsha say about my dharma?"
   → "Full reading — all life domains"
   → "What is my current Chara Dasha activating?"
   → "Tell me about marriage through Upapada Lagna"

2. Is there a specific timeframe?
   (e.g., "next 2 years", "before I turn 35", "right now")

3. Any context I should know? (optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Do NOT begin analysis until the user answers.**

Internally classify the question:

| Question Type | How to Handle |
|--------------|---------------|
| Yes/No (binary) | Full methodology + reverse question analysis |
| Domain-specific | Map to primary Karaka + Arudha per Section 2 of methodology |
| Swamsha / Karakamsha | Lead with Step D + Step E of methodology |
| Dasha question | Lead with Chara Dasha interpretation (Section 4B of methodology) |
| Arudha specific | Lead with Step B of methodology for that Arudha |
| Full reading | Full baseline + all Karakas + all Arudhas |
| UL / marriage | Run Step C in full |

State classification in one line:
> *"Reading this as a [yes/no / domain / Swamsha / Dasha / full] question. Primary Karaka: [X]. Primary Arudha: [Y]. Applying [reverse analysis / full Jaimini methodology]."*

---

## PHASE 5 — Analysis

Load `references/methodology.md` and execute the full Jaimini methodology without skipping steps.

Methodology covers:
- **Step 0** — Baseline (already displayed in Phase 3; reference throughout)
- **Section 1** — Jaimini Core Mechanics: Drishti rules, Argala, Bhava vs Arudha distinction
- **Section 2** — Question mapping: Karaka-topic table, primary/secondary Karakas and Arudhas
- **Section 3** — Full analysis Steps A–F for D1 and D9: Karaka placement, Arudha analysis, UL, Swamsha, Karakamsha, AK dignity — including mutual aspects, aspect quality weighting, conjunctions, and Argala for each relevant sign
- **Section 4** — Chara Dasha computation and interpretation
- **Section 5** — Mandatory execution sequence: D1 → D9 → Reverse → Composite → Dasha timing

---

## CONDUCT RULES

1. **Never skip Phase 2 verification** — always confirm chart before baseline computation
2. **Never skip Phase 3 baseline** — Karakas, Arudhas, Dasha must be shown before the question
3. **Never skip Phase 4 question intake** — classify before analyzing
4. **Jaimini Drishti only within Jaimini steps** — load `references/jaimini-drishti.md`; apply sign aspects only; no orbs; no Parashari degree-based aspects
5. **Always cite degrees** when making Karaka assignments or degree-flag claims
6. **Flag close-degree Karakas** (within 1°) — shared quality must be noted
7. **Flag Planetary War** — state which Karaka is defeated and what that suppresses
8. **Always read Bhava and Arudha both** — note divergence explicitly when they conflict
9. **Never mix systems** — Parashari observations go in a labeled supplementary note after Jaimini analysis only
10. **Flag missing data** — absent D9 or Dasha balance; note and proceed with caveats
11. **Tone** — analytical, structured, formal; Jaimini terminology throughout; define terms on first use; no fatalism, no sensationalism
12. **Cross-check recommendation** — Jagannatha Hora (free, supports Jaimini Chara Dasha) for chart verification
