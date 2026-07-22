# Vedic Astrology Reference Tables

## Nakshatra Master Table
| # | Nakshatra | Ruler | Degrees (Sidereal) | Gana | Symbol |
|---|-----------|-------|-------------------|------|--------|
| 1 | Ashwini | Ketu | Aries 0°00' – 13°20' | Deva | Horse Head |
| 2 | Bharani | Venus | Aries 13°20' – 26°40' | Manushya | Yoni |
| 3 | Krittika | Sun | Aries 26°40' – Taurus 10°00' | Rakshasa | Razor |
| 4 | Rohini | Moon | Taurus 10°00' – 23°20' | Manushya | Chariot |
| 5 | Mrigashira | Mars | Taurus 23°20' – Gemini 6°40' | Deva | Deer Head |
| 6 | Ardra | Rahu | Gemini 6°40' – 20°00' | Manushya | Teardrop |
| 7 | Punarvasu | Jupiter | Gemini 20°00' – Cancer 3°20' | Deva | Bow |
| 8 | Pushya | Saturn | Cancer 3°20' – 16°40' | Deva | Flower |
| 9 | Ashlesha | Mercury | Cancer 16°40' – 30°00' | Rakshasa | Coiled Serpent |
| 10 | Magha | Ketu | Leo 0°00' – 13°20' | Rakshasa | Throne |
| 11 | Purva Phalguni | Venus | Leo 13°20' – 26°40' | Manushya | Hammock |
| 12 | Uttara Phalguni | Sun | Leo 26°40' – Virgo 10°00' | Manushya | Bed |
| 13 | Hasta | Moon | Virgo 10°00' – 23°20' | Deva | Hand |
| 14 | Chitra | Mars | Virgo 23°20' – Libra 6°40' | Rakshasa | Pearl |
| 15 | Swati | Rahu | Libra 6°40' – 20°00' | Deva | Coral |
| 16 | Vishakha | Jupiter | Libra 20°00' – Scorpio 3°20' | Rakshasa | Triumphal Arch |
| 17 | Anuradha | Saturn | Scorpio 3°20' – 16°40' | Deva | Lotus |
| 18 | Jyeshtha | Mercury | Scorpio 16°40' – 30°00' | Rakshasa | Earring |
| 19 | Mula | Ketu | Sagittarius 0°00' – 13°20' | Rakshasa | Tied Roots |
| 20 | Purva Ashadha | Venus | Sagittarius 13°20' – 26°40' | Manushya | Fan |
| 21 | Uttara Ashadha | Sun | Sagittarius 26°40' – Capricorn 10°00' | Manushya | Elephant Tusk |
| 22 | Shravana | Moon | Capricorn 10°00' – 23°20' | Deva | Ear |
| 23 | Dhanishtha | Mars | Capricorn 23°20' – Aquarius 6°40' | Rakshasa | Drum |
| 24 | Shatabhisha | Rahu | Aquarius 6°40' – 20°00' | Rakshasa | Empty Circle |
| 25 | Purva Bhadrapada | Jupiter | Aquarius 20°00' – Pisces 3°20' | Manushya | Sword |
| 26 | Uttara Bhadrapada | Saturn | Pisces 3°20' – 16°40' | Deva | Twins |
| 27 | Revati | Mercury | Pisces 16°40' – 30°00' | Deva | Fish |

## Nakshatra Pada Reference
Each Nakshatra spans 13°20' divided into 4 Padas of 3°20' each.
- Pada 1: 0°00' – 3°20' within the Nakshatra
- Pada 2: 3°20' – 6°40' within the Nakshatra
- Pada 3: 6°40' – 10°00' within the Nakshatra
- Pada 4: 10°00' – 13°20' within the Nakshatra

Pada placement determines the Navamsa sign:
- For fire sign Nakshatras (Aries/Leo/Sagittarius start): Pada 1=Aries, 2=Taurus, 3=Gemini, 4=Cancer
- For earth sign Nakshatras: Pada 1=Leo, 2=Virgo, 3=Libra, 4=Scorpio
- For air sign Nakshatras: Pada 1=Sagittarius, 2=Capricorn, 3=Aquarius, 4=Pisces
- For water sign Nakshatras: Pada 1=Aries, 2=Taurus, 3=Gemini, 4=Cancer

## Dasha Sequence & Years
| Planet | Years |
|--------|-------|
| Ketu | 7 |
| Venus | 20 |
| Sun | 6 |
| Moon | 10 |
| Mars | 7 |
| Rahu | 18 |
| Jupiter | 16 |
| Saturn | 19 |
| Mercury | 17 |

