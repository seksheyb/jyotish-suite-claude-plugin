# Jyotish Suite — Optimization Blueprint

*Compiled 2026-07-23 from a 7-agent parallel analysis workflow (6 skill analysts + 1 cross-cutting
compute-layer analyst, ~778K tokens of analysis). This is a recommendation document — no code has
been changed.*

---

## Executive summary

The optimization you asked about — methodology in skills, execution roles as agents with earmarked
models, deterministic math in Python scripts, parallel fan-out, orchestration — **already exists,
~95% complete, on the local branch `refactor-efficient`** (commit `4febb09`, one commit ahead of
`main`, plus a final WIP layer in `git stash@{0}`). The untracked `.pyc` bytecode in `lib/` and
`scripts/` on your working tree is the compiled residue of that branch: every `.pyc` was verified to
match the branch sources byte-for-byte at the code-object level.

**The recommended path is therefore not "design from scratch" but:**

1. **Merge `refactor-efficient` + apply `stash@{0}`** — recovers the shared lib, 6 baseline
   scripts, 5 shared agents, and rewritten wave-orchestrator SKILL.mds.
2. **Apply the refinements below** that the analysis identified beyond what the branch has:
   per-agent *effort* earmarks, per-school synthesis model tuning (opus is over-provisioned for 4 of
   6 schools), 3 missing delta scripts, reference-file consolidation, and conditional fan-out
   scaling.

---

## 1. The headline discovery: `refactor-efficient` branch

| What | Where | Status |
|---|---|---|
| `lib/jyotish_primitives.py` (512 L) | commit `4febb09` | Pure math/lookup: signs, nakshatras, Vimshottari, navamsa, sub-lords, degree flags, combustion orbs, Mrityu Bhaga, Pushkara. Zero I/O, zero ephemeris deps. |
| `lib/ephemeris.py` (368 L) | `4febb09` (+stash) | The **only** pyswisseph/pytz consumer. 3 chart-mode assemblers: `parashari_natal_chart()`, `kp_natal_chart()`, `kp_horary_chart()`. Fails loudly if deps missing. |
| `lib/chart_io.py` (138 L) | `4febb09` | Expands a user-*pasted* chart into the same JSON shape `ephemeris.py` produces — baselines work identically for computed or pasted charts. |
| 6 × `scripts/compute_<school>_baseline.py` (350–960 L) | `4febb09` (+stash for vedic) | One deterministic baseline JSON per school. Explicitly retire the 4 old per-skill scripts (incl. the byte-identical duplicated `compute_ruling_planets.py`). |
| 5 × `agents/*.md` | `4febb09` | `chart-calculator` (haiku), `chart-verifier` (haiku), `baseline-runner` (haiku), `unit-analyzer` (sonnet), `synthesizer` (opus). |
| 6 × rewritten `SKILL.md` + `references/orchestration-notes.md` | `4febb09` | Each skill becomes a **wave orchestrator**: collect → verify → Wave 0 baseline → Wave 1 parallel unit-analyzers → Wave 2 synthesis. |
| `.gitignore` (excludes `__pycache__`) | `4febb09` | Fixes the current hygiene problem (untracked bytecode on main). |
| Final ~5% WIP | `git stash@{0}` | Adds `NAKSHATRA_GANA`/`gana_of`, node exalt/debil tables, `lagna_longitude`, ~180 lines to `compute_vedic_baseline.py`. |

**Verified on this machine:** Python 3.14.2 matches the `cpython-314` bytecode tag; `pyswisseph
2.10.3.2` and `pytz` are installed; the recovered sources recompile to byte-identical code objects.

Recovery commands (verified to work):

```bash
git merge refactor-efficient        # or rebase/cherry-pick 4febb09
git stash apply stash@{0}           # the final WIP layer
```

---

## 2. Target architecture (5 layers)

