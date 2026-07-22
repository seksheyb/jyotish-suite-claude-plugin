# KP House Combinations — Question Categories

The CSL of the **primary house** must signify the **positive set**, not the **negative set**, for the matter to fructify.

This file mirrors the 18-key `HOUSE_COMBINATIONS` constant in
`scripts/compute_kp_natal_baseline.py` exactly (primary/positive/negative sets
below match the script key-for-key) — it exists for narrative context and
worked examples the baseline's one-line `note` field can't carry. If the two
ever disagree, the script wins; file an update here.

## Marriage / partnership (`marriage`)

**Primary:** 7 (spouse, partnership)
**Positive:** 2 (family expansion), 7 (spouse), 11 (fulfillment of desire)
**Negative:** 1 (self alone), 6 (separation, dispute), 10 (career over family)
**Notes:**
- 7th CSL must signify 2, 7, or 11. If signifies 1, 6, or 10 → denial.
- For *love* marriage specifically, also check 5 (romance) connection.
- Rahu in 7 or 7th CSL = unconventional partner; nodes need careful sub-sub check.

## New job / employment (`new_job`)

**Primary:** 10 (career, status)
**Positive:** 2 (income), 6 (employment, service), 10 (profession), 11 (gain, fulfillment)
**Negative:** 5 (speculation over service), 8 (obstacles, transformation), 12 (loss, isolation)
**Notes:**
- 10th CSL must signify 2, 6, 10, or 11.
- 6 is essential — without 6, no employment (only self-employment via 7).
- For self-employment / consulting, primary becomes 7, supporting 2 and 11.

## Job change / leaving current job (`job_change`)

