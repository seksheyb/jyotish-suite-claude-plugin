# Jaimini Drishti — Sign Aspect Tables

Sign-based aspects only. No orbs. No degree calculation. A sign either aspects
another or it does not.

**The live lookup path is `jaimini_drishti_matrix()` in
`lib/jyotish_primitives.py`** (the Jaimini baseline script aliases it as
`build_drishti_map()`) — it precomputes the full 12x12 matrix and the baseline
JSON carries it as `jaimini_drishti_map`. Workers read that map as ground
truth and never recompute it (Conduct Rule 4). This file is rationale only:
why the rules produce the table they do, so a worker can explain an aspect,
not just cite it.

---

## The Three Rules

**Rule 1 — Movable signs** (Aries, Cancer, Libra, Capricorn):
Aspect all Fixed signs *except* the adjacent one — the Fixed sign immediately
*after* it in zodiacal order (Aries skips Taurus).

**Rule 2 — Fixed signs** (Taurus, Leo, Scorpio, Aquarius):
Aspect all Movable signs *except* the adjacent one — the Movable sign
immediately *before* it in zodiacal order (Taurus skips Aries).

**Rule 3 — Dual signs** (Gemini, Virgo, Sagittarius, Pisces):
Aspect all other Dual signs, no exception.

## Why every Rasi Drishti is mutual

The exception in Rules 1 and 2 is one and the same pair seen from either side:
each Movable sign sits immediately before a Fixed sign (Aries–Taurus,
Cancer–Leo, Libra–Scorpio, Capricorn–Aquarius), and those four adjacent pairs
are exactly the ones excluded in both directions. A Movable sign therefore
aspects the three Fixed signs that are not its neighbour, and each of those
three Fixed signs aspects it back, because it is not *their* neighbour either.
Dual signs aspect all other Dual signs unconditionally. So the 12x12 matrix is
symmetric: if A aspects B, B aspects A. Read an aspect as a bidirectional
exchange between the two signs.

(An earlier version of the builder skipped the Movable sign *two ahead* of a
Fixed sign — Taurus skipping Cancer — which produced eight spurious one-way
aspects. That was a bug, fixed in the lib move; the matrix the baseline emits
now matches the classical rule.)

---

## Complete Aspect Table — All 12 Signs

| Sign | Type | Aspects |
|------|------|---------|
| Aries | Movable | Leo, Scorpio, Aquarius |
| Taurus | Fixed | Cancer, Libra, Capricorn |
| Gemini | Dual | Virgo, Sagittarius, Pisces |
| Cancer | Movable | Taurus, Scorpio, Aquarius |
| Leo | Fixed | Aries, Libra, Capricorn |
| Virgo | Dual | Gemini, Sagittarius, Pisces |
| Libra | Movable | Taurus, Leo, Aquarius |
| Scorpio | Fixed | Aries, Cancer, Capricorn |
| Sagittarius | Dual | Gemini, Virgo, Pisces |
| Capricorn | Movable | Taurus, Leo, Scorpio |
| Aquarius | Fixed | Aries, Cancer, Libra |
| Pisces | Dual | Gemini, Virgo, Sagittarius |

(Verified against `jaimini_drishti_matrix()` output field-for-field; the
regression test `tests/test_gochara_primitives_regressions.py` asserts the
matrix is symmetric and `one_way` is empty.)

---

## Mutual Aspect Pairs

**Movable–Fixed pairs (12 of 16 possible; the 4 adjacent pairs are excluded):**
Aries↔Leo, Aries↔Scorpio, Aries↔Aquarius,
Cancer↔Taurus, Cancer↔Scorpio, Cancer↔Aquarius,
Libra↔Taurus, Libra↔Leo, Libra↔Aquarius,
Capricorn↔Taurus, Capricorn↔Leo, Capricorn↔Scorpio.

**Excluded adjacent pairs (no aspect either way):**
Aries–Taurus, Cancer–Leo, Libra–Scorpio, Capricorn–Aquarius.

**Dual–Dual pairs (all 6 are mutual):**
Gemini↔Virgo, Gemini↔Sagittarius, Gemini↔Pisces, Virgo↔Sagittarius,
Virgo↔Pisces, Sagittarius↔Pisces.

---

## Application Notes

1. **Every aspect is mutual** — if the Dasha Rasi aspects the Arudha Lagna, the
   Arudha Lagna aspects the Dasha Rasi. Describe the exchange, not a direction.
2. **Empty aspecting sign** → the aspect still operates; read through the sign
   lord's placement.
3. **Multiple planets in the aspecting sign** → all contribute their Karaka
   roles and natural natures to the aspected sign.
4. **Movable and Fixed signs never aspect their own quality** — a Movable sign
   has no Rasi Drishti on another Movable sign, nor a Fixed on a Fixed. Only
   Dual signs aspect within their quality.