```
commands/<school>.md          thin slash-command triggers (unchanged)
        │
skills/<school>/SKILL.md      WAVE ORCHESTRATOR — conversational gates (chart intake,
        │                     confirm display, question intake, mode menu) + dispatch logic.
        │                     Methodology/judgment rules stay here + orchestration-notes.md.
        ▼
agents/                       SHARED EXECUTION ROLES (school passed as parameter)
  chart-calculator  [haiku]   birth data → chart JSON  (lib/ephemeris.py)
  chart-verifier    [haiku]   pasted chart → JSON + verification display  (lib/chart_io.py)
  baseline-runner   [haiku]   Wave 0: run compute_<school>_baseline.py, return file path
  unit-analyzer     [sonnet]  Wave 1: N parallel copies — one unit each (house / Karaka /
        │                     cusp / relative / year / dasha window)
  synthesizer       [opus*]   Wave 2: weave unit blocks into the final reading
        ▼                     (*tune per school — see §3)
scripts/ + lib/               DETERMINISTIC LAYER — all arithmetic and table lookup
        ▼
skills/<school>/references/   interpretive prose only, lazy-loaded by agents
```

Design invariants the analysis confirmed:

- **Conversational gates cannot be delegated.** Chart intake, the "Confirmed" verification gate,
  and mode menus are multi-turn — they stay in the orchestrator skill (all 6 analysts agree).
- **Baseline JSON stays out of orchestrator context** — baseline-runner writes it to a file and
  returns the path; unit-analyzers Read only their slice.
- **Scripts never interpret; agents never compute.** Every number an agent cites must originate
  in the baseline JSON.

---

## 3. Model & effort matrix

The branch earmarks **models** but not **effort**. Recommended matrix (branch defaults + analyst
refinements):

### Shared agents

| Agent | Model | Effort | Notes |
|---|---|---|---|
| chart-calculator | haiku | low | Script wrapper; zero judgment |
| chart-verifier | haiku | low | Parse + format; re-loop on user correction |
| baseline-runner | haiku | low | Run script, return path + 1-line gloss |
| unit-analyzer | sonnet | **medium default, high for dense units** | See per-school below |
| synthesizer | **per school** | — | Branch hard-codes opus for all — over-provisioned for 4 of 6 schools |

### Synthesis tier per school (the main tuning delta vs the branch)

| School | Synthesizer | Why |
|---|---|---|
| jaimini-astrology | **opus / medium** | Cross-domain reconciliation: D1 vs D9 Karaka confirmation, Bhava/Arudha divergence, Chara Dasha activation — most contradiction-prone |
| bnn-astrology (full/reverse readings) | **opus / medium** | 10-priority weighting across up to 7 analyst outputs |
| bnn-astrology (single-Karaka questions) | sonnet / high — or inline, no agent | Not enough threads to reconcile |
| vedic-astro | **sonnet / high** | 8-tier weighting, single methodology — dense but single-domain |
| kp-natal | **sonnet / high** | CSL+significators+RP+dasha+transit merge; single-methodology |
| kp-horary | **sonnet / high** | One verdict chain; opus is waste |
| lal-kitab | **sonnet / high** | Analyst explicit: "opus would be overkill" — single-domain throughout |

### Unit-analyzer effort per unit type

| Unit type | Effort |
|---|---|
| Vedic D1-house / D9-house analysis | high |
| Lal Kitab baseline diagnostician (Phases 2–6 narrative), timing narrative (8D) | high |
| KP cusp verdicts, Jaimini D1/D9 Steps A–F, BNN per-Karaka, dasha-timing, family members | medium |
| Varshphal year prose, final summary card compression | low (haiku candidate for the summary card) |

---

## 4. Deterministic vs probabilistic — the canonical split

Rule of thumb that emerged from all 6 analyses: **arithmetic, table lookup, set membership, and
tree search → script; meaning, weighting, narrative, and contradiction resolution → LLM.**

Worst hallucination hotspots found (all resolved by the branch baselines):