Total cycle: 120 years. Sequence always follows: Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter → Saturn → Mercury → repeat.

## Mrityu Bhaga (Death Degrees)

The full Mrityu Bhaga table — every planet, every sign, plus the Lagna row —
lives in `degree-flags.md`. That file is the single source of truth the
baseline script (`compute_vedic_baseline.py`) implements; do not maintain a
second copy here.

## Gandanta Zones (Karmically Sensitive)
Junction of water-to-fire sign transitions:
- Cancer 26°40' – Leo 3°20' (most intense at exact cusp)
- Scorpio 26°40' – Sagittarius 3°20'
- Pisces 26°40' – Aries 3°20'

## Pushkara Navamsa Degrees
Especially auspicious placements that strengthen a planet's results:
- Aries: 6°40'–10° and 23°20'–26°40'
- Taurus: 3°20'–6°40' and 16°40'–20°
- Gemini: 6°40'–10° and 20°–23°20'
- Cancer: 0°–3°20' and 16°40'–20°
- Leo: 3°20'–6°40' and 20°–23°20'
- Virgo: 6°40'–10° and 23°20'–26°40'
- Libra: 0°–3°20' and 16°40'–20°
- Scorpio: 3°20'–6°40' and 20°–23°20'
- Sagittarius: 6°40'–10° and 23°20'–26°40'
- Capricorn: 0°–3°20' and 16°40'–20°
- Aquarius: 3°20'–6°40' and 20°–23°20'
- Pisces: 6°40'–10° and 23°20'–26°40'

## Planetary Combustion Orbs
Planet is combust when within this distance of the Sun:
| Planet | Combustion Orb |
|--------|---------------|
| Moon | 12° |
| Mars | 17° |
| Mercury | 14° (12° if retrograde) |
| Jupiter | 11° |
| Venus | 10° (8° if retrograde) |
| Saturn | 15° |

## Parashari Aspects
| Planet | Special Aspects (in addition to universal 7th) |
|--------|-----------------------------------------------|
| Mars | 4th and 8th house from itself |
| Jupiter | 5th and 9th house from itself |
| Saturn | 3rd and 10th house from itself |
| Rahu/Ketu | 5th and 9th (school-dependent) |
| All others | 7th house only |

## Lagna Lord & Functional Benefic/Malefic Reference
| Lagna | Functional Benefics | Functional Malefics | Yogakaraka |
|-------|--------------------|--------------------|------------|
| Aries | Sun, Moon, Jupiter, Mars | Mercury, Rahu, Saturn | Sun |
| Taurus | Saturn, Mercury, Venus, Sun | Jupiter, Moon, Mars | Saturn |
| Gemini | Venus, Saturn, Mercury | Mars, Sun, Jupiter | Venus |
| Cancer | Mars, Jupiter, Moon | Saturn, Mercury, Venus | Mars |
| Leo | Mars, Sun, Jupiter | Mercury, Venus, Saturn | — |
| Virgo | Mercury, Venus, Saturn | Mars, Moon, Jupiter | Mercury |
| Libra | Mercury, Saturn, Venus | Jupiter, Sun, Mars | Saturn |
| Scorpio | Jupiter, Moon, Mars | Mercury, Venus | Moon |
| Sagittarius | Mars, Sun, Jupiter | Saturn, Venus | Sun |
| Capricorn | Venus, Saturn, Mercury | Mars, Moon, Jupiter | Venus |
| Aquarius | Venus, Saturn, Mars | Jupiter, Moon, Sun | Venus |
| Pisces | Moon, Mars, Jupiter | Saturn, Venus, Mercury | — |

## Planet Dignity Reference
| Planet | Exaltation | Own Sign | Moolatrikona | Debilitation |
|--------|-----------|----------|--------------|-------------|
| Sun | Aries 10° | Leo | Leo 0°–20° | Libra 10° |
| Moon | Taurus 3° | Cancer | Taurus 4°–30° | Scorpio 3° |
| Mars | Capricorn 28° | Aries, Scorpio | Aries 0°–12° | Cancer 28° |
| Mercury | Virgo 15° | Gemini, Virgo | Virgo 16°–20° | Pisces 15° |
| Jupiter | Cancer 5° | Sagittarius, Pisces | Sagittarius 0°–10° | Capricorn 5° |
| Venus | Pisces 27° | Taurus, Libra | Libra 0°–15° | Virgo 27° |
| Saturn | Libra 20° | Capricorn, Aquarius | Aquarius 0°–20° | Aries 20° |
| Rahu | Taurus/Gemini | — | Gemini | Scorpio/Sagittarius |
| Ketu | Scorpio/Sagittarius | — | — | Taurus/Gemini |
