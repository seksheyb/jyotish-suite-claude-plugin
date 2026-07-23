# Orchestration Notes — Jaimini

Interpretive guidance for the wave orchestrator and its workers. Deterministic
computation (Chara Karakas, Arudhas, Swamsha, Argala, Chara Dasha, the Jaimini
drishti map) is produced by `scripts/compute_jaimini_baseline.py` and verified
against `references/computation.md`. The methodology workers apply lives in
`references/methodology.md`; this file holds the question-routing logic and
the cross-cutting conduct rules that used to sit in SKILL.md.

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
  • Current Chara Dasha or Vimshottari Mahadasha, if you have it

Option 2 — give birth data:
  • Date, exact time, and place of birth

Degrees matter — Chara Karaka ranking, Arudhas, Swamsha and the degree
flags all need them. The D9 is derived automatically; you don't need to
paste it.

Paste from Jagannatha Hora, Astro-Seek, Astro.com (Vedic/Lahiri), or any
Vedic software. Any format is fine.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

`chart-verifier` parses a pasted chart (via `chart_io.py`) or renders a computed
one, then produces the **Chart Verification Display** below — the D1/D9 tables
and flag legend only. It does **not** render the Jaimini baseline block: the
Karakas, Swamsha, Arudhas, Argala and Chara Dasha do not exist until
`baseline-runner` computes them (Wave 0 step 3), so they are rendered separately
at Wave 0 step 4 from the baseline JSON — see **Jaimini Baseline Display** below.

---

## Question Intake Prompt (for Phase B)

Only **after** the Jaimini baseline is displayed, ask this — do not skip:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Baseline established. Before I begin the reading, tell me:

1. What do you want to explore?
   → "Will I change careers this year?"  (yes/no — reverse analysis applied)
   → "Read my career and social status through Jaimini"  (domain)
   → "What does my Swamsha say about my dharma?"  (Swamsha)
   → "Full reading — all life domains"   (full)
   → "What is my current Chara Dasha activating?"  (Dasha)
   → "Tell me about marriage through Upapada Lagna"  (Arudha-specific)

2. Is there a specific timeframe?
   (e.g. "next 2 years", "before I turn 35", "right now")

3. Any context I should know? (optional)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Do not begin Wave 1 until the user answers. Then classify per the table below.

---

## Question Classification

After the baseline is shown, classify the user's question before fanning out
Wave 1. State the classification in one line to the user:

> *"Reading this as a [yes/no / domain / Swamsha / Dasha / full] question.
> Primary Karaka: [X]. Primary Arudha: [Y]. Applying [reverse analysis / full
> Jaimini methodology]."*

| Question Type | How to Handle | Wave 1 dispatch |
|--------------|---------------|--------------|
| Yes/No (binary) | Full methodology + reverse question analysis | D1 + D9 + reverse-question analyst (all medium); Chara-Dasha-timeline analyst if a timeframe is in play |
| Domain-specific | Map to primary Karaka + Arudha per Section 2 of methodology | D1 + D9 analyst, each scoped to the topic's Karaka/Arudha/secondaries |
| Swamsha / Karakamsha (narrow, single-Karaka) | Lead with Step D + Step E of methodology | **Inline, zero agents** — answer directly from the baseline |
| Dasha question | Lead with Chara Dasha interpretation (Section 4B) | Chara-Dasha-timeline analyst + D1/D9 analysts scoped to the activated Karakas/Arudhas |
| Arudha specific | Lead with Step B of methodology for that Arudha | D1 + D9 analyst scoped to that Arudha + its lord (+ DK if marriage) |
| Full reading | Full baseline + all Karakas + all Arudhas | All four: D1 analyst (all 7 Karakas + 8 Arudhas) + D9 analyst (same) + reverse-question analyst (if yes/no) + Chara-Dasha-timeline analyst |
| UL / marriage | Run Step C in full | D1 + D9 analyst scoped to UL, A7, DK, 7th Bhava |

D1 and D9 analysts always run together (never D9 alone); the
Chara-Dasha-timeline and reverse-question analysts are conditional per the
table above. See SKILL.md Wave 1 for the dispatch table and the dasha-lord
coverage rule.

Topic-to-unit mapping (from methodology Section 2):

