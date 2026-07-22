# Lal Kitab — Orchestration & Interpretive Notes

Methodology context for the wave orchestrator and its workers. The deterministic
computation (fixed-house re-map, pakka ghar, sleeping check, six rins, teva,
varshphal table, four-signal timing engine) now lives in
`scripts/compute_lalkitab_baseline.py`. This file holds the interpretive and
routing guidance that used to sit inline in `SKILL.md`.

---

## Hard methodological lines (enforce in every reading)

1. **Houses are fixed to signs.** Aries = always 1st, Taurus = always 2nd, …
   Pisces = always 12th. Lagna sign is noted as flavour but house numbers never
   rotate.
2. **Dignity is by house number, not sign.** Sun is exalted in *house 1* (not in
   Aries the sign). Pakka ghar governs full results. Use Lal Kitab tables only —
   never Parashari dignity tables.
3. **No D9, no divisional charts.** If the user supplies a D9, display it but
   exclude it from analysis with an explicit note — Lal Kitab is a single-chart
   system and its logic breaks if mixed with divisional methods.
4. **No Nakshatras, no Vimshottari Dasha.** Those are Parashari. Lal Kitab uses
   the age-based Varshphal table only. Mention this only if the user asks why.
5. **Lal Kitab aspects only** (see `aspects.md`). Never import Parashari 7th-house
   or special Mars/Jupiter/Saturn aspects.
6. **Every upaay must cite a Farman.** No invented remedies. Modern adaptations
   are flagged `[Modern Tradition — …]` and ranked lower.
7. **Sleeping planets give zero results until awakened.** State this plainly; do
   not soften it with Vedic dignity reasoning.
8. **No mixing of systems mid-reading.** If the user asks "but in KP / BNN /
   Jaimini…", redirect to those skills — do not blend.
9. **Be honest about ambiguity.** Where Farmans conflict or are cryptic, say so.
   Do not fabricate certainty.
10. **Ancestor lineage:** cite Pt. Roop Chand Joshi's volumes only. Modern
    commentaries (Arun Sanhita, U.C. Mahajan, etc.) are flagged as such, never
    stated as authoritative.
11. **Timing is probabilistic, never deterministic.** The four-signal convergence
    engine outputs year-windows with probability tiers, never specific dates.
    Single-signal timing calls are prohibited. Every timing window must be paired
    with the upaay that activates or stabilizes it. For date-precision, redirect
    to KP horary.
12. **Intent capture is pre-baseline, not pre-diagnostic.** Phase 0 captures
    intent BEFORE chart collection, but the full deterministic baseline always
    runs. Intent only *tilts narration emphasis* and *pre-routes the mode menu* —
    it never skips diagnostic steps. A user asking "when will I marry" still
    receives full pakka ghar, sleeping, rin, and teva diagnostics; what changes
    is which configurations get highlighted in the narration.

---

## Phase 0 — Intent capture rules

When `/lal-kitab` triggers, before asking for the chart, present the intent
prompt (see SKILL.md Phase 0). Then:

1. **Store the intent** as `user_intent` — passed to the baseline runner and to
   every Wave-1 worker so narration tilts consistently.
2. **The baseline ALWAYS runs in full.** Intent does not skip phases.
3. **Mode pre-routing.** If intent maps cleanly to one Mode A–F, mark it as the
   *suggested* mode. Phase A then asks for confirmation rather than presenting
   the full menu: "Based on what you asked, I'd run Mode F (event timing for
   '[event]'). Confirm, or pick a different mode?"
4. **Ambiguous intent → default behaviour.** If the user picks "not sure" or
   gives unclear input, present the full mode menu.
5. **Honesty rule.** If intent suggests something the chart can't cleanly answer
   (e.g. "tell me my exact death date"), state the boundary in Phase 0 itself
   and offer the closest legitimate read.

### Intent-driven narration tilting

Pass these emphasis cues to Wave-1 workers based on the user's question:

| User Intent Signals | Workers Should Emphasize |
|---------------------|--------------------------|
| Marriage / partnership / relationship | Venus condition, 7th & 2nd houses, Stri Rin, Sukhi vs Dukhi teva |
| Career / job / promotion | Sun + Saturn condition, 10th & 6th houses, Pitri Rin, Rajyogi vs Lula teva |
| Father / paternal | Sun condition, 9th house, Pitri Rin, family-chart routing |
| Mother / maternal / home | Moon condition, 4th house, Matri Rin, family-chart routing |
| Children | Jupiter condition, 5th house, Kanya Rin |
| Money / finance / wealth | 2nd & 11th houses, Jupiter & Venus condition |
| Health | 6th & 8th houses, Sun + Mars condition, danger years |
| Foreign / travel / settlement | Rahu condition, 12th & 9th houses |
| Spiritual / detachment | Ketu + Jupiter condition, 12th house, Pujari teva |
| Generic / no question | Standard emphasis across all axes |

---

## Verification Display Format

`chart-verifier` (school `lalkitab`) re-maps the Vedic D1 into the Lal Kitab
FIXED house frame (Aries = house 1 … Pisces = house 12) and renders it into
exactly this layout. The orchestrator shows it and waits for the user to
confirm before any analysis. The birth Lagna is recorded only as *flavour* —
the houses never rotate. Lal Kitab uses no D9, no Nakshatras, no Vimshottari;
if the user supplied any of those, display them but exclude with an explicit
note — do not render them in this verification display.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAL KITAB CHART (re-mapped to fixed-house frame)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Native: [name]
Born: [date] at [time]
Place: [city]
Vedic Lagna: [sign] [degree] (flavour only — houses do not rotate)
Current Age: [N] years

