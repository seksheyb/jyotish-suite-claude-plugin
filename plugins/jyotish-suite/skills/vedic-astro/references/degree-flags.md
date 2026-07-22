# Degree Flags Reference — Interpretive Meaning

The numeric tables that used to live in this file (Mrityu Bhaga degrees,
Pushkara Navamsa/Bhaga zones, Gandanta junctions, Sandhi bands, Planetary War
threshold) now live in `${CLAUDE_PLUGIN_ROOT}/lib/jyotish_primitives.py` and
are computed once into `baseline.json`'s per-planet `degree_flags` block by
`compute_vedic_baseline.py`. Workers **never** recompute a degree flag from
scratch — read it off the baseline and use this file only for what the flag
*means*. (This also retires the stale Pushkara Navamsa table that used to
live here and disagreed with `chart-tables.md` — there is now exactly one
source of truth for the zones, and no reference-file conflict to resolve.)

---

## Mrityu Bhaga (Death Degrees)

A planet at its Mrityu Bhaga degree in a sign struggles to deliver its
significations. It is considered weakened or "dying" in that placement —
present but unable to fully express its promise. Read it as suppressed
delivery, not absence: the planet's themes still exist in the chart, they
just come through diminished, delayed, or via difficulty.

---

## Pushkara Navamsa

Pushkara Navamsas are specific zones within signs considered highly
auspicious. A planet placed here is empowered to give its best results —
treat it as an amplifier on top of whatever the planet's dignity and house
placement already indicate. It does not rescue a badly afflicted planet on
its own, but it meaningfully raises the ceiling of what the planet can
deliver.

---

## Pushkara Bhaga (Single Auspicious Degrees)

A more precise version of Pushkara Navamsa — a single degree per sign,
considered extraordinarily powerful. A planet sitting exactly on (within the
baseline's orb) a Pushkara Bhaga is read as especially fortunate in
delivering its significations, stronger than a planet merely in the wider
Pushkara Navamsa zone.

---

## Gandanta Zones

Water→Fire sign junctions. Karmically charged and unstable. Planets here
carry unresolved soul-level knots — the theme isn't fully processed yet, and
outcomes tied to that planet tend to feel effortful, entangled, or
recurring rather than clean.

**Interpretation by Pada:**
- Last Pada of a water sign (e.g., Ashlesha 4, Jyeshtha 4, Revati 4): the
  water themes are unresolved — emotional, relational, or spiritual karmas
  still being worked through.
- First Pada of the following fire sign (e.g., Magha 1, Mula 1, Ashwini 1):
  the fire initiation is raw — the soul is just beginning to process the new
  theme, so early results can be unsteady even when the underlying promise
  is good.

---

## Sandhi (Cusp) Degrees

| Zone | Interpretation |
|------|---------------|
| Start-of-sign (0°) | Planet is immature in this sign — inexperienced, just arriving, not fully expressing sign qualities. Sometimes read as having qualities of the previous sign bleeding through. |
| End-of-sign (29°) | Planet is finishing its tenure — unstable, wrapping up, transitioning, unreliable delivery. Sometimes read as exhausted or extreme in its sign expression. |

---

## Planetary War (Graha Yuddha)

Occurs when two visible planets (Mars, Mercury, Jupiter, Venus, Saturn — not
Sun, Moon, Rahu, or Ketu, which don't war) are close enough in longitude for
the baseline to flag it.

**Rules:**
- The planet with the **lower longitude degree wins** the war; the one with
  the **higher longitude degree is defeated** — its significations are
  weakened.
- The defeated planet's themes and the houses it rules suffer even if it is
  otherwise well-placed.
- Both planets' significations are somewhat disturbed during the war — the
  winner is not unaffected, just dominant.

> In a planetary war, read the winner's significations as dominant but note
> both are under stress. The baseline surfaces `planetary_war` per planet
> (winner/loser/separation) — cite it directly rather than re-deriving it
> from raw longitudes.