| Skill | Hotspot currently done by LLM on `main` |
|---|---|
| vedic-astro | Full degree-flag scan (Gandanta/Mrityu Bhaga/Pushkara/Sandhi/Planetary War), aspect pre-map, navamsa derivation, dasha balance from Moon nakshatra, dignity, AK/AmK |
| kp-natal | 4-level significator derivation, retrograde/combustion/sandhi flags, fruitful-window search over the dasha tree |
| kp-horary | Per-cusp occupation/ownership/star-lord chains, RP-vs-significator set intersections, MD/BD/AD/SD membership checks |
| jaimini | Chara Karaka ranking, Arudha count-forward formula, Argala counting, **Chara Dasha wraparound math** (computation.md states the rule 3 contradictory ways), Jaimini Drishti table |
| bnn | 12×7 Mrityu Bhaga grid, sign-counting for 2nd/12th/5th/9th/3rd/11th/7th from each Karaka × 7 positions, mutual-aspect detection |
| lal-kitab | Sign→fixed-house remap, pakka-ghar 5-table lookup, sleeping-planet detection, 6 rin boolean triggers, 8 teva predicates, **Phase 8D 4-signal timing engine** (densest hotspot in the suite) |

Stays LLM (correctly): question classification, retrograde/conjunction interpretation, aspect
*quality* narrative, D1/D9 convergence meaning, verdict synthesis + confidence, upaay tiering,
honesty-boundary framing.

---

## 5. Parallelization plan per school

| School | Fan out (Wave 1, parallel) | Do NOT split |
|---|---|---|
| vedic-astro | D1-house analyst ∥ D9-house analyst ∥ dasha-timing ∥ reverse-question (binary Qs, same wave). Full readings: house clusters (career+wealth / relationships+children / health / dharma) | — |
| kp-natal | Life Reading: 4 trine-group analysts (1/5/9, 2/6/10, 3/7/11, 4/8/12) | Event Timing mode is a hard dependency chain — single dense analyst |
| kp-horary | **Minimal fan-out.** Primary + supporting cusps feed one verdict; scripts already remove the LLM latency. The branch's per-cusp unit-analyzer wave is defensible but low-value — cap it at the 2–5 relevant cusps, or run single-analyst | Don't fan per-cusp beyond relevant houses |
| jaimini | D1 analyst ∥ D9 analyst ∥ reverse (binary) ∥ Chara-Dasha timeline | — |
| bnn | Per-Karaka analysts (up to 5 in full readings) ∥ dasha-timing ∥ reverse. **Scale to question scope: 0 agents (single-Karaka Q, inline) → 7 (full + reverse)** | **D1+D9 for the same Karaka must stay in ONE agent** — methodology forbids standalone D9 reading. Give every analyst the full mutual-aspect map to avoid slice blindness |
| lal-kitab | Mode D (full reading) only: 8A natal-house ∥ 8B family ∥ 8C varshphal ∥ 8D timing, all off the finalized baseline; join at Phase 9 upaay prescriber | Phases 2–6 narrative = ONE diagnostician pass (cross-rin compounding, teva tie-breaks). Never per-house micro-agents for 8A. Phase 9 must wait for all Phase-8 agents |

Common pattern: **conditional dispatch scaled to question scope.** Simple/narrow questions run
inline in the orchestrator with zero agent dispatch; fan-out reserved for full/multi-domain
readings. This is the second main tuning delta vs the branch (which leans wave-always).

A full Workflow engine is **not needed for any single reading** — orchestrator skill + parallel
Agent dispatch covers every case. (Workflow-scale orchestration is only worth it for batch jobs,
e.g. re-running baselines across many charts.)

---

## 6. Shared components — final decisions

### Already shared on the branch (adopt as-is)
- `lib/jyotish_primitives.py`, `lib/ephemeris.py`, `lib/chart_io.py`
- 5 shared agents (parameterized by school) — replaces 6 skills × 5 roles = 30 bespoke agents
- 6 per-school baseline scripts (thin entry points over the lib)
- Chart intake/verification pattern unified in chart-verifier
- Old duplicated scripts deleted (`compute_ruling_planets.py` ×2 — byte-identical today,
  `compute_horary_chart.py`, `compute_sookshma.py`)

### Delta scripts to add (identified by analysts, absent from branch baselines)
1. **`scripts/compute_transits.py`** — forward transit confirmation (Jupiter/Sun/Moon through
   significator stars). kp-natal Step 7 and kp-horary Phase 7 currently *prose-only* — a genuine
   functional gap on both main and the branch.
2. **`find_fruitful_window`** (extend kp baselines) — scan the Vimshottari tree for MD/BD/AD/SD
   windows whose lords are fruitful significators; currently "examine and find" LLM inspection.
