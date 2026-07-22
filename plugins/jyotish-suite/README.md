# Jyotish Suite

Six rigorously-scripted Vedic astrology systems for Claude Code, packaged as a single plugin.
Every skill is a **wave orchestrator**: deterministic math runs in shared Python scripts,
interpretation runs in parallel subagents, and a synthesizer weaves the final reading.

## Slash commands

| Command         | What it does                                                                                  |
| --------------- | --------------------------------------------------------------------------------------------- |
| `/vedic-astro`  | Classical Parashari reading (D1 + derived D9)                                                 |
| `/bnn`          | Brighu Nadi reading using natural Karakas + Nadi flow methodology                             |
| `/jaimini`      | Jaimini reading with Chara Karakas, Arudha Padas, Swamsha, Argala, Chara Dasha                |
| `/lal-kitab`    | Lal Kitab — natal, rin diagnosis, family, varshphal, timing, or upaay (Pt. Roop Chand Joshi)  |
| `/kp-natal`     | KP natal reading or event-timing prediction with Sookshma dasha + Ruling Planets              |
| `/kp-horary`    | KP horary — answer a question via number 1–249 + moment + place                               |

## Inputs

Every skill accepts **either**:

- **Birth data** — date, exact time, and place; the chart is computed by the shared ephemeris
  layer (`lib/ephemeris.py`, sidereal, school-appropriate ayanamsa/houses), **or**
- **A pasted pre-computed chart** — parsed and expanded to the same internal JSON via
  `lib/chart_io.py`, then verified back to you before any analysis.

`/kp-horary` additionally needs the horary number (1–249) and the exact moment + place of the
question. `/lal-kitab` uses only the D1 (no D9, no Vimshottari — the fixed-house frame is
re-mapped automatically).

## Architecture

```
commands/            thin slash-command triggers
skills/<school>/     wave-orchestrator SKILL.md + interpretive references
agents/              shared roles: chart-calculator, chart-verifier, baseline-runner (haiku)
                     unit-analyzer (sonnet) · synthesizer (opus)
scripts/             compute_<school>_baseline.py per school + delta scripts
                     (compute_transits.py, find_fruitful_window.py, lk_upaay_check.py)
lib/                 jyotish_primitives.py (pure math) · ephemeris.py (pyswisseph)
                     · chart_io.py (pasted-chart expansion)
tests/               golden-chart regression harness (run_golden.py)
```

All arithmetic and table lookup (nakshatras, dashas, degree flags, significators, aspect maps,
rin/teva triggers, timing signals) is computed deterministically in the baseline scripts —
subagents interpret those facts; they never recompute them.

## Requirements

The compute layer uses [`pyswisseph`](https://pypi.org/project/pyswisseph/) (and `pytz`) for
ephemeris math — needed by **all six skills** when computing charts from birth data, and by the
two KP skills in every case:

```bash
pip install pyswisseph pytz
```

If you hit `ModuleNotFoundError: No module named 'swisseph'`, that's the cause — install the
package and retry. Pasted-chart intake for the non-KP skills works without ephemeris deps
(`lib/chart_io.py` and `lib/jyotish_primitives.py` are dependency-free).

## Notes

- All skills will ask for any missing inputs before proceeding — they don't guess.
- All scripts live in the shared `plugins/jyotish-suite/scripts/` and `lib/` directories and are
  invoked automatically by the skills (there are no per-skill `scripts/` directories).
- Run `python3 tests/run_golden.py` after touching `lib/` or `scripts/` — it snapshot-tests all
  six baselines against pinned golden charts.

## License

MIT
