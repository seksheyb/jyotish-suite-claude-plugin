# Jaimini Analysis Methodology

Full framework. Execute every step in sequence. Never skip.

---

## STEP 0 — Chart Baseline *(Run once per session; display as structured block)*

### 0A — Chara Karaka Computation

Use the **Sapta Karaka (7-planet) system**. Exclude Rahu from ranking. For Rahu: effective degree = 30° − Rahu's degree within sign.

Rank Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn by degree within sign (highest → lowest):

| Rank | Karaka | Abbr | Signifies |
|------|--------|------|-----------|
| 1st | Atmakaraka | AK | Soul, self, core life theme |
| 2nd | Amatyakaraka | AmK | Career, counsel, mind |
| 3rd | Bhratrukaraka | BK | Siblings, courage |
| 4th | Matrukaraka | MK | Mother, home, emotions |
| 5th | Putrakaraka | PK | Children, creativity, intellect |
| 6th | Gnatikaraka | GK | Enemies, illness, competition |
| 7th | Darakaraka | DK | Spouse, partnerships, desire |

Tiebreaker: same degree → higher minutes/seconds wins.

**Close-degree flag (within 1°):** When two adjacent Karakas are within 1° of each other, flag explicitly — both planets partially carry both Karaka qualities. Read their themes as shared throughout the analysis.

**Planetary War check:** After ranking, check every sign with 2+ planets. If any two warring planets (excludes Sun, Moon, Rahu, Ketu) are within 1° in the same sign:
- Lower degree wins; higher degree is **defeated**
- Defeated planet's Karaka significations are weakened throughout
- Flag: *"[Planet] is [Karaka] but defeated in Planetary War — [Karaka] themes are suppressed"*
- AK defeated → soul themes obstructed; AmK defeated → career hampered; DK defeated → partnership themes weakened
- Planets within 2°–5° → "close contention" — flag, note the gap

