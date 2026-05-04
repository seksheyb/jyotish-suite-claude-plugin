# Sekshey's Jyotish Suite — Claude Code Marketplace

A curated marketplace distributing **Jyotish Suite**: a six-system Vedic astrology toolkit for Claude Code.

## What's inside

One plugin — `jyotish-suite` — bundling six rigorous astrology systems, each as a skill with its own slash command:

| Slash command       | System                              | Use it for                                                                 |
| ------------------- | ----------------------------------- | -------------------------------------------------------------------------- |
| `/vedic-astro`      | Classical Vedic (Parashari)         | Multi-layered chart reading: Nakshatras, Padas, aspects, Vimshottari Dasha |
| `/bnn`              | BNN (Brighu Nadi Nadi)              | Natural Karaka + Nadi flow analysis with degree-based timing               |
| `/jaimini`          | Jaimini                             | Chara Karakas, Arudha Padas, Swamsha, Argala, Chara Dasha                  |
| `/lal-kitab`        | Lal Kitab                           | Rin diagnosis, pakka ghar, varshphal, upaay (Farmans 1939–1952)            |
| `/kp-natal`         | Krishnamurti Paddhati — Natal       | Life reading + event timing via Sookshma dasha + Ruling Planets            |
| `/kp-horary`        | Krishnamurti Paddhati — Horary      | Yes/no/timing answers from a 1–249 number + moment + place                 |

Each skill is also auto-triggered by its skill description, so you can use either the slash command or natural language.

## Install

```bash
# In Claude Code
/plugin marketplace add sekshey/jyotish-suite-marketplace
/plugin install jyotish-suite@sekshey-jyotish
```

To test locally before publishing:

```bash
/plugin marketplace add /path/to/jyotish-suite-marketplace
/plugin install jyotish-suite@sekshey-jyotish
```

## Requirements

The two KP slash commands (`/kp-natal`, `/kp-horary`) need [`pyswisseph`](https://pypi.org/project/pyswisseph/) installed in Claude Code's Python environment:

```bash
pip install pyswisseph
```

The other four commands (`/vedic-astro`, `/bnn`, `/jaimini`, `/lal-kitab`) work on pre-computed charts and have no runtime dependencies.

## Update

```bash
/plugin marketplace update sekshey-jyotish
```

## Uninstall

```bash
/plugin uninstall jyotish-suite@sekshey-jyotish
/plugin marketplace remove sekshey-jyotish
```

## Repository structure

```
.
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog
├── plugins/
│   └── jyotish-suite/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest
│       ├── skills/               # Six SKILL.md files + references + scripts
│       └── commands/             # Six slash command definitions
└── README.md                     # This file
```

## License

MIT
