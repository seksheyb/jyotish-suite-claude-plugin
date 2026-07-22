# KP House Combinations — Question Categories

The CSL of the **primary house** must signify the **positive set**, not the
**negative set**, for the matter to fructify. The tables below mirror
`HOUSE_COMBINATIONS` in `scripts/compute_kp_horary_baseline.py` exactly (same
keys, same primary/positive/negative house numbers) — this file adds only the
interpretive notes the script doesn't carry. If a future script edit changes a
number, update it here too; this file must never drift from the source dict.

## marriage / partnership

**Primary:** 7 · **Positive:** 2, 7, 11 · **Negative:** 1, 6, 10
- 7th CSL must signify 2, 7, or 11. If signifies 1, 6, or 10 → denial.
- For *love* marriage specifically, also check 5 (romance) connection.
- Rahu in 7 or 7th CSL = unconventional partner; nodes need careful sub-sub check.

## new_job — new job / employment

**Primary:** 10 · **Positive:** 2, 6, 10, 11 · **Negative:** 5, 8, 12
- 10th CSL must signify 2, 6, 10, or 11.
- 6 is essential — without 6, no employment (only self-employment via 7).
- For self-employment / consulting, primary becomes 7, supporting 2 and 11.

## job_change_leaving / job_change_new — job change

Two independent CSL chains — score both, don't blend them:

- **job_change_leaving** — **Primary:** 1, 10 · **Positive:** 5, 9 ·
  **Negative:** 2, 6, 10, 11. CSL of 1 (or 10) signifying 5/9 = inclination to
  leave; signifying 2/6/10/11 = staying put.
- **job_change_new** — identical combination to `new_job` above (**Primary:**
  10 · **Positive:** 2, 6, 10, 11 · **Negative:** 5, 8, 12) — "will I get a new
  one."

**Verdict:** Both chains must align. If the leaving-CSL says "stay" but the
new-job CSL says "you'll get one," the outcome is delayed/conflicted — say so
rather than picking one chain to report.

## promotion — promotion / raise

**Primary:** 10, 2 · **Positive:** 2, 6, 10, 11 · **Negative:** 5, 8, 12
- Same combination as new job, but 10th CSL must signify 11 strongly (gain
  over status). 2 = financial gain.

## litigation_own — litigation, own case

**Primary:** 6 · **Positive:** 1, 6, 11 · **Negative:** 5, 8, 12
- 6th CSL signifying 1, 6, 11 = win. Signifying 5, 8, 12 = lose.
- For settlement out of court, check 9 (compromise, dharma).

## litigation_opponent — litigation, opponent's case

**Primary:** 12 · **Positive:** 5, 8, 12 · **Negative:** 1, 6, 11
- Mirror of `litigation_own` from the opponent's side: their 1 = your 7, their
  6 = your 12, their 11 = your 5. Their victory (their positive set) is your
  defeat — check the 12th CSL against this category's own positive/negative
  sets directly rather than re-deriving the mirror by hand.

## property_purchase

**Primary:** 4 · **Positive:** 4, 11, 12 · **Negative:** 3, 5, 10
- 4th CSL signifying 4, 11, 12 = acquisition.
- 4th CSL signifying 3, 5, 10 = sale (don't acquire; relinquish) — this is the
  negative set exactly as `property_sale`'s positive set below.

## property_sale

**Primary:** 3 · **Positive:** 3, 5, 10 · **Negative:** 4, 11, 12
- Inverse of `property_purchase` — 3rd CSL signifying 3, 5, 10 = transfer
  completes; signifying 4, 11, 12 = buyer's-side acquisition energy dominates
  and the sale stalls.

## childbirth / conception

**Primary:** 5 · **Positive:** 2, 5, 11 · **Negative:** 1, 4, 10
- For male native, also check 11 = elder sibling of 5 = first-child timing.
- Saturn or Ketu on the 5th CSL = delay or denial; sub-sub crucial.

## loan_borrowing

**Primary:** 6 · **Positive:** 2, 6, 11 · **Negative:** 8, 12

## loan_giving

**Primary:** 8 · **Positive:** 8, 11, 2 · **Negative:** 6, 12
- Separate category from `loan_borrowing`, not a note on it — the primary
  house flips (8 = others' money placed at risk, vs 6 = your own debt), so it
  needs its own CSL chain. Positive set centers on 11 (repayment received).

## investment_return — speculation

**Primary:** 5 · **Positive:** 2, 5, 11 · **Negative:** 8, 12

## travel_long — long journey

**Primary:** 9 · **Positive:** 3, 9, 12 · **Negative:** 4, 8

## foreign_settlement — immigration

**Primary:** 12 · **Positive:** 9, 12, 7 · **Negative:** 4, 11

## health_cure — disease cure

**Primary:** 1 · **Positive:** 1, 5, 11 · **Negative:** 6, 8, 12
- 1st CSL signifying 1, 5, 11 = recovery. Signifying 6, 8, 12 = continued
  illness. (6 is where the disease itself lives — the question is "will I be
  freed FROM 6," so 6 sits in the negative set, not the primary house.)

## education_exam

**Primary:** 4, 9 · **Positive:** 4, 9, 11 · **Negative:** 8, 12
- For competitive exams specifically, also weigh 6 (winning over competitors)
  and 10 (status from the result) even though they aren't in the base set.

## lost_item_recovery

**Primary:** 2 · **Positive:** 2, 11 · **Negative:** 6, 8, 12
- **Direction:** sign of the CSL gives direction (fire = SE, earth = S, air =
  W, water = N, etc.).

## election_appointment

**Primary:** 10 · **Positive:** 6, 10, 11 · **Negative:** 5, 8, 12

## business_launch — project / venture launch

**Primary:** 10, 11 · **Positive:** 2, 6, 10, 11 · **Negative:** 5, 8, 12

## When in doubt

If no clear category fits, ask the user to clarify the question. Don't
force-fit a question into a category.

## Why 20 keys here vs kp-natal's 18

This file's categories and `kp-natal`'s equivalent reference intentionally
diverge in count — this is a methodological split, not drift:

- **`job_change` splits into two keys here** (`job_change_leaving` +
  `job_change_new`) instead of kp-natal's single `job_change`. Horary is
  single-issue by definition (see SKILL.md Question intake: "one chart, one
  question") — "will I leave" and "will I get the new job" are two
  independent CSL chains that must be scored and reported separately even
  when asked together. A life reading can narrate both under one combined
  lens; a horary verdict cannot blend two questions into one answer.
- **`loan_giving` is its own key here**, not folded into `loan_borrowing`'s
  note the way kp-natal does it — the primary house flips (8 vs 6), so it
  needs an independent primary/positive/negative set, not a footnote.

Everything else lines up house-for-house with kp-natal's set under matching
or renamed keys.
