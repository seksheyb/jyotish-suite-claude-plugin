# Ruling Planets — KP Methodology

## What RP represents

The Ruling Planets (RP) are the planets active at the moment of the question
(or the moment of any decision). They cross-confirm the cuspal sub-lord
verdict. **A matter fructifies when the running dasha-bhukti-antara lord is
also a Ruling Planet AND a significator of the positive house combination.**

## The seven RP factors (in strength order)

1. **Lagna Sub Lord** — strongest
2. **Lagna Star Lord (Nakshatra Lord)**
3. **Lagna Sign Lord (Rasi Lord)**
4. **Moon Sub Lord**
5. **Moon Star Lord**
6. **Moon Sign Lord**
7. **Day Lord** — weakest, but always included

`Lagna` here is the **RP Lagna** — the real rising sign at the place/moment of
the question — never the horary chart Lagna derived from the 1-249 number.
See "Two Lagnas" in `orchestration-notes.md`.

## How RP is computed (script owns this — nothing below to hand-derive)

Day Lord, Moon's sign/star/sub, the RP Lagna's sign/star/sub, deduplication,
retrograde exclusion (with the depositor-is-RP exception), and the Rahu/Ketu
agent rule are all computed by `scripts/compute_kp_horary_baseline.py` and
returned in the baseline JSON's `ruling_planets` block. Workers read and cite
that block directly — nothing here is recomputed by hand.
`orchestration-notes.md`'s Verification Display Format is the exact layout the
RP calculation is rendered in for the user.

Combustion is computed separately as a **per-planet flag** (`combust: true`,
uniform KP 8.5° orb from the Sun) on each entry of the baseline JSON's
`planets` block — not as an RP-set weighting. Treat a combust significator as
weakened when reasoning, but the RP set itself is not re-ranked for combustion.

## Using RP in the verdict

1. **The dasha lord during the fructification window must be in the RP set.**
   If running Saturn-Mercury and neither is RP → fructification delayed.
2. **CSL of primary house must be in RP set OR in the star/sub of an RP
   planet.** If yes, strong yes. If no, weak yes or no.
3. **Repeat RP at fructification** — Krishnamurti's principle: the same
   planets ruling at the moment of question will rule again at the moment of
   fructification. Use this to forecast: scan upcoming dates for when transit
   Moon passes through a star whose lord is in the RP set + a sub whose lord
   is RP. (`scripts/compute_transits.py`, wired in SKILL.md Wave 1, now does
   this scan instead of the worker eyeballing an ephemeris.)

## Common errors (interpretation, not computation)

- Citing RP from a natal chart instead of the moment-of-question chart.
- Reporting a retrograde planet as RP without checking the baseline's
  depositor-exception flag first.
- Treating the RP Lagna and the chart (horary) Lagna as interchangeable —
  they never are.
