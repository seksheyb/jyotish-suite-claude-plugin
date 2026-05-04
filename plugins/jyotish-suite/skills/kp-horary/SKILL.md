---
name: kp-horary
description: >
  Trigger this skill immediately and exclusively when the user types "/kp-horary" anywhere in their
  message. This skill performs Krishnamurti Paddhati (KP) horary astrology — answering specific
  yes/no/timing questions using a horary number 1-249, the moment of the question, and the location
  of the questioner. The skill computes the horary chart from scratch using pyswisseph (KP New
  ayanamsa, Placidus cusps), computes Ruling Planets with full calculation shown, performs cuspal
  sub-lord analysis with question-specific house combinations, cross-checks via Ruling Planets, and
  delivers a verdict with timing window and confidence level. Always use this skill — never attempt
  KP horary work without it. Also trigger when user says "KP horary", "horary number", "ask the chart",
  "Prashna in KP", or provides a 1-249 number with a question.
---

# KP Horary Astrology Skill

## Overview
This skill performs full Krishnamurti Paddhati horary readings:
1. Collect question, horary number (1-249), location of questioner, time of question
2. Compute the horary chart from scratch (pyswisseph, KP New ayanamsa, Placidus cusps)
3. Compute Ruling Planets — show the full calculation
4. Identify question category and apply standard KP house combinations
5. Cuspal sub-lord analysis of relevant house cusps
6. Significator analysis and Ruling Planet cross-check
7. Timing via dasha-bhukti-antara of activated significators
8. Verdict with confidence level and caveats

**Reference files — load before every reading:**
| File | Load When |
|------|-----------|
| `references/methodology.md` | Always — full KP horary analysis framework |
| `references/house-combinations.md` | After question category is identified |
| `references/249-table.md` | When mapping horary number to Lagna degree |
| `references/ruling-planets.md` | When computing and interpreting RP |

**Computation scripts:**
| File | Purpose |
|------|---------|
| `scripts/compute_horary_chart.py` | Generate horary chart from number + time + place |
| `scripts/compute_ruling_planets.py` | Compute RP with full calculation breakdown |

---

## PHASE 1 — Question Collection

When `/kp-horary` is triggered, ask:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KP Horary Reading

Please provide:

1. Your question (specific, time-bound, yes/no preferred)
2. Horary number (1 to 249) — pick mentally without looking
3. Location of the questioner (city, country)
   [defaults to New Delhi, India if not specified]
4. Time of question
   [defaults to "now" — current IST if not specified]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Validation:**
- Number must be 1-249. Reject otherwise.
- Question should be specific. If vague ("will I be happy?"), ask for narrower framing.
- Time must include timezone or city — if "now", use system time + IST default.

---

## PHASE 2 — Chart Computation

Run `scripts/compute_horary_chart.py` with arguments: number, datetime (ISO), latitude, longitude, timezone.

