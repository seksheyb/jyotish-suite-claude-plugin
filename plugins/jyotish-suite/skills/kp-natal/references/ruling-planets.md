# Ruling Planets — KP Methodology

## What RP represents
The Ruling Planets (RP) are the planets active at the moment of the question (or the moment of any decision). They cross-confirm the cuspal sub-lord verdict. **A matter fructifies when the running dasha-bhukti-antara lord is also a Ruling Planet AND a significator of the positive house combination.**

## The seven RP factors (in strength order)

1. **Lagna Sub Lord** — strongest
2. **Lagna Star Lord (Nakshatra Lord)**
3. **Lagna Sign Lord (Rasi Lord)**
4. **Moon Sub Lord**
5. **Moon Star Lord**
6. **Moon Sign Lord**
7. **Day Lord** — weakest, but always included

Computation of all seven factors, the exclusion rules (retrograde, combustion),
and the Rahu/Ketu qualification test are owned entirely by
`scripts/compute_kp_natal_baseline.py` — the baseline emits the full derivation
(`ruling_planets` block) with each factor's sign/star/sub-lord shown. Do not
recompute or re-derive RP by hand; read the baseline's output and show it
verbatim per Critical Rule 2 in `references/orchestration-notes.md`.

## Using RP in the verdict

1. **The dasha lord during the fructification window must be in the RP set.** If running Saturn-Mercury and neither is RP → fructification delayed.
2. **CSL of primary house must be in RP set OR in the star/sub of an RP planet.** If yes, strong yes. If no, weak yes or no.
3. **Repeat RP at fructification:** Krishnamurti's principle — the same planets ruling at the moment of question will rule again at the moment of fructification. Use this to forecast: scan upcoming dates for when transit Moon passes through a star whose lord is in the RP set + a sub whose lord is RP.

**Strongest RP convention.** The baseline reports `strongest_rp` as the **Lagna Sub Lord** (RP factor #1), always. A qualifying Rahu/Ketu is *added* to the RP set (via its sign-lord, star-lord, or a conjunction with an RP), and it acts as the agent for the matters it signifies — but it does **not** displace the Lagna Sub Lord as the single strongest ruling planet in this implementation. Treat a qualifying node as a strong co-ruler, not as the top of the strength order.

## Common errors

- Forgetting to subtract KP New ayanamsa (different from Lahiri by ~6 arc-minutes)
- Using natal Moon's nakshatra instead of transit Moon's nakshatra at moment of question
- Including retrograde planets without depositor-check
- Using RP from natal chart instead of moment-of-question chart
- Day-lord error when question is asked in early morning hours before sunrise