| Topic | Primary Karaka | Primary Arudha | Secondary |
|-------|---------------|----------------|-----------|
| Career | AmK | A10 | AK, Karakamsha |
| Marriage/Spouse | DK | UL, A7 | 7th Bhava |
| Finance | AK | AL, A2, A11 | AmK |
| Children | PK | A5 | 5th Bhava |
| Health | GK | A6 | 6th Bhava |
| Mother | MK | A4 | 4th Bhava |
| Siblings | BK | A3 | 3rd Bhava |
| Spirituality | AK | Swamsha | Karakamsha |
| Social Status | — | AL | 1st Bhava |
| Enemies | GK | A6 | 6th Bhava |

A full reading scopes the D1/D9 analysts to all 7 Karakas + 8 Arudhas; a
domain question narrows each to the 2-4 Karakas/Arudhas in the table above.

---

## D9 (Navamsa) — always derived, no need to ask

The D9 is computed **deterministically from the D1 planetary degrees**. Both
`chart-calculator` (computed chart) and `chart_io.py` (pasted chart) always
produce the D9 alongside the D1, and `compute_jaimini_baseline.py` carries it —
the D9 is what Swamsha and Karakamsha are read from. So:

- **Never ask the user for a separate D9 chart.** If the user *does* supply
  one, `chart-verifier` cross-checks it against the derived D9 and flags any
  discrepancy — it does not replace the derived values.
- The `unit-analyzer` workers always run the full D9 layer (Swamsha,
  Karakamsha, D9 Karaka confirmation) — D9 is never absent.
- **The one real gate is degrees.** The D9, Swamsha, Karakamsha and every
  degree flag need each planet's **degree within sign**. If a pasted chart
  gives signs only (no degrees), flag once at the start: *"Planetary degrees
  not provided — Navamsa, Swamsha/Karakamsha and degree-flag analysis are
  limited; share degrees for a full reading."*

---

## Chart Verification Display *(Wave 0 step 2 — `chart-verifier`)*

`chart-verifier` renders the confirmed chart into exactly this layout — the D1
table, the flag legend, then the D9 table. **No Jaimini baseline block appears
here** (Karakas, Swamsha, Arudhas, Argala and Chara Dasha are not yet computed
at this step). The orchestrator shows this, waits for the user to reply
"Confirmed", and only then runs `baseline-runner`.

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
│ Sun … Ketu — one row per planet                                                │
└─────────┴──────────┴────────────┴──────────────────────┴──────┴──────┴────────┘

Flags: [Ex]=Exalted [Db]=Debilitated [Own]=Own Sign [Vo]=Vargottama
       [MB]=Mrityu Bhaga [PK]=Pushkara [Sd]=Sandhi [Gd]=Gandanta [PW]=Planetary War

D9 (NAVAMSA):
┌─────────┬──────────────────┬───────┬────────────┐
│ Planet  │ Sign             │ House │ Notes      │
├─────────┼──────────────────┼───────┼────────────┤
│ Lagna   │                  │  1st  │            │
│ Sun … Ketu — one row per planet                  │
└─────────┴──────────────────┴───────┴────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ Does this match your chart?
  Reply "Confirmed" — or — tell me what needs correction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Do not run `baseline-runner` until the user explicitly confirms this chart.

---

## Jaimini Baseline Display *(Wave 0 step 4 — from `baseline-runner` JSON)*

**After** the chart is confirmed and `baseline-runner` has produced the baseline
JSON (step 3), the orchestrator renders this block directly from that JSON — it
is never computed inline and never shown before step 3. Every value below reads
straight out of `baseline.json`; degree flags on each Karaka come from
`chara_karakas[*].degree_flags`, the running Antardasha from
`chara_dasha.running.running_antardasha`.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
              JAIMINI BASELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CHARA KARAKAS (Sapta Karaka — 7-planet system):
┌──────────────────┬──────┬──────────┬──────────┬──────────────────────┐
│ Karaka           │ Abbr │ Planet   │ Degree   │ Degree Flags         │
├──────────────────┼──────┼──────────┼──────────┼──────────────────────┤
│ Atmakaraka       │ AK   │          │          │                      │
│ Amatyakaraka … Darakaraka — one row per Karaka (AK, AmK, BK, MK, PK,  │
│ GK, DK)                                                               │
└──────────────────┴──────┴──────────┴──────────┴──────────────────────┘

