# KP Natal — Full Methodology

## Core principles

1. **Cuspal Sub Lord (CSL) decides.** The sub-lord of every house cusp determines whether matters of that house will fructify in this life. This is the central KP rule.

2. **Signification through stars.** A planet primarily signifies the houses owned/occupied by its star-lord, secondarily its own occupation/ownership. Star-lord effect > own effect.

3. **Houses are computed Placidus, not whole-sign.** KP uses unequal houses based on actual astronomical computation. A house is a swathe of degrees, not a sign.

4. **KP ignores classical benefic/malefic.** Saturn isn't bad, Jupiter isn't good — what matters is *what they signify*. A "malefic" Saturn signifying your 11th house gives gain. A "benefic" Jupiter signifying your 12th gives loss.

5. **Vimshottari is the only dasha system used.** Yogini, Ashtottari, etc. are not standard in KP.

6. **Ruling Planets are the cross-confirmation.** For event timing, the dasha lord must be a Ruling Planet (computed at moment of question or decision).

## Event timing — the eight-step KP natal read

### Step 1 — Identify houses for the matter
Use `references/house-combinations.md`. Define positive set, negative set, and primary house.

### Step 2 — Examine primary CSL
The single most important step. CSL signifies positive → fructifies. CSL signifies negative → denied. CSL signifies both → check sub-sub-lord. CSL signifies neither → unlikely in current life.

**STOP HERE if the CSL signifies the negative set only.** Deliver the verdict "will not fructify in this life" and do **not** proceed to significator or dasha analysis for this house — the cuspal sub-lord is final (see Critical Rule 4 in `orchestration-notes.md`). No favourable dasha, exaltation, or dignity argument overrides a CSL that denies the matter. Only continue to Step 3 when the CSL signifies the positive set (or both, after the sub-sub-lord tiebreak resolves positive).

### Step 3 — List significators (4 levels)
For each relevant house:
- **L1 (strongest):** Planets in the star of the occupant of the house
- **L2:** Planets occupying the house
- **L3:** Planets in the star of the house-lord
- **L4 (weakest):** The house-lord itself

Add Rahu/Ketu if conjunct any planet in the relevant house — they take on signification of conjunct planets.

Add planets in conjunction with Rahu/Ketu — they're amplified for that house's signification.

### Step 4 — Identify fruitful significators
A significator is "fruitful" if its sub-lord ALSO signifies the positive set. A significator with a sub-lord in the negative set is barren — it cannot deliver the matter even when its dasha runs.

This is why some seemingly favourable dashas don't bring results — the dasha lord signifies the right house, but its sub-lord betrays it.

### Step 5 — Compute Ruling Planets
At moment of reading + native's current location. Show calculation per `references/ruling-planets.md`.

### Step 6 — Find DBA-Sookshma matches
Run `scripts/find_fruitful_window.py` against baseline.json to scan the
Vimshottari tree for MD/BD/AD/SD windows whose lords are fruitful
significators — do not walk the dasha tree by eye. The fructification window is when:
- MD lord is a fruitful significator
- BD lord is a fruitful significator
- AD lord is a fruitful significator
- SD lord is a fruitful significator (narrows to days)
- Ideally, all are also Ruling Planets

The ideal scenario: 3-4 of these layers align AND are RP. That's a high-confidence date prediction.

### Step 7 — Transit confirmation
Run `scripts/compute_transits.py` for the candidate window(s) found in Step 6
to get actual transiting positions rather than reasoning about them in prose.
At the predicted DBA-Sookshma window:
- Where is transit Jupiter? (slow-moving — gives the year/month)
- Where is transit Sun? (gives the month)
- Where is transit Moon? (gives the day)
- Are they transiting through stars of the significators?

Transit Moon passing through the star of an active significator on a day already in the dasha window = the precise day.

### Step 8 — Verdict
Render the event-timing conclusion in the **VERDICT box** exactly:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VERDICT — [event]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Outcome        : [YES / NO / QUALIFIED YES]
Confidence     : [High / Medium / Low]
Primary window : [MD-BD-AD-SD lords] — [start date] to [end date]
Secondary      : [other qualifying DBA-SD windows, or "—"]
Why            : CSL of [house] signifies [houses]; fruitful significators
                 [planets]; RP cross-check [pass/fail]; transit [confirmation]
Caveats        : [combust/sandhi/retro/barren-sub-lord notes, or "—"]
Action         : [what the native should do / watch for]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Life reading methodology

For a comprehensive life reading without a specific question:

### Walk through all 12 CSLs
For each cusp, render a **per-cusp HOUSE box** exactly:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HOUSE [N] — [matters of this house]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CSL          : [planet] — signifies [houses]  →  [FRUITFUL / DENIED / MIXED]
Significators : L1 [..]  L2 [..]  L3 [..]  L4 [..]
Flags        : [combust/sandhi/gandanta/mrityu_bhaga, or "—"]
Verdict      : [will fructify / denied / conditional] — [one line]
Timing       : [dasha periods most likely to activate, or "—"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Identify dominant life themes
Close the reading with the **LIFE THEMES box**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIFE THEMES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Succeeds     : [houses with strong positive CSL + strong significators]
Blocked      : [houses with negative CSL — karmic / requires conscious work]
Unstable     : [CSLs at sandhi/gandanta, or in star of 6/8/12 lord]
Soul's theme : [one-line synthesis of the chart's curriculum]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- Houses with strong positive CSL + strong significators = recurring themes that succeed
- Houses with negative CSL = blocked / karmic / requires conscious work

### Identify weak houses
- CSLs in star of 6, 8, 12 lord = struggle areas
- CSLs at sandhi or gandanta = unstable matters

### Synthesis
Weave the cuspal verdicts into a life narrative. What does the chart say is the soul's curriculum?

## Special rules

**Retrograde planets:** Give effects of the planet in whose star they sit. So a retrograde Saturn in Jupiter's star gives Jupiter-house effects, not Saturn-house effects. Critical for significator analysis.

**Combust planets (within 8.5° of Sun):** Weakened as significators but not zeroed out. Note as caveat.

**Planets at sandhi (last 0°30' or first 0°30' of a sign):** Cannot give clear results during their dasha. Effects spill into next sign's house signification — read accordingly.

**Mrityu Bhaga:** A KP-specific list of "death-degrees" in each sign. A planet at MB is weakened; in horary, a planet at MB cannot fulfill the matter.

**Pushkara navamsa / degree:** Auspicious — strengthens a planet's signification.

**Gandanta degrees (29° of water sign / 0° of fire sign):** Highly unstable. A CSL at Gandanta = matter starts and stops repeatedly.

**Empty houses:** Use the lord of the cusp + planets in the lord's star. An empty house is not weak by itself — KP doesn't penalize empty houses the way Parashari does.

**Multiple planets in one star:** All co-signify; the closest to nakshatra mid-point is the strongest representative.

## Common natal KP errors

- Reading sign-lord effects when star-lord should dominate
- Skipping sub-sub-lord when CSL is mixed
- Using natal Moon's nakshatra instead of transit Moon for RP
- Using whole-sign houses instead of Placidus
- Applying classical benefic/malefic logic
- Ignoring retrograde rule for significators
- Predicting timing from Mahadasha alone (need DBA-SD)
- Confusing horary RP (moment of question) with natal RP (moment of reading)
