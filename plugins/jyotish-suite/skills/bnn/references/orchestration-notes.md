# BNN Orchestration Notes

Interpretive rules that govern how a BNN reading is conducted and assembled.
Workers (`unit-analyzer`, `synthesizer`) and `chart-verifier` load this
alongside `methodology.md`. Moved here from the former SKILL.md so the skill
stays a lean orchestrator while no interpretive content is lost.

---

## Core BNN Principle

The Sign (Rasi) dictates the **field of expression**. The Planet dictates the
**event or actor**. Everything is read relative to the natural Karaka planet —
**never from the Lagna**. Lagna is secondary context only. Every BNN position
(2nd, 12th, 5th, 9th, 3rd, 11th, 7th) is counted **by sign from the Karaka's
sign**, not from Lagna. If any Lagna-based observation is offered, label it
"Supplementary (Parashari)" and keep it after the BNN analysis.

---

## Chart Intake Format (for Phase A)

Use this prompt to ask the user for a chart:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Please share your Vedic birth chart — OR your birth details and I'll
compute it.

Option 1 — paste a pre-computed chart:
  • Lagna — sign and degree
  • Each planet — sign, degree, house (retrograde if known)
  • Current Mahadasha + Antardasha with dates, if you have them

Option 2 — give birth data:
  • Date, exact time, and place of birth

Note: BNN reads from natural Karakas (planets), not Lagna houses. Degrees
matter — Mrityu Bhaga, Pushkara, aspect orbs and Planetary War all need
them. D9 is derived automatically; you don't need to paste it.

Paste from Jagannatha Hora, Astro-Seek, Astro.com (Vedic/Lahiri), or any
Vedic software. Any format is fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Accept any format — tabular, paragraph, software export, or conversational.
`chart-verifier` parses a pasted chart (via `chart_io.py`) or renders a computed
one, then produces the verification display below.

---

## D9 (Navamsa) — always derived, no need to ask

The D9 is computed **deterministically from the D1 planetary degrees**. Both
`chart-calculator` (computed chart) and `chart_io.py` (pasted chart) always
produce the D9 alongside the D1, and `compute_bnn_baseline.py` carries it. So:

- **Never ask the user for a separate D9 chart.** If the user *does* supply
  one, `chart-verifier` cross-checks it against the derived D9 and flags any
  discrepancy.
- The `unit-analyzer` workers always run the full D9 BNN layer (methodology
  Section 3) — Steps A–F within D9, the Vargottama flag, and D9
  confirmation/contradiction logic.
- **The one real gate is degrees.** D9, Vargottama, Mrityu Bhaga, Pushkara,
  aspect orbs and Planetary War all need each planet's **degree within sign**.
  If a pasted chart gives signs only, flag once: *"Planetary degrees not
  provided — Navamsa, degree flags and aspect-orb analysis are limited; share
  degrees for a full reading."*

---

## Question Classification

Classify the question before any analysis. State the classification in one line:
> *"Reading this as a [yes/no / domain / full] question. Primary Karaka:
> [Planet] as [signification]. Secondary Karaka: [Planet]. Applying
> [reverse analysis / full BNN methodology]."*

| Question Type | How to Handle |
|--------------|---------------|
| Yes/No (binary) | Full methodology + reverse question analysis (opposite Karaka) |
| Domain-specific | Identify primary + secondary Karakas from `karaka-tables.md` 1A |
| Specific Karaka | Lead with that Karaka through all Steps A–F |
| Dasha question | Lead with Section 4 Dasha analysis, then BNN position of Dasha lord |
| Full reading | Run all major Karakas: Sun, Moon, Jupiter/Venus (per gender), Saturn, Mars |
| Timing ("when will X") | Lead with Dasha activation; identify which period activates the Karaka |

For a full reading the Karaka set is gender-sensitive: marriage Karaka is Venus
for male charts and Jupiter for female charts (see `karaka-tables.md` 1A).

---

## Question Intake Prompt (for Phase A)

After the chart is confirmed, ask this before any analysis — do not skip:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chart confirmed. Before I begin the BNN reading, tell me:

1. What do you want to explore?
   → "Will I get a promotion this year?"  (yes/no — reverse analysis applied)
   → "Read my career and professional growth"   (domain)
   → "What does BNN say about my marriage prospects?"  (domain)
   → "Full reading — all life domains"    (full)
   → "What is my current Dasha activating in BNN terms?"  (dasha)
   → "Read Venus as the Karaka for relationships"  (specific Karaka)

2. Is there a specific timeframe?
   (e.g. "next 2 years", "before I turn 35", "right now")

3. Any context I should know? (optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Do not begin analysis until the user answers. Then classify per the table above.

---

## Verification Display Format

`chart-verifier` renders the confirmed chart into exactly this layout. The
orchestrator shows it and waits for the user to reply "Confirmed".

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        BNN BIRTH CHART (D1 — Rashi)
        Ayanamsa: Lahiri | Sidereal Zodiac
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAGNA: [Sign] [Deg]°[Min]'

D1 PLANET POSITIONS:
┌─────────┬──────────┬────────────┬──────┬──────┬─────────────────────────┐
│ Planet  │ Sign     │ Degree     │ House│  R?  │ Flags                   │
├─────────┼──────────┼────────────┼──────┼──────┼─────────────────────────┤
│ Sun … Ketu — one row per planet                                          │
└─────────┴──────────┴────────────┴──────┴──────┴─────────────────────────┘

Flags: [Ex]=Exalted [Db]=Debilitated [Own]=Own Sign [Cb]=Combust
       [Gd]=Gandanta [MB]=Mrityu Bhaga [PK]=Pushkara [Sd]=Sandhi
       [Vo]=Vargottama [PW]=Planetary War [CC]=Close Contention

SIGN LAYOUT (BNN's primary working table — fill completely):
All 12 signs with their field label and occupying planets — see the Sign
Layout Working Reference below. BNN reads relative to Karakas by sign, so this
table, not a Lagna house grid, is the working reference.

D9 (NAVAMSA): Lagna sign + each planet's D9 sign (derived from D1 degrees).

VIMSHOTTARI DASHA:
  Mahadasha  : [Planet] — [start] to [end]
  Antardasha : [Planet] — [start] to [end]
  Pratyantar : [Planet] — [start] to [end]  (if known)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ Does this match your chart?
  Reply "Confirmed" — or tell me what needs correction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Do **not** proceed to Wave 1 until the user explicitly confirms.

---

## Conduct Rules (interpretive)

1. **Never read from Lagna in BNN steps** — all positions are counted from the
   Karaka's sign. Lagna-based notes go last, labelled "Supplementary (Parashari)".
2. **State the Karaka before every step** — BNN is Karaka-relative; always make
   clear which planet is the reference point.
3. **Apply degree flags to every planet encountered** — Karaka, conjuncts, flow
   positions, trine positions, growth positions, opposition, and aspecting
   planets. No planet is exempt. (The baseline sidecar pre-computes these; the
   worker applies them interpretively.)
4. **Never omit the empty-sign aspect check** — a position is not "empty" until
   both occupants and aspects have been checked (see `aspects.md`).
5. **D9 is always derived** from D1 degrees (see above) — always run the D9
   layer; never conflate D1 and D9.
6. **Degrees required for full analysis** — if degrees are missing, flag
   explicitly which steps are unavailable (aspect orbs, Planetary War, Mrityu
   Bhaga, Pushkara).
7. **Tone** — analytical, structured, formal; use BNN terminology (Karaka, flow
   position, trine support, sign field, Naisargika significator); define terms
   on first use; no fatalism, no sensationalism.
8. **Cross-check recommendation** — Jagannatha Hora (free, Lahiri ayanamsha) or
   Astro-Seek Vedic for chart verification.

---

## Sign Layout Working Reference

Because BNN reads relative to Karakas by sign (not by Lagna house), a complete
12-sign map with each sign's occupying planets is the primary working reference.
`chart-verifier` fills it completely. Field labels per sign:

| Sign | Field |
|------|-------|
| Aries | Self / initiative |
| Taurus | Wealth |
| Gemini | Communication / siblings |
| Cancer | Home / mother |
| Leo | Authority |
| Virgo | Service / health |
| Libra | Partnerships |
| Scorpio | Transformation |
| Sagittarius | Dharma / fortune |
| Capricorn | Career / discipline |
| Aquarius | Gains / network |
| Pisces | Liberation |

Full domain definitions: `karaka-tables.md` Section 1B.