Planetary War: [warring pairs — winner / defeated and Karaka impact]
Close-degree flags: [Karakas within 1° of each other — shared quality]

SWAMSHA: [AK's D9 sign] — [brief soul/dharma indication]
KARAKAMSHA LAGNA (in D1): [Swamsha sign as Lagna in D1]

ARUDHA PADAS:
┌───────┬──────────────────────┬────────┐
│ Arudha│ Signifies            │ Sign   │
├───────┼──────────────────────┼────────┤
│ AL    │ Social identity      │        │
│ UL … A11 — one row per Arudha (AL, UL, A2, A3, A6, A7, A10, A11)      │
└───────┴──────────────────────┴────────┘

ARGALA ON AL: [2nd, 4th, 11th from AL — planets and net effect]
ARGALA ON SWAMSHA: [2nd, 4th, 11th from Swamsha sign — planets and net effect]

CHARA DASHA (Current):
  Mahadasha  : [Rasi] — [start] to [end]
  Antardasha : [Rasi] — [start] to [end]
  Next shift : [Rasi] begins [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Show this baseline, then proceed to Phase B (question intake). Do not proceed to
Wave 1 until the user has been shown the baseline and has answered the question.

---

## Conduct Rules (apply across all waves)

1. **Never skip chart verification** — Wave 0's `chart-verifier` output must be
   confirmed by the user before `baseline-runner` runs.
2. **Never skip the baseline display** — Chara Karakas, Arudhas, Swamsha, and
   Chara Dasha must be shown before the question is asked.
3. **Never skip question intake** — classify before dispatching Wave 1.
4. **Jaimini Drishti only** — workers apply sign aspects only; no orbs, no
   Parashari degree-based aspects within Jaimini steps. The baseline JSON
   carries the 12×12 drishti map; workers read it, never recompute it.
5. **Always cite degrees** when stating Karaka assignments or degree-flag claims
   (degrees come from the baseline JSON).
6. **Flag close-degree Karakas** (within 1°) — shared quality must be noted by
   the worker handling each affected Karaka.
7. **Flag Planetary War** — the worker for a defeated Karaka states which Karaka
   is defeated and what it suppresses.
8. **Always read Bhava and Arudha both** — note divergence explicitly when they
   conflict; this is a synthesizer responsibility at composite time.
9. **Never mix systems** — Parashari observations go only in a labeled
   supplementary note after the Jaimini analysis.
10. **Flag missing data** — the D9 is always derived (see the D9 note above),
    so the real gates are missing **degrees** or absent Dasha balance: note
    and proceed with caveats.
11. **Tone** — analytical, structured, formal; Jaimini terminology throughout;
    define terms on first use; no fatalism, no sensationalism.
12. **Cross-check recommendation** — Jagannatha Hora (free, supports Jaimini
    Chara Dasha) for chart verification.

---

## Wave-to-Methodology Map

| Wave | Methodology section | Owner |
|------|--------------------|-------|
| Wave 0 baseline | Step 0 (0A–0F) — Karakas, Swamsha, Karakamsha, Arudhas, Argala pre-map, Chara Dasha | `baseline-runner` (sidecar) |
| Wave 1 — D1 analyst | Section 1 (core mechanics), Section 2 (mapping), Section 3 Steps A–F on D1 data | `unit-analyzer` (medium) |
| Wave 1 — D9 analyst | Section 3 Steps A–F on D9 data, Step D (Swamsha), Step E (Karakamsha) | `unit-analyzer` (medium) |
| Wave 1 — reverse-question analyst | Section 5 Step 5 (yes/no questions only) | `unit-analyzer` (medium) |
| Wave 1 — Chara-Dasha-timeline analyst | Section 4A/4B, Step 7 | `unit-analyzer` (medium) |
| Wave 2 synthesis | Section 4B (Dasha interpretation), Section 5 (execution sequence, composite priority, Dasha timing output) | single `synthesizer` (opus, high) |

The synthesizer executes the mandatory sequence: D1 → D9 → reverse check
(yes/no only) → composite reading (priority order in methodology Section 5) →
Chara Dasha timing output. It only runs after the explicit Wave 1 barrier —
every dispatched unit-analyzer must have returned first.