**Two-step:**
1. **Leaving:** Primary houses 1, 10. CSL of 1 (or 10) signifying 5/9 = inclination to change. (Positive set for this step is [5, 9]; there is no negative set — it's a binary inclination check, not a fructify/deny gate.)
2. **New job:** Standard `new_job` combination above.
**Verdict:** Both must align. If 1-CSL says "stay" but new-job CSL says "you'll get one," outcome is delayed/conflicted.

## Promotion / raise (`promotion`)

**Primary:** 10 (status increase) + 2 (income increase)
**Positive:** 2, 6, 10, 11
**Negative:** 5, 8, 12
**Notes:** Same as new job, but 10th CSL must signify 11 strongly (gain over status). 2 = financial gain.

## Litigation — own case (`litigation_own`)

**Primary:** 6 (victory over opponent)
**Positive:** 1 (self), 6 (victory), 11 (fulfillment)
**Negative:** 5 (defeat), 8 (obstacle), 12 (loss)
**Notes:**
- 6th CSL signifying 1, 6, 11 = win
- 6th CSL signifying 5, 8, 12 = lose
- For settlement out of court, check 9 (compromise, dharma).

## Litigation — opponent's case (`litigation_opponent`)

**Primary:** 12 (mirrors the opponent's 6th — their victory)
**Positive:** 12, 5, 1
**Negative:** 6, 11
**Notes:**
- Mirror houses: their 1 = your 7, their 6 = your 12, their 11 = your 5.
- 12th CSL signifying 12, 5, or 1 = opponent wins (your defeat).
- 12th CSL signifying 6 or 11 = opponent loses (your win) — cross-check against `litigation_own`.

## Property purchase (`property_purchase`)

**Primary:** 4 (property, fixed asset)
**Positive:** 4 (acquisition), 11 (gain), 12 (investment, expense)
**Negative:** 3 (transfer/sale), 5 (negation of 4), 10 (relinquish/profession over asset)
**Notes:**
- 4th CSL signifying 4, 11, 12 = acquisition
- 4th CSL signifying 3, 5, 10 = sale (don't acquire; relinquish)

## Property sale (`property_sale`)

**Primary:** 3 (transfer, exchange)
**Positive:** 3, 5 (negation of 4), 10 (cash flow from asset)
**Negative:** 4, 11, 12 (acquisition mode)

## Childbirth / conception (`childbirth`)

**Primary:** 5 (children)
**Positive:** 2 (family addition), 5 (child), 11 (fulfillment of desire)
**Negative:** 1 (self alone), 4 (no progression past mother stage), 10 (career over family)
**Notes:**
- For male native, also check 11 = elder sibling of 5 = first child timing
- Saturn or Ketu CSL on 5 = delay or denial; sub-sub crucial

## Loan / borrowing (`loan_borrow`)

**Primary:** 6 (borrowing, debt)
**Positive:** 2 (money received), 6 (loan granted), 11 (gain)
**Negative:** 8 (debt that won't be repaid easily), 12 (loss)
**Notes:** For *giving* a loan, primary becomes 8 (others' money) and look for 11 (you'll be repaid).

## Investment return / speculation (`speculation`)

**Primary:** 5 (speculation)
**Positive:** 2 (gain), 5 (speculation), 11 (fulfillment)
**Negative:** 8 (sudden loss), 12 (loss)

## Travel — long journey (`long_travel`)

**Primary:** 9 (long journey)
**Positive:** 3 (movement), 9 (long), 12 (foreign land)
**Negative:** 4 (stay home), 8 (travel obstacle/danger)

## Foreign settlement / immigration (`foreign_settlement`)

**Primary:** 12 (foreign land, moksha)
**Positive:** 9 (long journey, dharma in new place), 12 (foreign), 7 (away from home, partnership/sponsor)
**Negative:** 4 (homeland holds you), 11 (gain at home)

## Health / disease cure (`health_cure`)

**Primary:** 1 (vitality) or 6 (disease — wanting to free FROM 6)
**Positive for cure:** 1, 5, 11 (recovery, fulfillment of desire to heal)
**Negative:** 6 (continued disease), 8 (chronic), 12 (hospitalization, loss)
**Notes:** 1st CSL signifying 1, 5, 11 = recovery. Signifying 6, 8, 12 = continued illness.

## Education / exam (`education_exam`)

**Primary:** 4 (formal learning) or 9 (higher learning)
**Positive:** 4, 9, 11 (success, fulfillment)
**Negative:** 8 (obstruction), 12 (failure, loss)
**For competitive exam:** add 6 (winning over competitors) and 10 (status from result).

## Lost item — recovery (`lost_item`)

**Primary:** 2 (recovery of possession)
**Positive:** 2, 11 (recovered, gained back)
**Negative:** 6, 8, 12 (lost, gone, beyond reach)
**Direction:** Sign of CSL gives direction (fire = SE, earth = S, air = W, water = N, etc.)

## Election / appointment (`election`)

**Primary:** 10 (status, position)
**Positive:** 6 (defeat opponent), 10 (position), 11 (fulfillment)
**Negative:** 5, 8, 12

## Project / business venture launch (`business_launch`)

**Primary:** 10 (action) + 11 (gain)
**Positive:** 2, 6, 10, 11
**Negative:** 5, 8, 12

## When in doubt
If no clear category fits, ask the user to clarify the question. Don't force-fit a question into a category.

## Note — kp-horary uses a different, 20-key variant

`scripts/compute_kp_horary_baseline.py` has its own `HOUSE_COMBINATIONS` with
20 keys, not 18. This is a **deliberate methodological split, not drift**:
horary Prashna questions are asked one at a time with a fixed direction (e.g.
"will I get the loan" vs "will I have to give one"), so kp-horary splits what
kp-natal treats as a single two-step category into two standalone keys —
`job_change_leaving` / `job_change_new` (vs kp-natal's single `job_change` with
an internal two-step note) and `loan_borrowing` / `loan_giving` (vs kp-natal's
single `loan_borrow` with a giving-loan note). Do not try to reconcile the two
scripts to a shared key count — reconcile only if a future audit finds the
*shared* keys (e.g. `marriage`, `new_job`, `childbirth`) have drifted in their
primary/positive/negative sets, since those must stay identical across both
schools.
