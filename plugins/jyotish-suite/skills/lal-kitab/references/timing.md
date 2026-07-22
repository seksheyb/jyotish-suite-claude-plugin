# Lal Kitab Timing Engine — Generic Event-Timing Protocol

This reference is **event-agnostic**. The same convergence engine answers "when will X happen?" for any life event — marriage, career pivot, child, property, foreign travel, health crisis, financial windfall, parental loss, business launch — by changing only the *event-to-significator mapping* in Step 1.

The engine has **four independent timing signals**, then **three modifier filters**, then a **convergence ranker** that produces probability-weighted windows.

---

## Part A — The Four Timing Signals

### Signal 1 — Planetary Maturation Age

Each planet matures *once per lifetime* at a fixed age. At maturation, the planet's full natal verdict (good or bad) lands in that year.

| Planet  | Maturation Age | Notes |
|---------|----------------|-------|
| Jupiter | 16             | Earliest maturation; education, dharma, elder approval |
| Sun     | 22             | Authority, self-identity, father-relationship events |
| Moon    | 24             | Emotional reset, mother-related events, mind-state lock-in |
| Venus   | 25             | Marriage, partnership, aesthetic life direction |
| Mars    | 28             | Decisive action, conflict resolution, sibling events |
| Mercury | 32             | Career articulation, communication-based identity |
| Saturn  | 36             | Career legitimacy, structural reset, social standing |
| Rahu    | 42             | Foreign/unconventional pivot, ambition culmination |
| Ketu    | 48             | Detachment, spiritual reckoning, release events |

**Delivery logic:**
- Planet in **pakka ghar** → maturation delivers fully and positively
- Planet **exalted** → maturation delivers with amplification
- Planet **debilitated** → maturation delivers the *negative* verdict fully
- Planet **sleeping** → maturation year is muted UNLESS an awakening transit/year-ruler activates it
- Planet **combust** (within 10° of Sun) → maturation distorted; the Sun-related domain interferes

**One-time event.** If the maturation year is missed (sleeping planet, no awakening), the result does not re-fire on a 9-year cycle — it has to be awakened via upaay or transit, and even then delivers diminished.

---

### Signal 2 — Year-Ruler from the Age Table

See `varshphal.md` for the full age-to-ruler table. Each year of life is assigned to a planet. The year-ruler is **universal** (same for every native); the natal condition of that planet determines *quality of delivery*.

**Recurrence pattern:** Year-rulership is NOT a clean 9-year cycle per planet — read the actual recurrence off `varshphal.md`'s full age-to-ruler table (e.g. Sun rules ages 1, 10, 19, 32, 40, 44, 50, 56 — not an even 9-year spacing). Major years are flagged in that table: 21 Jupiter major, 24 Venus major, 36 Saturn major, 42 Saturn-Rahu severity, 48 Saturn major, 54 Mars-Saturn, 63 Rahu major.

**Year-ruler delivery rule:**
- Year-ruler is the *primary executor* for that year's events
- An event happens when the year-ruler is **the natural significator of that event** AND **is awake AND well-placed in the natal chart**
- A weak/afflicted year-ruler does not just delay — it can deliver the event's *opposite* (a Venus year for a chart with debilitated Venus can bring separation instead of union)

---

### Signal 3 — The 35-Year House Cycle (House Period Activation)

Each house governs a fixed band of years. The active house's *contents* (resident planets, aspects, owner's condition) become the dominant life themes for that band.

| House | Active Years (1st cycle) | Active Years (2nd cycle) |
|-------|---------------------------|---------------------------|
| 1     | 1–6                       | 36–41                     |
| 2     | 7–12                      | 42–47                     |
| 3     | 13–18                     | 48–53                     |
| 4     | 19–24                     | 54–59                     |
| 5     | 25–30                     | 60–65                     |
| 6     | 31–36 (overlaps)          | 66–71                     |
| 7     | 37–42                     | 72–77                     |
| 8     | 43–48                     | 78–83                     |
| 9     | 49–54                     | 84+                       |
| 10    | 55–60                     |                           |
| 11    | 61–66                     |                           |
| 12    | 67–72                     |                           |

*Note on lineage variance:* Some Lal Kitab lineages use a 5-year-per-house cycle (60-year completion), others 6-year-per-house (72-year completion). This skill uses the 6-year version per the dominant Joshi tradition. The boundaries at 35/36 and 42 overlap deliberately — both Saturn maturation and Saturn-Rahu severity reinforce house transitions there.