PLANETARY HOUSE PLACEMENT (Lal Kitab — Aries always house 1)
| House | Sign        | Planet(s)     | Degree(s) | Retro |
|-------|-------------|---------------|-----------|-------|
|   1   | Aries       | [planets]     | [deg]     | [R?]  |
|  ...  | ...         | ...           | ...       | ...   |
|  12   | Pisces      | [planets]     | [deg]     | [R?]  |
(one row per house, 1–12 — Aries→1, Taurus→2, Gemini→3, Cancer→4,
 Leo→5, Virgo→6, Libra→7, Scorpio→8, Sagittarius→9, Capricorn→10,
 Aquarius→11, Pisces→12)

Empty houses: [list]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ Does this match your chart?
  Reply "Confirmed" — or tell me what needs correction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Do not proceed until the user explicitly confirms.

---

## Worker dispatch notes by mode

The baseline JSON already contains: the re-mapped fixed-house chart, pakka ghar
+ dignity per planet, sleeping/awake status, the six-rin diagnosis with Farman
citations, the teva classification, the age-based Varshphal table, and the
four-signal timing-engine output. Workers treat all of it as ground truth.

- **Mode A — natal.** 12 `unit-analyzer` agents, one per house. Each worker:
  loads `pakka_ghar.md` + `aspects.md` + `rin_diagnosis.md` + `teva_types.md`,
  reads its house's significance, resident planets' sleeping/dignity status, and
  Farman-driven dynamics. The synthesizer produces strongest/weakest houses and
  the rin→upaay links.
- **Mode B — family.** One `unit-analyzer` per relative requested (father,
  mother, spouse, sons, daughters, siblings — ~6). Each loads `family_chart.md`
  + `pakka_ghar.md` + `aspects.md`, examines the relative's house(s) and karaka,
  determines Enhancer / Neutral / Drainer role, applies the relative-specific
  Farman rule tables, flags cross-family compounding patterns.
- **Mode C — varshphal.** One `unit-analyzer` per year window: current age,
  next-5-years (brief), next major year, plus any 42/48/63 in the next 25 years.
  Each loads `varshphal.md` + `upaay_catalog.md`, applies the per-year reading
  procedure to the baseline's year-ruler table, prescribes year-upaay.
- **Mode D — full.** Run Modes A + B + C as one wide parallel wave.
- **Mode E — upaay.** Reuse `unit-analyzer` to tier the remedy catalog: one
  worker per tier (Critical / Strengthening / Maintenance), each loading
  `upaay_catalog.md`, mapping the baseline's active rins, sleeping planets, and
  teva-driven upaay priority to ranked remedies with Farman citations and
  contraindications.
- **Mode F — timing.** ~3 `unit-analyzer` agents interpreting the convergence
  engine's top candidate years from the baseline JSON. Each loads `timing.md` +
  `upaay_catalog.md`, explains why a window scored (which of the four signals
  fired), applies the sleeping/rin/danger-year filters, pairs each window with
  activation upaay. Always 2–3 ranked windows, never a single date.

---

## Synthesis weighting (Wave 2)

The `synthesizer` produces the Phase-10 one-page summary. Lal Kitab weighting:

- **Rin overlay dominates.** Active rins take precedence over isolated house
  strengths — a strong house under an active lineage rin still reads as blocked
  until the rin is addressed.
- **Sleeping benefics = unrealized promise.** Flag explicitly; a sleeping
  benefic's results never materialize without intervention.
- **Teva sets upaay priority** (see `teva_types.md` table): Dukhi → lineage rins
  first; Andha → awaken sleeping planets first; Lula → Mars-Saturn pacification
  first; Rajyogi → Saturn-year preparation; Pujari → reinforce Jupiter-Ketu,
  avoid material-amplification upaay.
- **Multi-rin charts.** 2 rins → each one tier worse; 3+ → debt-saturation,
  prioritize Pitri/Matri first.
- Pyramid principle: verdict first, full reasoning underneath.

### Phase 10 summary template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAL KITAB READING — SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Chart type (teva):    [primary + secondary]
Active rins:          [list with severity]
Sleeping planets:     [list]
Strongest houses:     [list]
Weakest houses:       [list]

Top 3 life themes:    1. … 2. … 3. …
Top 3 priority upaay: 1. [name + Farman ref] 2. … 3. …

Watch-year (next danger year): [age + planet]
Watch-year upaay:              [name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Upaay output rules (Phase 9 / Mode E)

Output remedies in three priority tiers — Tier 1 Critical (rin-related),
Tier 2 Strengthening (sleeping benefics, weak houses), Tier 3 Maintenance
(lifestyle / dietary / behavioral). For each upaay state: for whom, action,
frequency, duration, timing, Farman citation, caution.

- Every upaay cites a Farman; modern adaptations flagged and ranked lower.
- Conflicting upaay must be flagged (some remedies cancel each other).
- Age-bound upaay must state the age window.
- Pregnancy / health contraindications must appear if relevant.
- No mantras, no pujas as primary upaay — Lal Kitab is action-based.

Full remedy catalog with all Farman citations is in `upaay_catalog.md`.

---

## Output style

- Authoritative, precise, advisory tone.
- Show every diagnostic step explicitly — pakka ghar status, sleeping check, rin
  trigger, teva.
- Use tables liberally. Pyramid principle — verdict first, reasoning underneath.
- No unnecessary hedging; if a rin is present, name it. If a planet is sleeping,
  declare it.
- Sanskrit/Urdu terms italicized once on first use, then plain.
- Farman citations in `[Farman X, Vol Y (year)]` format.