The script outputs:
- **Lagna**: derived from horary number 1-249 (each number = ~1°26'24" arc starting from 0° Aries)
- **Cusps 1-12**: Placidus, with sign-lord, star-lord, sub-lord, sub-sub-lord
- **Planets** (Sun through Ketu, plus Uranus/Neptune/Pluto for reference): longitude, sign, star-lord, sub-lord, sub-sub-lord, retrograde flag
- **Vimshottari dasha** at moment of question

Display the full chart back to the user in a clean markdown table for verification.

**Critical note:** The horary Lagna is determined by the 1-249 number, NOT by the rising sign at the time of the question. The time and place determine planetary positions and dasha — the number determines the Lagna. This is the defining feature of KP horary.

---

## PHASE 3 — Ruling Planets Computation (Show All Work)

Run `scripts/compute_ruling_planets.py` with the same time + place.

The skill must **display the calculation explicitly**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULING PLANETS — Calculation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Time: [datetime + timezone]
Place: [city, lat, long]

1. Day Lord (weekday at sunrise):
   [Day name] → [Planet]

2. Moon's position at this moment:
   • Longitude: [deg-min-sec]
   • Sign: [sign] → Sign Lord: [planet]
   • Nakshatra: [nakshatra] → Star Lord: [planet]
   • Sub: [sub] → Sub Lord: [planet]

3. Lagna's position at this moment (rising at this place):
   • Longitude: [deg-min-sec]
   • Sign: [sign] → Sign Lord: [planet]
   • Nakshatra: [nakshatra] → Star Lord: [planet]
   • Sub: [sub] → Sub Lord: [planet]

4. RP Set (deduplicated, in standard order):
   [Lagna Sub Lord, Lagna Star Lord, Lagna Sign Lord,
    Moon Sub Lord, Moon Star Lord, Moon Sign Lord,
    Day Lord]
   = [final list]

Strongest RP: Lagna Sub Lord = [planet]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Apply Krishnamurti's strength order: Lagna Sub > Lagna Star > Lagna Sign > Moon Sub > Moon Star > Moon Sign > Day Lord. Retrograde planets (except nodes) are excluded unless their depositor is also RP.

---

## PHASE 4 — Question Category & House Combinations

Identify the category. Load `references/house-combinations.md` for the full table. Common ones:

| Category | Houses | Logic |
|----------|--------|-------|
| Marriage | 2, 7, 11 | 7 (spouse), 2 (family), 11 (fulfillment of desire) |
| Career / new job | 6, 10, 11 | 10 (profession), 6 (employment/service), 11 (gain) |
| Job change | 1, 5, 9, 10 (leaving) + 2, 6, 10, 11 (new job) | Two-step analysis |
| Promotion | 2, 6, 10, 11 | Same as new job; 2 = financial gain |
| Litigation (own case) | 1, 6, 11 (win); 5, 8, 12 (loss) | 6 = victory over opponent |
| Litigation (opponent's case) | 7, 12, 5 (their loss) | Mirror houses |
| Property purchase | 4, 11, 12 | 4 (property), 12 (investment), 11 (gain) |
| Property sale | 3, 5, 10 | 3 (transfer), 5 (negation of 4), 10 (cash flow) |
| Childbirth | 2, 5, 11 | 5 (child), 2 (family addition), 11 (fulfillment) |
| Loan / money | 2, 6, 11 (gain); 8, 12 (loss) | 6 = borrowing |
| Travel (long-term) | 3, 9, 12 | 9 (long journey), 12 (foreign), 3 (short) |
| Travel (foreign settlement) | 9, 12 + 7 (away from home) | |
| Lost item (recovery) | 2, 11 (recovery); 6, 8, 12 (loss) | |
| Health / disease cure | 1, 5, 11 (cure); 6, 8, 12 (disease) | |
| Education / exam | 4, 9, 11 (success); 8, 12 (failure) | |

**Rule of fructification:** A house "matter" fructifies if the **Cuspal Sub Lord (CSL) of that house signifies the relevant house combination** AND is connected (by occupation, ownership, or signification) to the supporting houses.

---

## PHASE 5 — Cuspal Sub Lord Analysis

For each relevant house cusp, examine its Sub Lord:

```
Cusp [N] — [house name]
  Sub Lord: [planet]
    • Owns houses: [...]
    • Occupies house: [...]
    • In star of: [planet] → which signifies houses [...]
    • Itself signifies (via star + own): houses [...]
    • Connection to question's positive set: [yes/no, which houses]
    • Connection to question's negative set: [yes/no]
    • Verdict for this cusp: [favourable / unfavourable / mixed]
```

The CSL of the **primary house** (e.g., 7th for marriage, 10th for career) is decisive. If it signifies the positive combination, matter fructifies. If it signifies the negative set (6/8/12 for marriage, 5/8/12 for career), matter is denied.

---

## PHASE 6 — Ruling Planets Cross-Check

Compare the Ruling Planets list against the significators of the relevant houses.

**Strong YES:** RP planets are also significators of the positive house combination, and the CSL of the primary house is in the RP list (or in the star/sub of an RP planet).

**Strong NO:** RP planets are significators of the negative set; primary CSL is unconnected to RP.

**Mixed / conditional:** Some RP align, some don't — adjust confidence accordingly.

---

## PHASE 7 — Timing

Identify the running Vimshottari Dasha-Bhukti-Antara at the moment of the question. The matter fructifies during the joint period when:

1. **Mahadasha lord** is a significator of the positive house combination (or its sub-lord is)
2. **Bhukti lord** is also a significator
3. **Antara lord** is also a significator
4. Ideally, **Sookshma lord** completes the chain
5. **Transit confirmation:** Jupiter and Sun transiting through significator stars at the time of fructification

If the current DBA all signify the positive combo and CSL is favourable, fructification is **near-term** (within current Antara). If only MD-Bhukti align but Antara doesn't, fructification waits for the next favourable Antara.

Provide the **specific window**: "Between [start date] and [end date], during the [MD]-[BD]-[AD]-[SD] period."

---

## PHASE 8 — Verdict

Deliver a structured verdict:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERDICT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Question: [restated]
Horary number: [N]

Outcome: [YES / NO / CONDITIONAL]

Confidence: [HIGH / MEDIUM / LOW]
  • CSL of primary house: [favourable / unfavourable]
  • Ruling Planets alignment: [strong / partial / weak]
  • Dasha alignment: [supports / does not support]

Timing window: [date range, with DBA period]

Key supporting factors:
  • [...]
  • [...]

Caveats / what could change the call:
  • [degree-sensitive flags, e.g., CSL near sandhi]
  • [retrograde considerations]
  • [sub-sub-lord conflicts]
  • [transit confirmation needed]

Recommended action: [specific, actionable]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Critical Rules

1. **Never override the CSL with sentiment.** If the CSL of the 7th says no, the marriage doesn't happen — even if Jupiter is exalted in the 7th.
2. **Always show RP calculation.** The user must see how each ruling planet was derived.
3. **Show degrees and lord chains.** Every claim about a planet's signification must be traceable.
4. **Confidence ≠ certainty.** A high-confidence call still has caveats. State them.
5. **Don't combine charts.** The horary chart stands alone — never mix in natal data.
6. **Question framing matters.** If question is mis-asked, redirect before reading.
7. **Outer planets (Uranus/Neptune/Pluto)** — display for reference but do not use in core KP analysis. KP is a 9-graha system.
8. **Retrograde planets** — when retrograde, a planet gives the result of the planet in whose star it sits, not its own. Apply this rule when retrograde significators appear.

---

## Output Style
- Authoritative, precise, advisory tone (per user's professional output preferences)
- Show calculations explicitly — user wants to see the work
- Use tables liberally for cusps, planets, significators
- Pyramid principle — verdict first in summary, then full reasoning below
- Never hedge unnecessarily; if the chart says no, say no
