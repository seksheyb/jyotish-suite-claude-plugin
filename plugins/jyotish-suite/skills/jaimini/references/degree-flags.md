# Degree Flags Reference — Jaimini

Interpretation only. The numeric zones/tables (Mrityu Bhaga grid, Pushkara
Navamsa zones, Pushkara Bhaga degrees, Sandhi cusps, Planetary War orb) live
in `lib/jyotish_primitives.py` and are computed once, per planet, into
`compute_jaimini_baseline.py`'s output (`degree_flags` on each planet /
Karaka, plus `planetary_wars`). Workers read those flags from the baseline
JSON — never recompute a degree zone from this file.

---

## Gandanta

Water→Fire sign-junction degrees. A Karaka planet at Gandanta = the soul has
unresolved karma around that Karaka's themes. The karmic knot must be
consciously worked through — the significations don't unfold automatically.
Flag 🔴 Gd.

---

## Mrityu Bhaga (Death Degrees)

A planet at its Mrityu Bhaga has its Karaka significations suppressed — it
struggles to deliver even when sign dignity is strong. Flag 🔴 MB. Read with
±1° orb (from the baseline flag, not recomputed).

---

## Pushkara Navamsa / Pushkara Bhaga

A planet in a Pushkara zone has its Karaka significations empowered — it
delivers results with greater ease. Pushkara Bhaga (a single degree per sign)
is the more precise, more intense version of the same effect than Pushkara
Navamsa (a wider zone). Flag 🟢 PK.

---

## Sandhi (Cusp Degrees)

The first and last degree of a sign (0°–1°, 29°–30°) are junction zones. A
Sandhi Karaka delivers its themes inconsistently — results may come, but
erratically, because the planet is either just arriving in the sign's
expression or already leaving it. Flag 🟡 Sd.

---

## Planetary War (Graha Yuddha)

Two visible eligible planets (Mars, Mercury, Jupiter, Venus, Saturn — never
Sun, Moon, Rahu, Ketu) within 1° of each other in the same sign. The lower
degree planet wins — its Karaka themes stay intact. The higher degree planet
is defeated — its Karaka significations are suppressed throughout the chart
regardless of sign dignity:

- AK defeated → soul themes obstructed; requires extra conscious effort
- AmK defeated → career significations hampered despite apparent opportunity
- DK defeated → partnership and desire themes weakened

Flag 🔴 PW; state winner and defeated planet explicitly.

**Close contention** (2°–5° gap, not a formal war): flag as "in close
contention," note the degree gap — results from both Karakas may be uneasy or
competitive, without one being suppressed.

---

## Degree Flag Priority

When multiple flags apply to the same planet, net effect:

| Combination | Net Reading |
|-------------|-------------|
| Pushkara + strong sign | Exceptionally empowered Karaka |
| Mrityu Bhaga + exalted | Suppressed despite dignity — MB overrides |
| Gandanta + own sign | Karmically charged but capable if consciously worked |
| Sandhi + Pushkara | Instability partially offset by auspicious degree |
| Planetary War (defeated) + Pushkara | Suppression from war; Pushkara helps but doesn't fully override |
| Vargottama + Pushkara | Strongest possible Karaka expression |
| Vargottama + MB | Strong soul-level intent but material delivery blocked |
