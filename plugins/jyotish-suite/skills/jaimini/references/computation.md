# Computation Reference

Detailed computation rules for Chara Karakas, Navamsa (D9), Arudha Padas, and Chara Dasha.

---

## 1 — Navamsa (D9) Computation

Each D1 sign is divided into 9 Navamsas of 3°20' each.

**Starting Navamsa sign by D1 sign element:**
| D1 Sign | Element | First Navamsa Starts In |
|---------|---------|------------------------|
| Aries, Leo, Sagittarius | Fire | Aries |
| Taurus, Virgo, Capricorn | Earth | Capricorn |
| Gemini, Libra, Aquarius | Air | Libra |
| Cancer, Scorpio, Pisces | Water | Cancer |

**Full D9 mapping table:**

| Degrees within D1 sign | Ari | Tau | Gem | Can | Leo | Vir | Lib | Sco | Sag | Cap | Aqu | Pis |
|-----------------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0°00'–3°19' | Ari | Cap | Lib | Can | Ari | Cap | Lib | Can | Ari | Cap | Lib | Can |
| 3°20'–6°39' | Tau | Aqu | Sco | Leo | Tau | Aqu | Sco | Leo | Tau | Aqu | Sco | Leo |
| 6°40'–9°59' | Gem | Pis | Sag | Vir | Gem | Pis | Sag | Vir | Gem | Pis | Sag | Vir |
| 10°00'–13°19' | Can | Ari | Cap | Lib | Can | Ari | Cap | Lib | Can | Ari | Cap | Lib |
| 13°20'–16°39' | Leo | Tau | Aqu | Sco | Leo | Tau | Aqu | Sco | Leo | Tau | Aqu | Sco |
| 16°40'–19°59' | Vir | Gem | Pis | Sag | Vir | Gem | Pis | Sag | Vir | Gem | Pis | Sag |
| 20°00'–23°19' | Lib | Can | Ari | Cap | Lib | Can | Ari | Cap | Lib | Can | Ari | Cap |
| 23°20'–26°39' | Sco | Leo | Tau | Aqu | Sco | Leo | Tau | Aqu | Sco | Leo | Tau | Aqu |
| 26°40'–29°59' | Sag | Vir | Gem | Pis | Sag | Vir | Gem | Pis | Sag | Vir | Gem | Pis |

**Vargottama:** Planet in the same sign in both D1 and D9. The Navamsa sign matches the D1 sign. Flag [Vo].

---

## 2 — Arudha Pada Computation

**Formula:**
1. Identify the house to compute (e.g., 1st house for AL)
2. Identify the lord of that house's sign
3. Count from the house's sign to the lord's sign → N steps (zodiacally forward)
4. Count N more steps from the lord's sign → resulting sign = Arudha Pada

**Exception rule:** If Arudha falls in:
- The same sign as the house → use 10th sign from the house instead
- The 7th sign from the house → use 10th sign from the house instead

**Example — AL for Virgo Lagna:**
- 1st house = Virgo; lord = Mercury; Mercury in Leo
- Count Virgo → Leo = 12 steps (going backward)... use forward: Virgo(1) → Libra(2) → Scorpio(3) → Sagittarius(4) → Capricorn(5) → Aquarius(6) → Pisces(7) → Aries(8) → Taurus(9) → Gemini(10) → Cancer(11) → Leo(12) = 12 steps
- Count 12 from Leo forward: Leo(1)→Vir(2)→Lib(3)→Sco(4)→Sag(5)→Cap(6)→Aqu(7)→Pis(8)→Ari(9)→Tau(10)→Gem(11)→Can(12) = Cancer
- Check: is Cancer = Virgo? No. Is Cancer = Pisces (7th from Virgo)? No.
- AL = Cancer ✓

**Arudha computation table for quick reference:**
Compute all 8 Arudhas (AL, UL, A2, A3, A6, A7, A10, A11) using the same formula.

---

## 3 — Chara Dasha Computation

### Step 1 — Jaimini Sign Lordship

| Sign | Primary Lord | Secondary Lord (if applicable) |
|------|-------------|-------------------------------|
| Aries | Mars | — |
| Taurus | Venus | — |
| Gemini | Mercury | Jupiter (if Mercury is weak) |
| Cancer | Moon | — |
| Leo | Sun | — |
| Virgo | Mercury | Jupiter (if Mercury is weak) |
| Libra | Venus | — |
| Scorpio | Mars | Ketu (per Jaimini tradition) |
| Sagittarius | Jupiter | Mars (if Jupiter is weak) |
| Capricorn | Saturn | Mars (if Saturn is weak) |
| Aquarius | Saturn | Rahu (per Jaimini tradition) |
| Pisces | Jupiter | Venus (if Jupiter is weak) |

