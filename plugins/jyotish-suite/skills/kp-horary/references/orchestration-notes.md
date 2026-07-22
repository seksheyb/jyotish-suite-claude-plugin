# KP Horary — Orchestration & Output Notes

Interpretive material that workers and the synthesizer apply. Moved here from
the old monolithic SKILL.md when the skill became a wave orchestrator. The
deterministic computation (chart from 249-number, RP, cusps, 4-level
significators, dasha, house-combination tables) now lives in the Python sidecar
`scripts/compute_kp_horary_baseline.py`; this file keeps only interpretation.

## Two Lagnas — never mix them

KP horary uses two distinct Lagnas. The baseline JSON keeps them separate and
workers must too:

- **Chart Lagna** — derived from the 1-249 horary number. This is the Lagna of
  the horary chart; all 12 cusps and the CSLs are anchored to it. House
  signification and the CSL verdict use only this Lagna.
- **Ruling-Planets Lagna** — the *real* rising sign at the place and moment the
  question is taken. Used only to compute the RP set (its sign/star/sub lords).
  Never use the RP Lagna for cusps or CSLs; never use the chart Lagna for RP.

## Per-cusp CSL analysis — output block (unit-analyzer)

Each `unit-analyzer` working a cusp returns one block in this shape:

```
Cusp [N] — [house name]
  Sub Lord: [planet]
    - Owns houses: [...]
    - Occupies house: [...]
    - In star of: [planet] -> which signifies houses [...]
    - Itself signifies (via star + own): houses [...]
    - Connection to question's positive set: [yes/no, which houses]
    - Connection to question's negative set: [yes/no]
    - Sub-sub-lord (only if CSL is ambiguous): [planet] -> tilts [pos/neg]
    - Verdict for this cusp: [favourable / unfavourable / mixed]
    - Confidence + caveats: [sandhi, combustion, retrograde, conflicts]
```

The CSL of the **primary house** (7th for marriage, 10th for career, etc.) is
decisive. If it signifies the positive combination, the matter fructifies. If it
signifies the negative set, the matter is denied. If it signifies both, the
sub-sub-lord breaks the tie. If it signifies neither, the matter does not
fructify in the current dasha.

## Significator strength & signification through stars

A planet primarily signifies the houses owned/occupied by the planet in whose
**star** it sits, and only secondarily the houses it itself owns/occupies —
star-lord effects outrank own-placement effects. For any house, list its
significators in strength order:

- **Level 1** (strongest) — planets in the star of the planet occupying that
  house
- **Level 2** — planets occupying that house
- **Level 3** — planets in the star of the lord of that house
- **Level 4** (weakest) — the lord of the house itself

Conjunction with Rahu/Ketu in a house adds those nodes to that house's
significators. When a house is empty (no planet occupies it), read from
Level 3/4 — the lord of the house and planets in its star. If multiple
planets share one star, all are significators; the one closest in degree to
the star's mid-point is the strongest of that group.

## Special rules — degree-sensitive flags

These affect how much weight a CSL or significator carries. Some are emitted
by the baseline JSON already; where the audit found a gap, apply the rule by
eye against the baseline's raw degrees rather than skipping it:

- **Retrograde planets** give the result of the planet in whose star they
  sit, not their own placement's result. Exception: Rahu/Ketu always give the
  effects of their dispositor and any planet they're conjunct, retrograde or
  not (nodes have no independent "own" result).
- **Combust planets** (within 8.5° of the Sun — KP's own orb, not the wider
  Parashari combustion orbs used elsewhere in the suite) lose strength as
  significators unless they are themselves a Ruling Planet.
