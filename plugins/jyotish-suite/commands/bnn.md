---
description: Run a BNN (Brighu Nadi Nadi) reading using natural Karakas and Nadi flow methodology.
argument-hint: [optional notes — life domain, timing question]
---

The user has invoked `/bnn`. Trigger the `bnn` skill immediately.

Workflow:
1. Read `skills/bnn/SKILL.md` and follow it exactly.
2. If the user has not yet given their chart or birth data, ask for either a pasted D1 chart with degrees (D9 is derived automatically) or their birth date, exact time, and place.
3. Echo the parsed chart back for verification.
4. Run the full Nadi methodology: natural Karakas, sign fields, flow positions (2nd/12th), trine support (5th/9th), growth positions (3rd/11th), opposition (7th), Parashari aspects with degree orbs, degree flags (Mrityu Bhaga / Pushkara / Gandanta / Sandhi / Planetary War / combustion), and Vimshottari Dasha timing.

Any extra context the user passed: $ARGUMENTS