For dual-lord signs: use the lord that is stronger (by sign placement, exaltation, own sign) or more prominently placed (in Kendra or Trikona from Lagna).

### Step 2 — Assign Dasha Years to Each Sign

Count zodiacal signs forward from the sign to its lord's sign, *exclusive* of
the starting sign — the lord's own sign counts as 1 step, the next as 2, and
so on. That count = Dasha years for that sign.

**Special rule:** Lord in same sign → 12 years (there is no zero-step case).

Because the count is always between 1 and 11 signs away (a 12-sign zodiac,
exclusive count, lord never being "13 signs away" from its own sign), it can
never exceed 12 years — there is no ">12, subtract 12" case to handle.

**Dasha years by sign — example for Virgo Lagna:**
This must be computed fresh for each chart. Do not assume fixed values.

### Step 3 — Determine Starting Rasi and Direction

| Lagna Type | Starting Rasi | Direction |
|-----------|--------------|-----------|
| Movable (Aries, Cancer, Libra, Capricorn) | Lagna sign | Zodiacal (forward) |
| Fixed (Taurus, Leo, Scorpio, Aquarius) | Lagna sign | Anti-zodiacal (reverse) |
| Dual (Gemini, Virgo, Sagittarius, Pisces) | 9th sign from Lagna | Zodiacal (forward) |

**For Virgo Lagna (dual sign):** Dasha starts from 9th sign from Virgo = Taurus. Proceeds zodiacally: Taurus → Gemini → Cancer → Leo → Virgo → Libra → Scorpio → Sagittarius → Capricorn → Aquarius → Pisces → Aries → back to Taurus.

### Step 4 — Compute Birth Balance

**Formula:**
- Elapsed = (Lagna degree ÷ 30) × Total years of first Dasha sign
- Balance at birth = Total years − Elapsed

**Example:** Lagna at 11°10' in Virgo (dual → first Dasha sign = Taurus).
- If Taurus Dasha = 9 years (lord Venus; count Taurus→Libra = 6... verify per chart)
- Elapsed = (11.17 ÷ 30) × 9 = 0.372 × 9 = 3.35 years
- Balance = 9 − 3.35 = 5.65 years = 5 years, 7 months, 24 days

**Display full Dasha sequence:**

| Dasha Rasi | Years | Start Date | End Date |
|-----------|-------|-----------|---------|
| [First sign] | | [birth date + balance] | |
| [Second sign] | | | |
| ... | | | |

Show at least 6–8 periods into the future.

### Step 5 — Antardasha Computation

Within each Mahadasha Rasi, the Antardasha sequence:
- Starts from the same Rasi as the Mahadasha
- Proceeds in the same direction as the Mahadasha
- **Each Antardasha duration = Mahadasha years ÷ 12** — an EQUAL twelfth for
  every sign, regardless of that sign's own individual Chara-Dasha years.
  Example: a 6-year Mahadasha gives twelve 6-month Antardashas. (Verified
  against multiple sources; a sign's own chara-dasha-years value is recorded
  for reference/display only and does not affect its Antardasha duration.)
- The full cycle of all 12 signs completes within the Mahadasha exactly,
  since 12 × (Mahadasha years ÷ 12) = Mahadasha years by construction.

---

## 4 — Chara Karaka Degree Computation (For Reference)

When computing Chara Karakas manually:

1. Extract each planet's degree within its sign (ignore the sign itself; use only degrees 0–29°59')
2. For Rahu: effective degree = 30° − Rahu's degree within sign
3. Rank all 7 planets (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn) highest to lowest
4. Assign Karakas in sequence: AK (1st) through DK (7th)

**Sekshey's D1 — for reference/verification:**
| Planet | Sign | Degree in Sign | Effective Degree | Notes |
|--------|------|---------------|-----------------|-------|
| Sun | Cancer | 12°54' | 12°54' | |
| Moon | Aquarius | 21°23' | 21°23' | |
| Mars | Leo | 15°26' | 15°26' | |
| Mercury | Leo | 09°10' | 09°10' | |
| Jupiter | Cancer | 26°44' | 26°44' | |
| Venus | Leo | 13°34' | 13°34' | |
| Saturn | Capricorn | 09°35' | 09°35' | Retrograde |
| Rahu | Sagittarius | 24°20' | 30°−24°20' = 5°40' | Excluded from ranking |

Ranked by degree (descending): Jupiter 26°44' → Moon 21°23' → Mars 15°26' → Venus 13°34' → Sun 12°54' → Saturn 09°35' → Mercury 09°10'

Note: Mercury (09°10') and Saturn (09°35') are within 0°25' of each other → close-degree flag applies. Both share GK and DK qualities.
