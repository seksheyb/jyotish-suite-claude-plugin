# Jaimini Drishti — Sign Aspect Tables

Sign-based aspects only. No orbs. No degree calculation. A sign either aspects
another or it does not.

**The live lookup path is `build_drishti_map()` in
`scripts/compute_jaimini_baseline.py`** — it precomputes the full 12x12 matrix
and the baseline JSON carries it as `jaimini_drishti_map`. Workers read that
map as ground truth and never recompute it (Conduct Rule 4). This file is
rationale only: why the rules produce the table they do, so a worker can
explain an aspect, not just cite it.

---

## The Three Rules

**Rule 1 — Movable signs** (Aries, Cancer, Libra, Capricorn):
Aspect all Fixed signs *except* the one immediately next in zodiacal order.

**Rule 2 — Fixed signs** (Taurus, Leo, Scorpio, Aquarius):
Aspect all Movable signs *except* the one two signs ahead in zodiacal order.

**Rule 3 — Dual signs** (Gemini, Virgo, Sagittarius, Pisces):
Aspect all other Dual signs, no exception.

## Why the exceptions differ (Movable skips +1, Fixed skips +2)

The asymmetry is the whole reason the aspect map isn't fully mutual. A Movable
sign's excluded Fixed sign is the very next sign in the zodiac (e.g. Aries
skips Taurus, its immediate neighbor). A Fixed sign's excluded Movable sign is
*two* signs ahead, not one (e.g. Taurus skips Cancer, not Aries) — because the
sign one ahead of any Fixed sign is always Dual, and Dual signs aren't in a
Fixed sign's Movable-only aspect scope to begin with. So "skip the next sign"
and "skip the sign two ahead" are really the same rule — *skip the next sign
of the target quality* — applied to Movable-looking-at-Fixed and
Fixed-looking-at-Movable respectively. Because the two skip-offsets (+1 for
Movable, +2 for Fixed) don't mirror each other around the same pair, a handful
of Movable/Fixed pairs end up aspected from only one side — see One-Way
Aspects below. Dual signs have no such asymmetry: every Dual sign is one of
only four, and each aspects all three others unconditionally, so Dual-Dual
aspects are always mutual.

All Jaimini Drishti *within a quality pair that both sides retain* is mutual —
if A aspects B and B aspects A, the exchange is bidirectional. Where the
skip-offsets diverge, exactly one direction survives.

---

## Complete Aspect Table — All 12 Signs

| Sign | Type | Aspects |
|------|------|---------|
| Aries | Movable | Leo, Scorpio, Aquarius |
| Taurus | Fixed | Aries, Libra, Capricorn |
| Gemini | Dual | Virgo, Sagittarius, Pisces |
| Cancer | Movable | Taurus, Scorpio, Aquarius |
| Leo | Fixed | Aries, Cancer, Capricorn |
| Virgo | Dual | Gemini, Sagittarius, Pisces |
| Libra | Movable | Taurus, Leo, Aquarius |
| Scorpio | Fixed | Aries, Cancer, Libra |
| Sagittarius | Dual | Gemini, Virgo, Pisces |
| Capricorn | Movable | Taurus, Leo, Scorpio |
| Aquarius | Fixed | Cancer, Libra, Capricorn |
| Pisces | Dual | Gemini, Virgo, Sagittarius |

(Verified against `build_drishti_map()` output field-for-field.)

---

## Mutual Aspect Pairs

**Movable–Fixed pairs that are mutual (8 of 16 possible):**
Aries↔Leo, Aries↔Scorpio, Cancer↔Scorpio, Cancer↔Aquarius, Libra↔Taurus,
Libra↔Aquarius, Capricorn↔Taurus, Capricorn↔Leo.

**Dual–Dual pairs (all 6 are mutual):**
Gemini↔Virgo, Gemini↔Sagittarius, Gemini↔Pisces, Virgo↔Sagittarius,
Virgo↔Pisces, Sagittarius↔Pisces.

## One-Way Aspects (8 total)

The remaining 8 of the 16 Movable–Fixed pairs are one-way — the exchange
carries only in the direction listed, no return aspect. They chain into a
single reverse-zodiacal cycle through all eight Movable and Fixed signs:

Aries → Aquarius → Capricorn → Scorpio → Libra → Leo → Cancer → Taurus → (back to Aries)

| From | To |
|------|-----|
| Aries | Aquarius |
| Taurus | Aries |
| Cancer | Taurus |
| Leo | Cancer |
| Libra | Leo |
| Scorpio | Libra |
| Capricorn | Scorpio |
| Aquarius | Capricorn |

---

## Application Notes

1. **Always check both directions** when analyzing a sign — what it aspects,
   and what aspects it (they may differ; see one-way aspects above).
2. **Empty aspecting sign** → the aspect still operates; read through the sign
   lord's placement.
3. **Multiple planets in the aspecting sign** → all contribute their Karaka
   roles and natural natures to the aspected sign.
4. **Mutual aspect = bidirectional exchange** — describe both directions;
   planets in both signs co-influence each other's themes.
5. **One-way aspect** — only the aspecting sign's planets influence the
   aspected sign; there is no return influence to describe.
6. **Nodes (Rahu/Ketu)** cast aspects based on their sign's type
   (Movable/Fixed/Dual), same as any other occupant.
