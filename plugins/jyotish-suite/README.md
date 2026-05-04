# Jyotish Suite

Six rigorously-scripted Vedic astrology systems for Claude Code, packaged as a single plugin.

## Slash commands

| Command         | What it does                                                                                  |
| --------------- | --------------------------------------------------------------------------------------------- |
| `/vedic-astro`  | Classical Parashari reading on a pre-computed D1 + D9                                         |
| `/bnn`          | Brighu Nadi reading using natural Karakas + Nadi flow methodology                             |
| `/jaimini`      | Jaimini reading with Chara Karakas, Arudha Padas, Swamsha, Argala, Chara Dasha                |
| `/lal-kitab`    | Lal Kitab — natal, rin diagnosis, varshphal, or upaay (Pt. Roop Chand Joshi)                  |
| `/kp-natal`     | KP natal reading or event-timing prediction with Sookshma dasha + Ruling Planets              |
| `/kp-horary`    | KP horary — answer a question via number 1–249 + moment + place                               |

## Inputs

- **`/vedic-astro`, `/bnn`, `/jaimini`** — pre-computed D1 + D9 chart in the standard format the skill expects.
- **`/lal-kitab`** — pre-computed Vedic D1 chart (the skill re-maps it to the fixed-house frame).
- **`/kp-natal`** — pre-computed natal KP chart as markdown: cuspal positions with sign/star/sub/sub-sub lords, planetary positions with full lord chain, significators, dasha sequence.
- **`/kp-horary`** — horary number (1–249), exact moment of the question (date, time, timezone), and location.

## Methodology

Each skill loads its own `SKILL.md` and any references / scripts under its directory. None of them guess methodology — they execute against locked classical references:

- `vedic-astro` — Nakshatras, Padas, degrees, Parashari aspects, Vimshottari Dasha
- `bnn-astrology` — Brighu Nadi: natural Karakas, sign fields, flow positions, trine support, growth positions, opposition, degree flags (Mrityu Bhaga, Pushkara, Gandanta, Sandhi, Planetary War, combustion)
- `jaimini-astrology` — Chara Karakas, Arudha Padas, Swamsha, Argala, Chara Dasha
- `lal-kitab` — Pt. Roop Chand Joshi's Farmans (1939–1952): pakka ghar, sleeping planets, six rins, ranked upaay with citations
- `kp-natal` — KP New ayanamsa, cuspal sub-lord analysis, significators, Sookshma (4th-level) dasha, Ruling Planets
- `kp-horary` — Computes the chart from scratch using `pyswisseph`; KP New ayanamsa, Placidus cusps; cuspal sub-lord analysis with question-specific house combinations; Ruling Planets cross-check

## Requirements

The two **KP skills** (`/kp-natal`, `/kp-horary`) compute charts using the [`pyswisseph`](https://pypi.org/project/pyswisseph/) Python package. The four other skills (`/vedic-astro`, `/bnn`, `/jaimini`, `/lal-kitab`) accept pre-computed charts and have no runtime dependencies.

Before using the KP skills, install `pyswisseph` in the Python environment Claude Code executes scripts in:

```bash
pip install pyswisseph
```

If you hit `ModuleNotFoundError: No module named 'swisseph'` when running a KP command, that's the cause — install the package and retry.

## Notes

- All skills will ask for any missing inputs before proceeding — they don't guess.
- KP scripts ship with the plugin under each KP skill's `scripts/` directory and are invoked automatically by the skill.

## License

MIT
