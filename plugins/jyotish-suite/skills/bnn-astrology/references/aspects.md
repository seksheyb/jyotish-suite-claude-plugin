# BNN Aspects Reference (Graha Drishti)

BNN uses Parashari degree-based planetary aspects. Aspects are as significant as physical occupation — an aspecting planet modifies a sign's themes even when no planet occupies it.

---

## Aspect Rules

Every planet casts a 7th aspect (opposition). Additional special aspects:

| Planet | Special Aspects (in addition to 7th) |
|--------|--------------------------------------|
| Mars | 4th and 8th |
| Jupiter | 5th and 9th |
| Saturn | 3rd and 10th |
| Rahu | 5th and 9th (applied in BNN) |
| Ketu | 5th and 9th (applied in BNN) |

**How to count aspects:** Count signs from the planet's sign (inclusive). E.g., Mars in Leo:
- 4th from Leo = Scorpio → Mars aspects Scorpio
- 7th from Leo = Aquarius → Mars aspects Aquarius
- 8th from Leo = Pisces → Mars aspects Pisces

---

## Full Aspect Table — All Planets

Pre-compute aspects from each planet's sign using the rules above.

**Example for Sekshey's chart (reference only):**
- Sun in Cancer → 7th aspect on Capricorn
- Moon in Aquarius → 7th on Leo
- Mars in Leo → 4th on Scorpio, 7th on Aquarius, 8th on Pisces
- Mercury in Leo → 7th on Aquarius
- Jupiter in Cancer → 5th on Scorpio, 7th on Capricorn, 9th on Pisces
- Venus in Leo → 7th on Aquarius
- Saturn (R) in Capricorn → 3rd on Pisces, 7th on Cancer, 10th on Libra
- Rahu in Sagittarius → 5th on Aries, 7th on Gemini, 9th on Leo
- Ketu in Gemini → 5th on Libra, 7th on Sagittarius, 9th on Aquarius

Always compute fresh from the user's actual chart data.

---

## Orb Framework

Orb = degree difference between aspecting planet and any planet in the aspected sign (or the sign cusp if empty).

| Orb | Classification | Weight |
|-----|---------------|--------|
| Within 3° | Tight / Exact | High — behaves like conjunction in intensity |
| 3°–7° | Moderate | Moderate — clear influence |
| Beyond 7° | Loose | Low — background influence only |

**For empty aspected signs:** orb cannot be precisely calculated without a reference planet. Apply the aspect as a sign-level influence at moderate weight. If the sign lord is available, use degree difference to lord's position.

---

## Mutual Aspects

When two planets aspect each other and are within 3° of degree:
- Their significations **fuse bidirectionally** — treat as quasi-conjunction
- Neither can be read in full isolation for this chart
- Friendly mutual aspect → cooperative fusion of both Karaka significations
- Enemy mutual aspect → persistent tension or conflict between both planets' themes
- The fused signification is one of the most powerful indicators in BNN — weight heavily

**How to detect:** If Planet A aspects Planet B's sign AND Planet B aspects Planet A's sign, AND their degree difference is within 3° → mutual aspect confirmed.

---

## Aspect Quality Framework

For every aspecting planet, determine quality before applying:

1. **Natural relationship to Karaka** (from karaka-tables.md Section 1C):
   - Friend → supportive aspect; uplifts the aspected sign's themes
   - Enemy → restricting aspect; pressures or complicates the aspected sign
   - Neutral → conditional; read by sign field and context

2. **Degree flags on aspecting planet** (from degree-flags.md):
   - Combust aspecting planet → aspect is weakened/suppressed
   - Mrityu Bhaga aspecting planet → carries suppression into aspected sign
   - Pushkara aspecting planet → aspect is amplified and empowered
   - Gandanta aspecting planet → karmically charged and unstable aspect
   - Defeated in Planetary War → aspect is weakened
   - Retrograde aspecting planet → aspect present but delayed or internalized

3. **Orb** — tight (within 3°) = high weight; moderate (3°–7°) = medium; loose (7°+) = low

4. **Net quality statement:** *"[Planet] aspects [sign] — [relationship: friendly/enemy/neutral] — orb [X°] — [degree flags] — net effect: [supports / restricts / complicates] the [position name]'s delivery"*

---

## Empty Sign Rule

When a BNN position (2nd, 5th, 7th, 9th, 12th, etc. from Karaka) contains no occupying planets:

**Do NOT declare it "empty" until you have checked for aspects.**

Protocol:
1. Check which planets aspect this sign via Graha Drishti
2. For each aspecting planet: apply quality framework above
3. If aspecting planets exist → the position is not empty; list each and state their influence
4. Only declare "truly empty" when: no occupying planet AND no aspecting planet
5. Truly empty → sign lord's placement as tertiary indicator; check sign lord's own degree flags

---

## Aspect Pre-Map (Run at Start of Every Reading)

Before beginning Steps A–F, pre-map all aspects across the D1 chart:

For each planet, list which signs it aspects and at what orb to any occupying planets in those signs. This pre-map is referenced throughout the reading without recomputing each time.

Format:
```
ASPECT PRE-MAP (D1):
Mars (Leo 15°26'):
  → Scorpio (4th): [occupants if any, orb if any]
  → Aquarius (7th): Moon 21°23' — orb 5°57' — moderate
  → Pisces (8th): [occupants if any]

Jupiter (Cancer 26°44'):
  → Scorpio (5th): [occupants if any]
  → Capricorn (7th): Saturn 09°35' — orb 17°09' — loose
  → Pisces (9th): [occupants if any]

[...continue for all planets...]

MUTUAL ASPECTS (within 3°):
  [list any pairs]
```
