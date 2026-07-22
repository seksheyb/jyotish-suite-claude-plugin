# BNN Degree Flags Reference

Run these checks on every planet encountered — Karaka, conjuncts, flow positions, trine positions, growth positions, opposition, and aspecting planets. No planet is exempt.

The numeric tables (combustion orbs, Gandanta zones, Mrityu Bhaga degrees per
sign, Pushkara degrees) now live in `lib/jyotish_primitives.py` and are
pre-computed into every planet's `degree_flags` / `degree_flag_verdict` in
`baseline.json` by `compute_bnn_baseline.py`. Do not recompute or guess a
degree flag from raw sign/degree data — read the flag the baseline already
assigned, and apply the interpretive meaning below.

---

## Combustion

Planet within Sun's orb = suppressed; cannot deliver significations even if dignified.

Flag: 🔴 Cb — Combust planet's Karaka themes are burned. A combust planet in a flow or trine position means that support cannot activate. **Combustion dominates all other flags** — a combust Pushkara planet is still suppressed.

---

## Gandanta

Sign-junction degrees at the water→fire boundaries (Cancer→Leo, Scorpio→Sagittarius, Pisces→Aries). Karmically charged; unstable; results come through difficulty.

Flag: 🔴 Gd — Karaka at Gandanta carries karmic knots around its themes. Planet in Gandanta in a flow/trine position = that support is karmically charged and unstable.

---

## Mrityu Bhaga (Death Degrees)

Planet at its death degree struggles to deliver significations regardless of sign dignity.

Flag: 🔴 MB — Mrityu Bhaga overrides sign dignity. An exalted Karaka at MB still struggles to deliver.

---

## Pushkara Navamsa / Pushkara Bhaga

Planet at an auspicious degree is empowered to deliver results with greater ease.

Flag: 🟢 PK — Pushkara planet delivers with ease; a debilitated Karaka at Pushkara may outperform a dignified Karaka at Mrityu Bhaga.

---

## Sandhi (Cusp Degrees)

| Zone | Flag | Effect |
|------|------|--------|
| Sign entry (0°–1°) | 🟡 Sd | Immature; just arriving in sign; inexperienced expression |
| Sign exit (29°–30°) | 🟡 Sd | Finishing tenure; unstable; unreliable delivery |

Sandhi Karaka = erratic or inconsistent delivery of its themes.

---

## Planetary War (Graha Yuddha)

Two eligible planets in the same sign, within orb of each other.

**Eligible:** Mars, Mercury, Jupiter, Venus, Saturn — not Sun, Moon, Rahu, Ketu.

- **Lower degree = winner** → themes intact
- **Higher degree = defeated** → 🔴 PW — themes weakened throughout the chart
- **Close Contention** (wider separation, not an outright war) = 🟡 CC — mutual tension; results from both are uneasy

Defeated planet as Karaka → Karaka significations suppressed even if sign placement is strong.
Defeated planet as aspecting planet → aspect is weakened.
Defeated planet in flow/trine → that position's support is weakened.

---

## Degree Flag Priority Table

When multiple flags apply to the same planet:

| Combination | Net Effect |
|-------------|-----------|
| Combust + any positive flag | 🔴 Combustion dominates — planet suppressed regardless |
| Mrityu Bhaga + exalted | 🔴 MB overrides — struggles to deliver despite dignity |
| Gandanta + own sign | 🔴 Karmically charged but capable if worked consciously |
| Sandhi + Pushkara | 🟡 Instability partially offset — inconsistent but possible |
| Planetary War (defeated) + Pushkara | 🔴 War suppresses; Pushkara helps but does not fully override |
| Vargottama + Pushkara | 🟢 Exceptional delivery — soul-endorsed and degree-empowered |
| Vargottama + Mrityu Bhaga | Mixed — soul-level intent strong but material delivery blocked |
| Retrograde + Pushkara | 🟢 Empowered but internalized or delayed in timing |
| Retrograde + MB | 🔴 Double suppression — weakened and non-linear |
