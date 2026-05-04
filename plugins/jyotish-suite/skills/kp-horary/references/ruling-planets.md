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

## Computation steps (skill must show all)

### Step 1 — Day Lord
The lord of the weekday at the moment of question, counted from sunrise of that location.
- Sunday → Sun
- Monday → Moon
- Tuesday → Mars
- Wednesday → Mercury
- Thursday → Jupiter
- Friday → Venus
- Saturday → Saturn

**Important:** The "weekday" in Vedic system runs from sunrise to next sunrise. If question is asked between midnight and sunrise, the day-lord is still the previous day's lord.

### Step 2 — Moon's position
Compute Moon's tropical longitude at moment of question, subtract KP New ayanamsa to get sidereal longitude.
- **Sign** (which 30° segment) → Sign Lord
- **Nakshatra** (which 13°20' segment within sign) → Star Lord (Vimshottari sequence)
- **Sub** (sub-division within nakshatra) → Sub Lord

### Step 3 — Lagna's position
Compute the rising sign at the moment + place of question (NOT the horary Lagna from the 249-number — that's separate; for RP we use the actual rising Lagna).

Same triple: Sign Lord, Star Lord, Sub Lord.

### Step 4 — Compile RP set
List all seven planets above in strength order. Deduplicate (same planet may appear in multiple roles — count once but note its multiple roles).

### Step 5 — Apply exclusions
- **Retrograde planets (except Rahu/Ketu)** are normally excluded from RP. Exception: if the retrograde planet's depositor (sign-lord) is also a Ruling Planet, then keep it.
- **Combust planets** (within 8.5° of Sun) are weakened but not excluded.
- **Rahu/Ketu special rule:** If Rahu or Ketu is in a sign owned by an RP planet, OR is conjunct an RP planet, OR is in the star of an RP planet — Rahu/Ketu becomes the strongest RP for that question (representing the "agent" of the matter).

## Example output format

```
Time of question: 2026-05-01 22:30:00 IST
Place: New Delhi (28.6139°N, 77.2090°E)

Day Lord:
  Friday → Venus

Moon (computed):
  Sidereal longitude: 145°22'15"
  Sign: Leo (120°-150°) → Sign Lord: Sun
  Nakshatra: Purva Phalguni (133°20'-146°40') → Star Lord: Venus
  Sub: within Saturn's portion → Sub Lord: Saturn

Lagna (computed at place):
  Sidereal longitude: 232°10'45"
  Sign: Scorpio → Sign Lord: Mars
  Nakshatra: Anuradha → Star Lord: Saturn
  Sub: Jupiter portion → Sub Lord: Jupiter

RP set (in strength order):
  1. Lagna Sub Lord:  Jupiter
  2. Lagna Star Lord: Saturn
  3. Lagna Sign Lord: Mars
  4. Moon Sub Lord:   Saturn  (already in set as #2)
  5. Moon Star Lord:  Venus
  6. Moon Sign Lord:  Sun
  7. Day Lord:        Venus   (already in set as #5)

Final RP (deduplicated): Jupiter, Saturn, Mars, Venus, Sun

Exclusions check:
  • None of Jupiter/Saturn/Mars/Venus/Sun are retrograde at this time → all retained.
  • Rahu/Ketu check: Rahu in Aquarius (Saturn's sign — RP). Ketu in Leo (Sun's sign — RP).
    Both nodes are eligible to be added as RP.

Final RP set: Jupiter, Saturn, Mars, Venus, Sun, Rahu, Ketu

Strongest single RP: Lagna Sub Lord = Jupiter
```

## Using RP in the verdict

1. **The dasha lord during the fructification window must be in the RP set.** If running Saturn-Mercury and neither is RP → fructification delayed.
2. **CSL of primary house must be in RP set OR in the star/sub of an RP planet.** If yes, strong yes. If no, weak yes or no.
3. **Repeat RP at fructification:** Krishnamurti's principle — the same planets ruling at the moment of question will rule again at the moment of fructification. Use this to forecast: scan upcoming dates for when transit Moon passes through a star whose lord is in the RP set + a sub whose lord is RP.

## Common errors

- Forgetting to subtract KP New ayanamsa (different from Lahiri by ~6 arc-minutes)
- Using natal Moon's nakshatra instead of transit Moon's nakshatra at moment of question
- Including retrograde planets without depositor-check
- Using RP from natal chart instead of moment-of-question chart
- Day-lord error when question is asked in early morning hours before sunrise