**Degree flags for AK and AmK** (and DK for relationship questions):
- 🟢 **Pushkara Navamsa/Bhaga** → Karaka empowered; delivers results with ease (load `degree-flags.md`)
- 🔴 **Mrityu Bhaga** → Karaka suppressed; struggles to deliver even if sign placement is strong (load `degree-flags.md`)
- 🟡 **Sandhi** (0°–1° or 29°–30°) → Karaka unstable; inconsistent delivery
- 🔴 **Gandanta** (within 3°20' of water→fire junction) → Karaka karmically charged; themes require conscious effort
- Net modifier: state explicitly — a debilitated AmK at Pushkara may outperform a well-placed AmK at Mrityu Bhaga

**Vargottama:** Planet in same sign in D1 and D9. Karaka promise is undiminished — soul-level endorsement. Flag [Vo]. Vargottama AK = soul themes exceptionally clear this lifetime.

### 0B — Swamsha Identification

Swamsha = AK's sign in D9. Represents soul's deepest desires and dharmic path.

**Compute from AK's D1 degree:**
- Identify AK's sign element → determine starting Navamsa sign (Fire→Aries, Earth→Capricorn, Air→Libra, Water→Cancer)
- Count which 3°20' segment AK's degree falls in (1st = 0°00'–3°19', 2nd = 3°20'–6°39'... 9th = 26°40'–29°59')
- Count that many signs forward from starting sign → Swamsha

Cross-check against provided D9 data. Flag any discrepancy.

Swamsha planet interpretations:
- Sun/Jupiter in/aspecting Swamsha → government, administration, teaching, authority
- Venus → arts, beauty, luxury, diplomacy, creative fields
- Mercury → business, communication, trade, analysis
- Saturn → service, mass scale, discipline-based work, systems
- Mars → technical, engineering, real estate, defense
- Moon → public-facing, caregiving, travel, fluids
- Ketu → spirituality, occult, liberation, research
- Rahu → unconventional path, foreign, innovation, mass media

### 0C — Karakamsha

Karakamsha = Swamsha sign placed as Lagna in D1. Shows career nature and destiny in material world.

- Locate Swamsha sign in D1 → Karakamsha Lagna
- Read Whole Sign houses from Karakamsha Lagna:
  - 1st → self-expression in career
  - 2nd → wealth through profession
  - 5th → intellect and creativity applied to work
  - 7th → business partnerships
  - 9th → dharma, higher purpose
  - 10th → profession, public reputation
- Apply Jaimini Drishti on Karakamsha Lagna sign (see Section 1)
- Planets in the Karakamsha sign in D1 → conjunct Karakamsha, co-shape destiny nature

### 0D — Arudha Pada Computation

**Formula:** Count N signs from house to its lord's sign. Count N more signs from lord's sign → Arudha.
**Exception:** If Arudha falls in the same sign as the house OR 7th from it → use 10th from the house instead.

| Arudha | House | Signifies |
|--------|-------|-----------|
| AL | 1st | Self-image, social identity, worldly perception |
| UL | 12th | Marriage, committed partnerships |
| A2 | 2nd | Wealth manifestation, family image |
| A3 | 3rd | Efforts, skills, communication image |
| A6 | 6th | Enemies, debts, service image |
| A7 | 7th | Business partnerships, spouse image |
| A10 | 10th | Career image, public reputation |
| A11 | 11th | Gains, networks, desire fulfilment |

**Bhava vs Arudha distinction — always read both:**
- **Bhava** = actual house → real events, inner reality, karma
- **Arudha** = Pada → perception, social image, material manifestation
- Strong Bhava + weak Arudha = real results not publicly visible
- Strong Arudha + weak Bhava = visible image without inner substance
- Always note divergence when it exists

### 0E — Argala Pre-Map

Load `references/argala.md` for full rules. Pre-map for AL and Swamsha sign at baseline.

**Primary Argala positions (from reference sign):**
- 2nd sign → Argala (wealth, speech, sustenance)
- 4th sign → Argala (happiness, home)
- 11th sign → Argala (gains, fulfilment)
- 5th sign → secondary Argala (intellect, past karma)

**Virodha Argala (obstruction):**
- 12th obstructs 2nd; 10th obstructs 4th; 3rd obstructs 11th; 9th obstructs 5th

Argala is effective only when planets causing it outnumber obstructing planets.

### 0F — Chara Dasha Period

Load `references/computation.md` for full Chara Dasha computation rules. Display:
- Current Mahadasha Rasi + dates
- Current Antardasha Rasi + dates
- Full Dasha sequence table with start/end dates
- Next shift within 2 years

---

## SECTION 1 — Jaimini Core Mechanics

### 1A — Jaimini Drishti (Sign Aspects)

**Sign-based only. No orbs. No degree-based Parashari aspects within Jaimini steps.**

Load `references/jaimini-drishti.md` for complete aspect tables.

**Three rules:**
- **Movable signs** (Aries, Cancer, Libra, Capricorn) → aspect all Fixed signs except the adjacent one
- **Fixed signs** (Taurus, Leo, Scorpio, Aquarius) → aspect all Movable signs except the adjacent one
- **Dual signs** (Gemini, Virgo, Sagittarius, Pisces) → aspect all other Dual signs without exception

All Jaimini Drishti is **mutual** — if A aspects B, then B aspects A.

**Mutual aspect consequence:**
When two signs mutually aspect, their planets exchange influence bidirectionally — a sign-level quasi-conjunction. For each mutual aspect pair:
- List planets in both signs
- Describe how each set's Karaka roles and natural nature modify the other sign's themes
- When both signs contain question-relevant Karakas → their themes are fused; read as co-operating forces
- A mutual aspect between two Karaka-rich signs is one of the strongest indicators in Jaimini — weight heavily

**Strict prohibition:** Never apply Parashari degree-based aspects (Jupiter's 5th/9th, Mars's 4th/8th, Saturn's 3rd/10th by degree) within Jaimini analysis steps. If relevant, add as labeled supplementary note after Jaimini analysis only.

**Nodes:** Rahu and Ketu cast aspects based on the sign type they occupy (movable/fixed/dual).

**Aspect quality weighting:**
- Sign with AK aspecting → soul sanction; highest weight regardless of planet's nature
- Sign with AmK aspecting → career activation
- Sign with DK aspecting → partnership/desire themes fused
- Natural benefics (Jupiter, Venus, unafflicted Mercury, waxing Moon) aspecting → supportive, uplifting
- Natural malefics (Saturn, Mars, Sun, Rahu, Ketu) aspecting → challenging, demanding, or intensifying
- Empty sign aspecting → aspect operates at reduced intensity; follow sign lord's placement

### 1B — Bhava vs Arudha

Always read both layers for every house/topic (see 0D above). Never report only one layer.

---

## SECTION 2 — Question Mapping

Before analysis begins, identify:
1. Primary Karaka(s) for the question
2. Primary Bhava(s) and Arudha(s)
3. Swamsha relevance (career, dharma, destiny → Swamsha is always a primary reference)
4. Yes/No flag → reverse analysis required

| Topic | Primary Karaka | Primary Arudha | Secondary |
|-------|---------------|----------------|-----------|
| Career | AmK | A10 | AK, Karakamsha |
| Marriage/Spouse | DK | UL, A7 | 7th Bhava |
| Finance | AK | AL, A2, A11 | AmK |
| Children | PK | A5 | 5th Bhava |
| Health | GK | A6 | 6th Bhava |
| Mother | MK | A4 | 4th Bhava |
| Siblings | BK | A3 | 3rd Bhava |
| Spirituality | AK | Swamsha | Karakamsha |
| Social Status | — | AL | 1st Bhava |
| Enemies | GK | A6 | 6th Bhava |

---

## SECTION 3 — Full Jaimini Analysis *(Execute for D1 and D9 separately)*

### Step A — Karaka Placement

- Sign of primary Karaka planet; sign type (movable/fixed/dual)
- Signs it aspects via Jaimini Drishti → any relevant to question (contain AL, UL, Arudha, other Karaka)?
- Signs aspecting back → mutual? List planets in both signs; describe bidirectional exchange
- **Aspect quality:** apply weighting framework from Section 1A for each aspecting sign
- **Conjunctions in Karaka's sign:**
  - List all co-occupants; identify their Karaka roles
  - Higher degree = dominant in conjunction
  - Karaka blending: e.g., AK + AmK in same sign → soul and career themes fused and inseparable
  - 3+ planets in sign → focal concentration zone; all their Karaka themes interlinked
  - Natural benefics in conjunction → support Karaka delivery; malefics → friction or intensity
- **3rd sign from Karaka** → planets here = effort and initiative toward Karaka themes
- **6th sign from Karaka** → planets here = obstacles or service conditions; malefic = obstruction; benefic = surmountable challenge

### Step B — Arudha Pada Analysis

- Sign of relevant Arudha
- Planets in Arudha sign → Karaka role, natural nature, how their presence shapes the perceived image
- Multiple planets in Arudha → all their themes merge into how that Arudha is perceived
- Signs aspecting Arudha via Jaimini Drishti → apply aspect quality weighting for each
- **Mutual aspects involving Arudha sign:**
  - List planets in both signs; describe bidirectional exchange of Karaka themes
  - DK sign mutually aspecting UL → partnership desire and marriage image are fused
- Argala on Arudha sign (2nd, 4th, 11th) → which planets intervene and how?
- Virodha Argala (12th, 10th, 3rd) → stronger or weaker than Argala?

### Step C — UL Analysis *(Marriage/relationship questions)*

- UL sign; planets in UL sign
- Lord of UL sign → placement (house + sign) in D1
- 2nd from UL → marriage sustenance; malefics here = strain or disruption
- 7th from UL → separation, transformation, or end of marriage themes
- DK's sign → does it aspect UL via Jaimini Drishti?
- DK's D9 sign → soul-level desire for partnership; what does DK's Swamsha indicate?

### Step D — Swamsha Analysis *(Career, dharma, destiny questions)*

- Swamsha sign; planets in Swamsha in D9
- Signs aspecting Swamsha via Jaimini Drishti → planets in aspecting signs
- Apply Swamsha planet interpretations (from Step 0B)
- **Mutual aspects on Swamsha sign** → describe bidirectional exchange; planets in mutually aspecting sign co-author the soul's dharmic expression
- AK's sign aspecting Swamsha → soul's own themes are directly blessing the dharmic path

### Step E — Karakamsha Analysis *(Career and destiny questions)*

- Karakamsha Lagna sign in D1
- Planets in the Karakamsha sign → conjunct Karakamsha Lagna; apply conjunction rules
- Houses from Karakamsha (1st, 2nd, 5th, 7th, 9th, 10th) and their planets
- **Jaimini Drishti on Karakamsha Lagna sign:**
  - Signs aspecting Karakamsha → apply aspect quality weighting
  - AK sign aspecting → soul endorses the destiny path
  - AmK sign aspecting → career themes powerfully activated through destiny
  - Mutual aspects involving Karakamsha sign → planets in mutually aspecting sign co-shape career/dharma path

### Step F — AK Dignity Check *(Every reading)*

- AK in D1: exalted/own/friendly → soul themes less obstructed; debilitated → extra effort required; combust → soul themes submerged by Sun/ego themes
- AK in D9 (Swamsha): debilitated or enemy sign → deep soul-level conflict or karmic burden
- Note net AK strength as a modifier for all conclusions in the reading

---

## SECTION 4 — Chara Dasha Computation & Interpretation

Load `references/computation.md` for full Chara Dasha computation algorithm.

### 4A — Key Computation Rules (Summary)

**Sign lordship (Jaimini):**
Aries→Mars; Taurus→Venus; Gemini→Mercury; Cancer→Moon; Leo→Sun; Virgo→Mercury;
Libra→Venus; Scorpio→Mars/Ketu; Sagittarius→Jupiter; Capricorn→Saturn; Aquarius→Saturn/Rahu; Pisces→Jupiter

**Period assignment:** Count signs from Rasi to its lord's sign (forward) = Dasha years.
- Lord in same sign → 12 years
- Count > 12 → subtract from 12

**Starting Rasi:**
- Movable Lagna → start from Lagna, proceed zodiacally
- Fixed Lagna → start from Lagna, proceed anti-zodiacally
- Dual Lagna → start from 9th sign from Lagna, proceed zodiacally

**Birth balance formula:**
Elapsed = (Lagna degree within sign ÷ 30) × Total years of first Dasha sign
Balance = Total years − Elapsed

### 4B — Chara Dasha Interpretation

For operating Mahadasha and Antardasha Rasi:

1. **Read the Dasha Rasi** — Karakas in it? Arudhas in it? What house from Lagna? From AL?
2. **Jaimini Drishti on Dasha Rasi** — aspecting signs and their planets co-deliver results
3. **Argala on Dasha Rasi** — 2nd, 4th, 11th from Dasha Rasi; what intervenes?
4. **Antardasha relationship** — does Antardasha Rasi aspect Mahadasha Rasi? If yes → active, productive sub-period. No aspect → more internalized or neutral results
5. **Karaka activation** — does Dasha Rasi contain or aspect (via Jaimini Drishti) the question's primary Karaka? If yes → those Karaka themes are activated
6. **Arudha activation** — does Dasha Rasi coincide with or aspect AL, A10, UL, or relevant Arudha? Material manifestation is likely in this period

---

## SECTION 5 — Mandatory Execution Sequence

Every reading, in this exact order:

**Step 1 — Baseline display** (Step 0 — shown once, referenced throughout)
**Step 2 — Question classification** (state primary Karaka, Arudha, yes/no flag)
**Step 3 — D1 Analysis** (Steps A–F using D1 data)
**Step 4 — D9 Analysis** (Steps A–F using D9 data)
**Step 5 — Reverse Question Analysis** *(yes/no only)* — reverse the question; repeat Steps A–F for D1 and D9; compare signature strength to calibrate confidence
**Step 6 — Composite Reading** using this priority order:

| Priority | Factor |
|----------|--------|
| 1 | Chara Dasha activation — is relevant Karaka/Arudha activated? |
| 2 | AK and Swamsha — soul-level permission for the outcome |
| 3 | Relevant Arudha Pada strength — material manifestation capacity |
| 4 | Argala on relevant sign — intervention supporting or blocking? |
| 5 | Jaimini Drishti on relevant Bhava and Arudha — aspecting sign quality |
| 6 | D9 Karaka confirmation — soul-contract level support |
| 7 | Bhava vs Arudha divergence — real outcome vs visible outcome |

**Composite output must include:**
- Chart promise at Bhava level (actual/real)
- Chart promise at Arudha level (perceived/material)
- Whether they align or diverge — and what that means practically
- Degree caveats (Planetary War, Mrityu Bhaga, Gandanta, Pushkara on Karakas)
- Confidence: **Strong / Moderate / Unclear** — state why

**Step 7 — Dasha Timing Output:**
- Current Mahadasha Rasi + what it activates for this question
- Current Antardasha Rasi + how it modifies
- Next 2–3 Dasha shifts + improvement or reduction of prospects
- Most favorable upcoming Rasi period for the question's outcome — which Karakas and Arudhas it activates, and why