- **Sandhi** (within 0°30' of a sign edge) — a planet or the chart Lagna this
  close to a sign boundary cannot give a clear result. CSL at sandhi is
  unreliable; say so and suggest re-asking the question later rather than
  forcing a verdict.
- **Mrityu Bhaga, Pushkara, Gandanta degrees** — note as flags when present,
  but in horary they are secondary to the CSL verdict; don't let them
  override a clear CSL/RP/dasha chain.

## RP cross-check criteria (sequential, after CSL verdict)

- **Strong YES** — RP planets are also significators of the positive house
  combination, and the primary CSL is itself in the RP list (or in the star/sub
  of an RP planet).
- **Strong NO** — RP planets are significators of the negative set; the primary
  CSL is unconnected to RP.
- **Mixed / conditional** — some RP align, some don't; adjust confidence down
  accordingly.

## Timing chain (sequential, after RP cross-check)

The matter fructifies during the joint Dasha-Bhukti-Antara when the MD, Bhukti
and Antara lords are all significators of the positive set (or in the star of
one that is); Sookshma narrows to days. If current DBA all signify the positive
combo and the CSL is favourable, fructification is near-term (within the current
Antara). If only MD-Bhukti align, fructification waits for the next favourable
Antara. Always give a specific window: "Between [start] and [end], during the
[MD]-[BD]-[AD]-[SD] period."

**Transit confirmation is computed, not prose.** SKILL.md Wave 1 runs
`scripts/compute_transits.py` (forward transit of Jupiter/Sun/Moon through the
significator stars, scanned across the current dasha window) right after the
RP cross-check. Cite its actual confirming/denying dates in the verdict — do
not eyeball transit timing from the baseline's static planet positions.

## Common failure modes to avoid

- Reading the chart before framing the question precisely.
- Overweighting Jupiter or benefics — KP doesn't care about benefic/malefic,
  only signification.
- Ignoring the CSL when it contradicts visual planet placement (an exalted
  planet in the 7th doesn't override a 7th CSL that denies marriage).
- Skipping the RP cross-check.
- Forgetting to check the sub-sub-lord when the CSL signifies both the
  positive and negative sets.
- Mixing horary with natal data — keep them separate (Critical Rule 4).
- Treating the baseline's approximated Rahu/Ketu "conjunct" (same-sign, not a
  tight orb) as a precise conjunction when weighing a node's RP-agent
  eligibility.

## Phase-8 verdict — output template (synthesizer)

```
========================================
VERDICT
========================================

Question: [restated]
Horary number: [N]

Outcome: [YES / NO / CONDITIONAL]

Confidence: [HIGH / MEDIUM / LOW]
  - CSL of primary house: [favourable / unfavourable]
  - Ruling Planets alignment: [strong / partial / weak]
  - Dasha alignment: [supports / does not support]

Timing window: [date range, with DBA period]

Key supporting factors:
  - [...]

Caveats / what could change the call:
  - [degree-sensitive flags, e.g. CSL near sandhi]
  - [retrograde considerations]
  - [sub-sub-lord conflicts]
  - [transit confirmation needed]

Recommended action: [specific, actionable]
========================================
```

## Critical interpretive rules

1. **Never override the CSL with sentiment.** If the 7th CSL says no, the
   marriage doesn't happen — even if Jupiter is exalted in the 7th.
2. **Show degrees and lord chains.** Every claim about a planet's signification
   must be traceable.
3. **Confidence is not certainty.** A high-confidence call still carries
   caveats — state them.
4. **Don't combine charts.** The horary chart stands alone — never mix in natal
   data.
5. **Question framing matters.** If the question is mis-asked, redirect before
   reading.
6. **Outer planets (Uranus/Neptune/Pluto)** — display for reference only; KP is
   a 9-graha system. Do not use them in core analysis.
7. **Retrograde planets** — a retrograde planet gives the result of the planet
   in whose star it sits, not its own. Apply when retrograde significators
   appear (see "Special rules — degree-sensitive flags" above).

## Output style

- Authoritative, precise, advisory tone.
- Show calculations explicitly — the user wants to see the work; the
  RP-calculation gloss from the baseline must be surfaced, not hidden.
- Use tables liberally for cusps, planets, significators.
- Pyramid principle — verdict first in the summary, full reasoning below.
- Never hedge unnecessarily; if the chart says no, say no.

## Verification Display Format

`chart-verifier` renders the computed horary chart and the Ruling-Planets
calculation into exactly this layout. The orchestrator shows it and waits for
the user to reply "Confirmed" before Wave 1 dispatches. The display has two
distinct Lagnas — keep them visibly separate: the **chart Lagna** is derived
from the 1-249 number and anchors the cusps; the **RP Lagna** is the real
rising sign at the question moment and is used only for Ruling Planets.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        KP HORARY CHART
        Ayanamsa: KP New | Cusps: Placidus
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Question : [restated]
Horary number : [N] (1-249)   Time : [datetime + tz]   Place : [city, lat, lon]

CHART LAGNA (from horary number [N]): [Sign] [Deg]°[Min]'[Sec]"
  — this Lagna anchors all 12 cusps and the CSLs.

12 CUSPS:
┌──────┬──────────┬───────────────┬───────────┬───────────┬───────────┬──────────────┐
│ Cusp │ Sign     │ Degree        │ Sign Lord │ Star Lord │ Sub Lord  │ Sub-Sub Lord │
├──────┼──────────┼───────────────┼───────────┼───────────┼───────────┼──────────────┤
│ 1    │ [sign]   │ [d]°[m]'[s]"  │ [planet]  │ [planet]  │ [planet]  │ [planet]     │
│ … cusps 1-12 — one row per cusp                                                    │
└──────┴──────────┴───────────────┴───────────┴───────────┴───────────┴──────────────┘

9 PLANETS:
┌──────────┬──────────┬───────────────┬───────┬───────────┬───────────┬───────────┬──────────────┬──────┐
│ Planet   │ Sign     │ Degree        │ House │ Sign Lord │ Star Lord │ Sub Lord  │ Sub-Sub Lord │  R?  │
├──────────┼──────────┼───────────────┼───────┼───────────┼───────────┼───────────┼──────────────┼──────┤
│ Sun      │ [sign]   │ [d]°[m]'[s]"  │ [#]   │ [planet]  │ [planet]  │ [planet]  │ [planet]     │ [Y/N]│
│ … Sun through Ketu — one row per planet                                                                │
└──────────┴──────────┴───────────────┴───────┴───────────┴───────────┴───────────┴──────────────┴──────┘
(Uranus/Neptune/Pluto shown for reference only — not used in KP analysis.)

RULING PLANETS — Calculation
  1. Day Lord (weekday at sunrise) : [Day name] → [Planet]
  2. Moon at this moment : [d]°[m]'[s]" — [Sign]
       Sign Lord [planet] | Star Lord [planet] | Sub Lord [planet]
  3. RP LAGNA — real rising sign at this place/time : [d]°[m]'[s]" — [Sign]
       Sign Lord [planet] | Star Lord [planet] | Sub Lord [planet]
       (RP Lagna is used ONLY for Ruling Planets — never for cusps/CSLs.)
  4. RP Set (deduplicated, strength order) :
       [RP-Lagna Sub, RP-Lagna Star, RP-Lagna Sign,
        Moon Sub, Moon Star, Moon Sign, Day Lord]
       = [final list]
     Strongest RP : RP-Lagna Sub Lord = [planet]

VIMSHOTTARI DASHA (at question moment):
  Mahadasha  : [Planet] — [start] to [end]
  Antardasha : [Planet] — [start] to [end]
  Pratyantar : [Planet] — [start] to [end]
  Sookshma   : [Planet] — [start] to [end]  (if known)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠ Does this match the chart you expect?
  Reply "Confirmed" — or tell me what needs correction.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Do not proceed until the user explicitly confirms.