**House-period activation logic:**
- During house N's active period, all planets in that house "fire" their natal verdicts
- Planets aspecting that house also fire, but secondary
- The house owner (lord) becomes a co-executor with the active year-ruler
- An empty active house draws results from its lord's current placement

---

### Signal 4 — Jupiter Sanctification

Jupiter's role in Lal Kitab timing is **the sanctifier** — Jupiter aspect or year-ruling presence converts a *possible* event into a *manifest* event with elder/societal/karmic approval.

**Jupiter's aspect rule (Lal Kitab):** Jupiter aspects the 5th, 7th, and 9th houses from its position (same as Parashari, but applied by house number not sign).

**The sanctification protocol:**
- An event signal (Signals 1–3 aligned) without Jupiter involvement = the event happens but **without legitimacy** (e.g. career change without family support, marriage without ceremony, child without acknowledgment)
- An event signal **with** Jupiter aspect on the relevant house OR a Jupiter year-ruler = event manifests with full social/legal/karmic stamp
- Jupiter year-rulers — per `varshphal.md`'s age-to-ruler table: ages 5, 14, 21 (major), 46, 52, 58 — are the strongest sanctification windows
- Jupiter sleeping or debilitated natally = sanctification is structurally weak across the entire life; events tend to happen "off-the-books"

---

## Part B — Event-to-Significator Mapping

Before running the convergence engine, map the event to its Lal Kitab significators. This is the ONLY step that changes between event types.

| Life Event | Primary Houses | Primary Planet(s) | Secondary Planets |
|------------|---------------|-------------------|-------------------|
| Marriage / partnership | 7, 2 | Venus (male) / Jupiter (female) | Moon, Mars |
| Career pivot / job change | 10, 6 | Saturn, Sun | Mercury |
| Career legitimacy / promotion | 10, 11 | Sun, Saturn | Jupiter |
| Business launch | 7, 11, 2 | Mercury, Venus | Mars |
| Child (first) | 5 | Jupiter | Sun (son) / Mercury (daughter) |
| Property / real estate | 4 | Mars, Moon | Saturn |
| Foreign travel / settlement | 12, 9 | Rahu | Moon, Saturn |
| Higher education | 4, 5, 9 | Jupiter, Mercury | — |
| Financial windfall | 2, 11 | Jupiter, Venus | Mercury |
| Loss / setback | 6, 8, 12 | Saturn, Rahu, Ketu | — |
| Health crisis | 6, 8 | Sun (vitality), Mars (acute), Saturn (chronic) | — |
| Parental loss — father | 9 | Sun, Saturn | — |
| Parental loss — mother | 4 | Moon, Venus | — |
| Spiritual turn / detachment | 12, 9 | Ketu, Jupiter | Saturn |
| Legal / litigation | 6, 7 | Mars, Saturn | Rahu |
| Vehicle / accident | 4, 8 | Mars, Saturn | Rahu |
| Public recognition / fame | 10, 11 | Sun, Jupiter | Mercury |

For any event not in this table, derive the mapping from house significations (`pakka_ghar.md`) and karaka logic.

---

## Part C — Modifier Filters

After computing raw convergence windows, apply three filters in order.

### Filter 1 — Sleeping Significator Filter

If a primary significator of the event is **sleeping** in the natal chart, the event will not fire on its scheduled signal alone. The event year requires an **awakening trigger**:

- Year-ruler that aspects or co-houses the sleeping planet
- Transit (use Saturn or Jupiter transits over the sleeping planet — Lal Kitab uses transits sparingly but acknowledges these two)
- Performed upaay for that planet during the prior 40-day window

Without an awakening trigger, the scheduled year passes uneventfully and the event slips to the next convergence window.

### Filter 2 — Rin Overlay Filter

Active rins block or distort the event domains they govern:

| Rin Active | Blocks/Distorts These Events |
|------------|------------------------------|
| Pitri Rin   | Career legitimacy, public recognition, son's birth, property |
| Matri Rin   | Mother-related events, mental peace, home stability, property |
| Stri Rin    | Marriage, partnership, female-child birth, romantic stability |
| Kanya Rin   | Daughter's marriage/health, niece-relations, education |
| Bhratra Rin | Sibling events, business partnerships, communications |
| Atma Rin    | All major events delayed or hollow; spiritual turn forced |

If a rin is active and unaddressed, push the event window forward until the rin's prescribed upaay has been performed for its minimum duration (typically 40 days for activation, longer for completion).

### Filter 3 — Danger Year Filter

