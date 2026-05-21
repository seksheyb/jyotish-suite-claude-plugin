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
Antara. Transit of Jupiter/Sun through significator stars confirms. Always give
a specific window: "Between [start] and [end], during the [MD]-[BD]-[AD]-[SD]
period."

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
   appear (see `methodology.md` special rules).

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
