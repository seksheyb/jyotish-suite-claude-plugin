# KP 249-Number Lagna

## Concept

The zodiac (360°) is divided into 249 unequal segments based on Vimshottari
Mahadasha proportions — each nakshatra (13°20') is split into 9 sub-divisions
sized to its star-lords' dasha years, giving 249 subs total across the 27
nakshatras. Each segment is uniquely identified by Sign + Star + Sub. The
horary number 1-249 the user picks mentally (never supplied by the questioner
looking at a clock or a calculation — it must be spontaneous) maps to exactly
one segment; that segment's **mid-point degree** becomes the horary **chart
Lagna** — see "Two Lagnas — never mix them" in `orchestration-notes.md` for
why this is never the real rising sign at question time.

The full 249-segment table (start/end degree, sign, star, sub, sub-sub for
every segment) and the number→Lagna lookup are built and computed entirely
inside `ephemeris.horary_number_to_lagna()`, called from
`scripts/compute_kp_horary_baseline.py`. There is nothing in this mapping to
hand-table or recompute — read `horary_lagna` straight from the baseline JSON.

## Validation and the sandhi edge case

- The number must be an integer 1-249. Reject 0, 250+, or non-integers — ask
  the user again.
- **Sandhi:** if the chosen segment's mid-point falls within 0°30' of a sign
  edge, the horary Lagna sits at sandhi — warn the user that verdict
  reliability is reduced for a Lagna this close to a sign boundary, and
  suggest re-asking the question later (a few minutes is enough to move the
  number's segment mid-point off the edge). This is a genuine caveat to raise
  in the verdict's caveats section even when the script doesn't (yet) emit an
  explicit sandhi flag on `horary_lagna` — check the degree by eye against the
  0°30' band.