The Lal Kitab danger years (21, 36, 42, 48, 54, 63) **subtract** from event probability for *positive* events and **add** to probability for *negative* events:

- Marriage in age 42 → reads as marriage-at-risk, push to next window
- Career pivot in age 36 → reads as forced reset rather than chosen pivot
- Health crisis converging on age 42 → high probability, prepare upaay
- Spiritual turn converging on age 48 (Ketu maturation) + age 63 (Rahu major) → strongly indicated

---

## Part D — The Convergence Engine (Step-by-Step)

For any timing question, run this protocol:

**Step 1 — Map the event.** Use Part B to identify primary houses, primary planet(s), secondary planets.

**Step 2 — Build the signal timeline.** Across the relevant age range (typically current age to age + 15 years, or full life if asked):
- List all year-ruler years where the year-ruler is one of the event's planets (Signals 1 & 2)
- List the maturation age(s) of the event's primary planet(s) (Signal 1)
- Identify which years the event's primary house(s) is in active period (Signal 3)
- Identify all Jupiter years AND years where Jupiter would aspect the event house by current house position (Signal 4)

**Step 3 — Score each candidate year.** For each year in the timeline, count how many of the four signals fire:

| Signals firing | Probability tier |
|----------------|------------------|
| 1 signal       | Weak window — event possible, requires upaay |
| 2 signals      | Moderate window — likely if natal is clean |
| 3 signals      | Strong window — high probability |
| 4 signals      | Triple-fire year — near-certain manifestation |

**Step 4 — Apply Filter 1 (sleeping significator).** Demote any year where the primary significator is sleeping AND no awakening trigger fires that year.

**Step 5 — Apply Filter 2 (rin overlay).** If event-relevant rin is active, push windows forward by minimum 1 year (upaay activation period) for moderate windows; by 2–3 years for severe rin.

**Step 6 — Apply Filter 3 (danger year).** Invert probability for positive/negative events as appropriate.

**Step 7 — Rank and output.** Present the top 2–3 windows ranked by post-filter probability, with the upaay that activates or stabilizes each window.

---

## Part E — Output Template

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIMING SYNTHESIS — [Event Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Event:                 [name]
Primary houses:        [list]
Primary planet(s):     [list with current natal status]
Secondary planets:     [list]

NATAL READINESS:
  [Planet]:    [pakka ghar / exalted / debilitated / sleeping / friendly]
  [House N]:   [occupied by X, aspected by Y, owner condition]

ACTIVE OBSTACLES:
  Rin overlay:    [name if active, else "none"]
  Sleeping:       [list if primary significator is sleeping]
  Danger years:   [list in window]

CANDIDATE WINDOWS:
┌──────┬──────────────┬─────────────────────────────────┬──────────┐
│ Age  │ Year-Ruler   │ Signals Firing                   │ Tier     │
├──────┼──────────────┼─────────────────────────────────┼──────────┤
│ [N]  │ [Planet]     │ [maturation / ruler / house / J]│ [Tier]   │
└──────┴──────────────┴─────────────────────────────────┴──────────┘

PRIMARY WINDOW:    Age [N] — [reasoning]
SECONDARY WINDOW:  Age [N] — [reasoning]
TERTIARY WINDOW:   Age [N] — [reasoning]

WINDOW-ACTIVATION UPAAY:
  For primary window:    [upaay name, Farman ref, when to start]
  For tertiary window:   [upaay name if window needs strengthening]

CAVEATS:
  • Lal Kitab timing is probabilistic, not deterministic
  • Windows are years, not dates — for date precision use KP horary
  • Performed upaay can pull windows forward 1–2 years OR collapse them
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Methodological Notes

**Why no Vimshottari?** Lal Kitab rejects Vimshottari Dasha as a Parashari import. The four signals above are the complete Lal Kitab timing toolkit. Do not graft Mahadasha/Antardasha logic into this engine.

**Why no Tajaka return chart?** Lal Kitab Varshphal is read off the natal chart only. The age-based year-ruler table (Signal 2) is the Lal Kitab substitute for casting a solar return.

**Why probabilistic, not deterministic?** The Farmans are explicit that timing is *modifiable* via upaay. Determinism (e.g. "marriage will happen on March 14, 2027") contradicts the action-bound philosophy. KP horary handles deterministic timing; Lal Kitab handles structural windows + upaay levers.

**Convergence > any single signal.** A single signal firing is weak evidence. The strength of the method is in the convergence — three or four signals overlapping on a year is what makes the window high-probability. Never timing-call from one signal alone.
