# KP 249-Number Lagna Table

## How it works

The zodiac (360°) is divided into 249 unequal segments based on Vimshottari Mahadasha proportions:
- Each Nakshatra (13°20') is split into Subs proportional to dasha years
- Total subs across 27 nakshatras = 249
- Each segment is uniquely identified by Sign + Star + Sub

The horary number 1 to 249 maps directly to one of these segments. Whichever segment number is chosen, that segment's mid-point becomes the **horary Lagna degree**.

## Computation

The skill computes this programmatically in `scripts/compute_horary_chart.py`. The algorithm:

1. Build the 249 sub-table starting from 0° Aries
2. For each sub, compute start degree, end degree, sign, star (nakshatra lord), sub-lord, sub-sub-lord
3. Look up the user-provided number N → return mid-degree of segment N
4. That degree = Horary Lagna

## Vimshottari proportions (used for sub-divisions)

| Star Lord | Years | Proportion of 13°20' |
|-----------|-------|---------------------|
| Ketu | 7 | 0°46'40" |
| Venus | 20 | 2°13'20" |
| Sun | 6 | 0°40'00" |
| Moon | 10 | 1°06'40" |
| Mars | 7 | 0°46'40" |
| Rahu | 18 | 2°00'00" |
| Jupiter | 16 | 1°46'40" |
| Saturn | 19 | 2°06'40" |
| Mercury | 17 | 1°53'20" |
| **Total** | **120** | **13°20'00"** |

Each nakshatra contains 9 subs in Vimshottari order, starting from the star's own lord. The order of star lords across the zodiac is: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury (then repeats).

## Reference: standard 249-table starting points

The first sub of each nakshatra:

| # | Nakshatra | Sign | Start Lord (own) |
|---|-----------|------|------------------|
| 1 | Ashwini (0°-13°20' Aries) | Aries | Ketu |
| 10 | Bharani | Aries | Venus |
| 19 | Krittika | Aries/Taurus | Sun |
| 28 | Rohini | Taurus | Moon |
| 37 | Mrigashira | Taurus/Gemini | Mars |
| 46 | Ardra | Gemini | Rahu |
| 55 | Punarvasu | Gemini/Cancer | Jupiter |
| 64 | Pushya | Cancer | Saturn |
| 73 | Ashlesha | Cancer | Mercury |
| 82 | Magha | Leo | Ketu |
| 91 | Purva Phalguni | Leo | Venus |
| 100 | Uttara Phalguni | Leo/Virgo | Sun |
| 109 | Hasta | Virgo | Moon |
| 118 | Chitra | Virgo/Libra | Mars |
| 127 | Swati | Libra | Rahu |
| 136 | Vishakha | Libra/Scorpio | Jupiter |
| 145 | Anuradha | Scorpio | Saturn |
| 154 | Jyestha | Scorpio | Mercury |
| 163 | Mula | Sagittarius | Ketu |
| 172 | Purva Ashadha | Sagittarius | Venus |
| 181 | Uttara Ashadha | Sagittarius/Capricorn | Sun |
| 190 | Shravana | Capricorn | Moon |
| 199 | Dhanishtha | Capricorn/Aquarius | Mars |
| 208 | Shatabhisha | Aquarius | Rahu |
| 217 | Purva Bhadrapada | Aquarius/Pisces | Jupiter |
| 226 | Uttara Bhadrapada | Pisces | Saturn |
| 235 | Revati | Pisces | Mercury |

(Numbers shown are the first sub of each nakshatra; 244-249 are sub-divisions of Revati's last subs.)

The exact 249 → degree mapping is built procedurally in the script — no need to hand-table.

## Validation

If user provides number outside 1-249, ask again. If user provides number 0 or 250+, reject.

For the rare case where the chosen segment falls exactly at a sign-edge degree (sandhi), warn the user that the Lagna is at sandhi and verdict reliability is reduced — suggest re-asking after some time.
