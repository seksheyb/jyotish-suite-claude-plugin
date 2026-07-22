# Ashtakavarga — Bhinnashtakavarga Contribution Tables

The classical Parashari Sarvashtakavarga scheme. For each of the seven graha
"subjects" (Sun..Saturn), every contributor — the same seven planets plus the
Lagna — donates one benefic point ("rekha") to certain houses counted **from
the contributor's own sign** (house 1 = the contributor's own sign).

- **Bhinnashtakavarga (BAV)** of a planet = the per-sign sum over all eight
  contributors.
- **Sarvashtakavarga (SAV)** of a sign = the sum of the seven planets' BAV in
  that sign.
- The total SAV over the twelve signs is always **337** — a useful
  computation invariant. Per-planet BAV totals: Sun 48, Moon 49, Mars 39,
  Mercury 54, Jupiter 56, Venus 52, Saturn 39 (sum = 337).

`compute_vedic_baseline.py` implements these tables (`CONTRIB_HOUSES`); this
file is their human-readable spec. Each row below is a contributor; the cells
list the house-numbers (counted from that contributor) where the subject
planet earns one point.

---

## Subject: Sun
| Contributor | Benefic houses |
|-------------|----------------|
| Sun | 1, 2, 4, 7, 8, 9, 10, 11 |
| Moon | 3, 6, 10, 11 |
| Mars | 1, 2, 4, 7, 8, 9, 10, 11 |
| Mercury | 3, 5, 6, 9, 10, 11, 12 |
| Jupiter | 5, 6, 9, 11 |
| Venus | 6, 7, 12 |
| Saturn | 1, 2, 4, 7, 8, 9, 10, 11 |
| Lagna | 3, 4, 6, 10, 11, 12 |

## Subject: Moon
| Contributor | Benefic houses |
|-------------|----------------|
| Sun | 3, 6, 7, 8, 10, 11 |
| Moon | 1, 3, 6, 7, 10, 11 |
| Mars | 2, 3, 5, 6, 9, 10, 11 |
| Mercury | 1, 3, 4, 5, 8, 10, 11 |
| Jupiter | 1, 2, 4, 7, 8, 10, 11, 12 |
| Venus | 3, 4, 5, 7, 9, 10, 11 |
| Saturn | 3, 5, 6, 11 |
| Lagna | 3, 6, 10, 11 |

## Subject: Mars
| Contributor | Benefic houses |
|-------------|----------------|
| Sun | 3, 5, 6, 10, 11 |
| Moon | 3, 6, 11 |
| Mars | 1, 2, 4, 7, 8, 10, 11 |
| Mercury | 3, 5, 6, 11 |
| Jupiter | 6, 10, 11, 12 |
| Venus | 6, 8, 11, 12 |
| Saturn | 1, 4, 7, 8, 9, 10, 11 |
| Lagna | 1, 3, 6, 10, 11 |

## Subject: Mercury
| Contributor | Benefic houses |
|-------------|----------------|
| Sun | 5, 6, 9, 11, 12 |
| Moon | 2, 4, 6, 8, 10, 11 |
| Mars | 1, 2, 4, 7, 8, 9, 10, 11 |
| Mercury | 1, 3, 5, 6, 9, 10, 11, 12 |
| Jupiter | 6, 8, 11, 12 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 11 |
| Saturn | 1, 2, 4, 7, 8, 9, 10, 11 |
| Lagna | 1, 2, 4, 6, 8, 10, 11 |

## Subject: Jupiter
| Contributor | Benefic houses |
|-------------|----------------|
| Sun | 1, 2, 3, 4, 7, 8, 9, 10, 11 |
| Moon | 2, 5, 7, 9, 11 |
| Mars | 1, 2, 4, 7, 8, 10, 11 |
| Mercury | 1, 2, 4, 5, 6, 9, 10, 11 |
| Jupiter | 1, 2, 3, 4, 7, 8, 10, 11 |
| Venus | 2, 5, 6, 9, 10, 11 |
| Saturn | 3, 5, 6, 12 |
| Lagna | 1, 2, 4, 5, 6, 7, 9, 10, 11 |

## Subject: Venus
| Contributor | Benefic houses |
|-------------|----------------|
| Sun | 8, 11, 12 |
| Moon | 1, 2, 3, 4, 5, 8, 9, 11, 12 |
| Mars | 3, 5, 6, 9, 11, 12 |
| Mercury | 3, 5, 6, 9, 11 |
| Jupiter | 5, 8, 9, 10, 11 |
| Venus | 1, 2, 3, 4, 5, 8, 9, 10, 11 |
| Saturn | 3, 4, 5, 8, 9, 10, 11 |
| Lagna | 1, 2, 3, 4, 5, 8, 9, 11 |

## Subject: Saturn
| Contributor | Benefic houses |
|-------------|----------------|
| Sun | 1, 2, 4, 7, 8, 10, 11 |
| Moon | 3, 6, 11 |
| Mars | 3, 5, 6, 10, 11, 12 |
| Mercury | 6, 8, 9, 10, 11, 12 |
| Jupiter | 5, 6, 11, 12 |
| Venus | 6, 11, 12 |
| Saturn | 3, 5, 6, 11 |
| Lagna | 1, 3, 4, 6, 10, 11 |

---

## Strength thresholds (per-sign SAV)

A house is read through the SAV of the sign on it:

- **Below 25** — weak
- **25–30** — average
- **Above 30** — strong

Also weigh the BAV of the house lord's own sign, and the BAV of the relevant
planet in the sign it occupies, when judging a specific significator.