3. **`lk_upaay_conflict_check`** (extend lal-kitab baseline) — candidate-upaay generation from
   active rins/teva + conflict-pair and pregnancy/health contraindication flags from
   `upaay_catalog.md` §11. Missing a contraindication under long context is a real risk today.

### Reference-file consolidation (untouched by the branch — real drift found)
| Problem | Action |
|---|---|
| `degree-flags.md` ×3 (vedic 108 L / jaimini 126 L / bnn 121 L) — same numeric tables, three divergent prose wrappings (142–191 changed lines pairwise) | Numbers now live in `jyotish_primitives.py` (source of truth). Reduce each copy to school-specific *interpretation* of flags, or one shared reference + per-school notes |
| `house-combinations.md` byte-identical in kp-natal/kp-horary, **but** the Python `HOUSE_COMBINATIONS` constants have already diverged (18 vs 20 keys, renamed/split categories) | Decide: genuine methodological split (document it) or drift (reconcile). Then make the .md files mirror the constants |
| `ruling-planets.md` byte-identical ×2; both restate computation steps the script owns | Single shared reference; cut the "Steps 1–5 computation" section, keep only verdict-usage guidance |
| kp-horary `methodology.md` ≈ near-duplicate restatement of SKILL.md's phases | Fold unique content (special rules, failure modes) into SKILL.md; delete or shrink the file |
| `jaimini-drishti.md` contains visible self-correcting scratch work ("wait — adjacent means…", three successive "corrected" tables) | **Clean immediately** — dangerous to load verbatim into an LLM context. Aspect table is now `build_drishti_map()`; keep only the rationale prose |
| `249-table.md` (kp-horary) | Trim drastically — the mapping is 100% inside the baseline script; keep only concept + sandhi caveat |

---

## 7. Risks & guardrails (from the analysts)

1. **Synthesis quality is the product.** Decomposition only works because Wave 2 sees *all* unit
   blocks + the full baseline. Under-resourcing the synthesizer or starting it before all analysts
   return (esp. lal-kitab Phase 9) is the failure mode to guard against.
2. **Slice blindness.** Parallel unit-analyzers must each receive the shared aspect/mutual-aspect
   map, not just their unit's slice (BNN cross-Karaka aspects; dasha lord not among dispatched
   Karakas must be explicitly added).
3. **Methodology invariants:** D9 never read standalone (bnn/vedic); the two KP horary Lagnas never
   mixed (branch already documents this well); Lal Kitab Varshphal ≠ Tajaka solar-return Varshphal.
4. **Farman/citation provenance:** scripts compute *which* rule fired; the agent must still cite
   from the reference text — keep rule-IDs in script output so citations are lookups, not recall.
5. **Don't over-orchestrate.** Simple questions: zero dispatch. kp-horary: minimal fan-out. Adding
   agents where there's no independent work adds latency and synthesis risk, not quality.
6. **Honesty rules** (lal-kitab Phase 0 boundary statements, 8D no-specific-dates) must survive the
   refactor — they live in the orchestrator + synthesizer prompts, easy to drop accidentally.

### 7.1 Guard status — verified against the `refactor-efficient` branch (2026-07-23)

