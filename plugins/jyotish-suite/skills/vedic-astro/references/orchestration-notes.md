# Orchestration Notes — Vedic Astro (Classical Parashari)

Interpretive guidance moved out of SKILL.md when the skill became a wave
orchestrator. Wave-1 `unit-analyzer` and Wave-2 `synthesizer` workers load
this alongside `methodology.md`.

---

## Question Classification → Reading Mode

Classify the user's question before dispatching Wave 1. The classification
decides which houses to fan out (or whether to skip Wave 1 entirely) and
which synthesis path the `synthesizer` runs.

| Question Type | How to Handle | Wave 1 dispatch |
|--------------|---------------|------------------|
| Yes/No (binary) | Full methodology + reverse question analysis (methodology Step 5) | D1 + D9 house analysts, dasha-timing analyst, **and** reverse-question analyst — all in the same wave |
| Domain-specific | Map to primary + secondary houses per methodology Step 1 table | D1 + D9 house analysts (scoped to those houses) + dasha-timing analyst |
| House/Planet specific | Focus on that house/planet across D1 and D9 | **Zero dispatch** — a single house/planet is trivially narrow; analyze inline in the orchestrator from `baseline.json` (see SKILL.md's conditional-dispatch rule) |
| Dasha question | Lead with Dasha timing (Step 4), support with house analysis | D1 + D9 house analysts (question-relevant houses) + dasha-timing analyst |
| Full reading | Step 0 baseline + cover 1st, 2nd, 5th, 7th, 9th, 10th, 11th houses | One D1 + one D9 analyst per life-domain cluster (see SKILL.md Wave 1) + dasha-timing analyst |
| Timing ("when will X happen") | Lead with Dasha analysis (Step 4) | Dasha-timing analyst leads; D1 + D9 analysts scoped to the question's houses support it |

State the classification in one line before Wave 1 begins (or before the
inline analysis, for the House/Planet-specific case):
> *"Reading this as a [yes/no / domain / full / house-specific] question.
> Primary houses: [X, Y]. Applying [reverse analysis / full methodology /
> inline single-house analysis]."*

For a **full life reading**, the ~7 core houses (1, 2, 5, 7, 9, 10, 11) are
grouped into the four life-domain clusters in SKILL.md's Wave 1 section
(Career + Wealth, Relationships + Children, Health + Obstacles, Dharma) — one
D1-house analyst and one D9-house analyst per cluster, not one worker per
house. A **domain question** narrows to the primary + secondary houses from
the Quick House Reference in `methodology.md` Step 1. A **house/planet-specific
question** dispatches nothing — there is no independent parallel work for a
single house, so it is cheaper and just as accurate to reason it through
directly in the orchestrator.

The `dasha-timing` analyst is dispatched for **every** mode above except the
inline single-house case — dasha activation is the synthesizer's #1 weighting
factor (methodology Step 6) regardless of what the question is about.

---

## D9 (Navamsa) — always derived, no need to ask

The D9 is computed **deterministically from the D1 planetary degrees**. Both
`chart-calculator` (computed chart) and `chart_io.py` (pasted chart) always
produce the D9 alongside the D1, and `compute_vedic_baseline.py` carries it. So:

- **Never ask the user for a separate D9 chart.** If the user *does* supply
  one, `chart-verifier` cross-checks it against the derived D9 and flags any
  discrepancy — it does not replace the derived values.
- The `unit-analyzer` workers always run the full D9 layer (methodology
  Step 3) and derive each planet's **Pada Lord** as the lord of its D9 sign.
  Never derive Pada Lord from the Pada number alone.
- **The one real gate is degrees.** D9, Nakshatra, Pada and every degree flag
  need each planet's **degree within sign**. If a pasted chart gives signs
  only (no degrees), flag once at the start: *"Planetary degrees not provided
  — Navamsa, Nakshatra/Pada and degree-flag analysis are limited; share
  degrees for a full reading."*
- **This is the one condition under which Wave 1's D9-house analyst is
  waived** (SKILL.md Wave 1): with no degrees there is no reliable D9 sign to
  analyze. Skip that track entirely rather than dispatching it on guessed
  data; the synthesizer omits Step 3/D9 confirmation and states the caveat
  above instead.

---

## Conduct Rules (apply across all waves)

1. **Never skip chart verification.** Wave 0 must show the rendered chart and
   get explicit user confirmation before Wave 1 dispatches.
2. **Never skip question intake.** Classify the question before analyzing.
3. **Always cite degrees and Nakshatras** when making claims about planetary
   strength — the baseline JSON carries these; workers must quote them.
4. **Trust the baseline.** Deterministic facts (degree flags including
   planetary war, dignity, the as-of Vimshottari dasha, chara karakas,
   Ashtakavarga, the D1 + D9 aspect maps and the full D9 sub-chart) are
   pre-computed by the sidecar. Workers do not recompute them; they
   interpret them.
5. **Distinguish D1 from D9** clearly at all times; never conflate the two.
6. **Flag missing data** — e.g. absent dasha balance — and proceed with
   caveats rather than guessing.
7. **Tone** — warm, precise, grounded. No sensationalism, no fatalism. Frame
   challenges as karmic themes to work with, not fixed fates.
8. **Cross-check recommendation** — when relevant, point the user to
   Jagannatha Hora (free, Lahiri, Whole Sign) or Astro-Seek Vedic to
   independently verify the chart.

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
  (Degrees matter — Nakshatra, Navamsa and degree-flags need them.
   D9 is derived automatically; you don't need to paste it.)

Option 2 — give birth data:
  • Date, exact time, and place of birth

Paste from Jagannatha Hora, Astro-Seek, Astro.com (Vedic/Lahiri),
or any Vedic software. Any format is fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Accept any format — tabular, paragraph, software export, or conversational.
The `chart-verifier` agent parses a pasted chart (via `chart_io.py`) or renders
a computed one, then produces the verification display below.

---

## Question Intake Prompt (for Phase A)

After the chart is confirmed, ask this before any analysis — do not skip:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chart confirmed. Before I begin, tell me:

1. What do you want to explore?
   → "Will I get a promotion this year?"  (yes/no — reverse analysis applied)
   → "Read my career and finances"        (domain)
   → "What does my 7th house say about marriage?"  (house-specific)
   → "Full reading — all life domains"    (full)
   → "What does my current Dasha mean for me?"     (dasha)

2. Is there a specific timeframe?
   (e.g. "next 6 months", "before I turn 35", "right now")

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
        VEDIC BIRTH CHART (D1 — Rashi)
        Ayanamsa: Lahiri | Houses: Whole Sign
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAGNA: [Sign] [Deg]°[Min]' — [Nakshatra] Pada [#]

D1 PLANET POSITIONS:
┌─────────┬──────────┬────────────┬──────────────────────┬──────┬──────┬───────┐
│ Planet  │ Sign     │ Degree     │ Nakshatra (Pada)     │ House│  R?  │ Flags │
├─────────┼──────────┼────────────┼──────────────────────┼──────┼──────┼───────┤
│ Sun … Ketu — one row per planet                                              │
└─────────┴──────────┴────────────┴──────────────────────┴──────┴──────┴───────┘

Flags: [Ex]=Exalted [Db]=Debilitated [Own]=Own Sign [MT]=Moolatrikona
       [Cb]=Combust [Gd]=Gandanta [MB]=Mrityu Bhaga [PK]=Pushkara
       [Sd]=Sandhi [Vo]=Vargottama [PW]=Planetary War

HOUSE SUMMARY: 12 rows — house, sign, planets in it.

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