| Risk | Status | Evidence / gap |
|---|---|---|
| 1 — synthesis barrier | **Guarded by design** | `synthesizer.md`: "runs once, last, after every unit-analyzer has returned"; receives *all* unit blocks + full baseline path; upaay tiering happens in Wave 2 for Modes A–D |
| 1 — synthesis under-resourcing | **GAP (created by this blueprint)** | §3 downgrades synthesis opus→sonnet/high for 4 schools with no quality gate. Guard added: downgrade is contingent on a side-by-side spot-check (Phase 2), and Phase 5 gains a synthesis-quality eval, not just numeric snapshots |
| 1 — premature upaay tiering | **BRANCH DEFECT** | lal-kitab **Mode E dispatches 3 parallel workers, one per upaay tier** — fragments the single cross-tier consistency judgment (conflict pairs span tiers; same upaay must not appear twice). Fix in Phase 2: one upaay unit-analyzer, tiering stays in the synthesizer |
| 2 — slice blindness | **Guarded by design** | Every unit-analyzer receives the path to the *full* baseline.json (complete aspect/mutual-aspect map, all Karakas) as ground truth; workers scope their analysis, not their data |
| 2 — undispatched dasha lord | **Partial gap** | BNN Wave 1 dispatches per-Karaka workers only; if the running dasha lord isn't among the question's Karakas, its Steps A–F run nowhere (synthesizer is forbidden to re-derive units). Fix in Phase 2: dispatch rule — always add a dasha-lord unit for timing/activation questions |
| 3 — D9 never standalone | **Guarded by design** | BNN branch SKILL.md: "Each worker covers D1 and D9 and runs BNN Steps A-F". (Vedic's D1/D9 analyst split is methodology-legal there: D9 reconciles at synthesis) |
| 3 — KP two Lagnas | **Guarded by design** | Baseline JSON keeps them separate; orchestration-notes documents "never mix" with per-Lagna usage rules |
| 3 — LK no-D9/Vimshottari, Varshphal ≠ Tajaka | **Guarded by design** | Branch SKILL.md: "uses no D9 and no Vimshottari — if supplied, display but exclude with an explicit note"; Varshphal is the age-table engine in the baseline. Add a one-line Tajaka-distinction note in references (Phase 4) |
| 4 — Farman/citation provenance | **Guarded by design** (rin) / **plan** (upaay) | `compute_lalkitab_baseline.py` emits exact citation strings per rin record (e.g. `"farman": "Farman 8, Vol 2 (1940)"`) — citations are lookups. Upaay contraindications stay recall-based until the Phase 3 conflict-check script lands |
| 5 — over-orchestration | **Guarded by plan (Phase 2)** | Branch already scales workers per mode and narrows domain questions to 1–2 Karakas, but always dispatches (no inline path for trivial questions), Mode A is always 12 workers, and kp-horary fans per-cusp. All three are Phase 2 items |
| 6 — honesty rules survive | **GAP** | Rules survived but **relocated** into lazy-loaded `orchestration-notes.md` (branch SKILL.md itself: 0 matches vs 4 on main). The Phase-0 boundary rule now lives in a file not guaranteed to be loaded at Phase 0; no-specific-dates is not in the synthesizer's standing prompt. Fix in Phase 2: hoist both into SKILL.md orchestrator text and the synthesizer dispatch payload |

---

## 8. Recommended execution plan

| Phase | Work | Est. effort |
|---|---|---|
| 0 | Merge `refactor-efficient`, apply `stash@{0}`, commit (sources + .gitignore; bytecode disappears from status) | minutes |
| 1 | Smoke-test all 6 baselines end-to-end on a known chart (deps verified present) | small |
| 2 | **Orchestration-contract audit + tuning** (see §7.1): effort earmarks; per-school synthesis tiers (§3) *gated on a side-by-side quality spot-check before any opus→sonnet downgrade*; conditional-dispatch scaling incl. inline path for trivial questions and kp-horary cusp cap (§5); fix lal-kitab Mode E per-tier upaay split → single upaay unit; add always-dispatch-dasha-lord rule; hoist honesty rules from orchestration-notes into SKILL.md + synthesizer payload | small-medium |
| 3 | Delta scripts: transits, fruitful-window, upaay conflict check (§6) | medium |
| 4 | Reference consolidation + jaimini-drishti cleanup + Varshphal≠Tajaka note (§6, §7.1) | small-medium |
| 5 | Golden-chart regression: one fixed chart per school, baseline JSON snapshot-tested, so future edits to lib/ can't silently shift numbers. **Plus a synthesis-quality eval** (2–3 golden readings per school, judged on weighting fidelity, contradiction handling, honesty caveats) — the gate for the §3 synthesis-tier downgrades | medium, high value |

---

## Appendix — analysis provenance

Workflow run `wf_e8775bf9-342` (2026-07-23): 7 parallel Sonnet agents (5×medium, lal-kitab +
compute-layer at high effort), 778K tokens, ~10 min wall-clock. Full per-skill structured reports
in the session scratchpad (`vedic-astro.json`, `kp-natal.json`, `kp-horary.json`,
`jaimini-astrology.json`, `bnn-astrology.json`, `lal-kitab.json`, `compute-layer.json`).
