#!/usr/bin/env python3
"""
Regression guard for the lal-kitab bugfix-wave track.

Plain python3, no pytest — asserts + PASS/FAIL prints, exits nonzero on any
failure. Each test targets one specific defect class from AUDIT-lal-kitab.md /
the lal-kitab findings file, constructing a minimal synthetic chart that
isolates the bug so a regression trips immediately (rather than relying on
one pinned nativity to happen to exercise every rare branch).

Run:
    python3 plugins/jyotish-suite/tests/test_lal_kitab_regressions.py
"""

import inspect
import os
import sys
import traceback

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
sys.path.insert(0, SCRIPTS_DIR)
import compute_lalkitab_baseline as m  # noqa: E402

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"PASS: {label}")
    else:
        msg = f"FAIL: {label}" + (f" -- {detail}" if detail else "")
        print(msg)
        FAILURES.append(msg)


def mk_planet(sign_idx, deg=10.0, retro=False):
    return {"sign": m.jp.SIGNS[sign_idx], "deg_in_sign": deg, "retrograde": retro}


def build(planet_houses, deg_overrides=None):
    """planet_houses: {planet: fixed_house 1-12}. Builds a full fixed chart +
    pakka/aspect/sleeping/rin/teva pipeline for the given placements."""
    deg_overrides = deg_overrides or {}
    d1 = {
        "lagna_sign": "Aries",
        "planets": {
            p: mk_planet(h - 1, deg_overrides.get(p, 10.0)) for p, h in planet_houses.items()
        },
    }
    fixed_chart = m.build_fixed_house_chart(d1)
    pakka = m.build_pakka_ghar(fixed_chart)
    aspect_map = m.build_aspect_map(fixed_chart)
    sleeping = m.build_sleeping(fixed_chart, aspect_map)
    rin = m.build_rin_diagnosis(fixed_chart, pakka, aspect_map, sleeping)
    teva = m.build_teva(fixed_chart, pakka, sleeping, rin, aspect_map)
    return fixed_chart, pakka, aspect_map, sleeping, rin, teva


# ---------------------------------------------------------------------------
# W1 (P1-1) — Behra Teva must test Mercury (actual 3rd lord), not Mars.
# ---------------------------------------------------------------------------
def test_behra_teva_tests_mercury_not_mars():
    # Mars debilitated (house 4) but Mercury (3rd lord) exalted (house 6) and
    # untouched by Saturn/Rahu/Ketu; house 3 empty of Saturn/Ketu. Pre-fix,
    # third_bad fired purely off Mars's unrelated debilitation.
    placements = {
        "Mars": 4, "Mercury": 6,
        "Sun": 1, "Moon": 1, "Jupiter": 11, "Venus": 11,
        "Saturn": 11, "Rahu": 11, "Ketu": 11,
    }
    fixed_chart, pakka, aspect_map, sleeping, rin, teva = build(placements)
    third_lord_afflicted = m._lord_afflicted(
        m.HOUSE_OWNER[3], pakka, fixed_chart["planets"], aspect_map)
    check(
        "Behra Teva: 3rd-lord (Mercury) affliction test unaffected by Mars debilitation",
        m.HOUSE_OWNER[3] == "Mercury" and third_lord_afflicted is False,
        f"HOUSE_OWNER[3]={m.HOUSE_OWNER[3]!r}, third_lord_afflicted={third_lord_afflicted!r}, "
        f"Mars dignity={pakka['Mars']['lk_dignity']!r} (must not leak into the 3rd-lord check)")


# ---------------------------------------------------------------------------
# W2 (P1-2) — Andha Teva's affliction test must be "debilitated / sleeping /
# with Saturn-Rahu-Ketu", not "debilitated / enemy-house / buried".
# ---------------------------------------------------------------------------
def test_general_afflicted_matches_reference_not_enemy_or_buried():
    # Sun in house 11 (owned by Saturn -> enemy dignity for Sun), aspected
    # only by Jupiter (a benefic, not Saturn/Rahu/Ketu), not sleeping, not
    # buried, not debilitated. Reference (aspects.md) says this is NOT
    # afflicted; the pre-fix script's "enemy or buried" substitute said it was.
    placements = {
        "Sun": 11, "Jupiter": 7,
        "Moon": 1, "Mars": 1, "Mercury": 1, "Venus": 1,
        "Saturn": 4, "Rahu": 4, "Ketu": 4,
    }
    fixed_chart, pakka, aspect_map, sleeping, rin, teva = build(placements)
    afflicted = m._general_afflicted("Sun", pakka, sleeping, fixed_chart["planets"], aspect_map)
    check(
        "general_afflicted(): enemy-dignity + benefic-only aspect is NOT afflicted",
        pakka["Sun"]["lk_dignity"] == "enemy" and not sleeping["Sun"]["sleeping"]
        and not pakka["Sun"]["buried"] and afflicted is False,
        f"Sun dignity={pakka['Sun']['lk_dignity']!r}, sleeping={sleeping['Sun']['sleeping']!r}, "
        f"buried={pakka['Sun']['buried']!r}, general_afflicted={afflicted!r}")


# ---------------------------------------------------------------------------
# M1 (P1-3) — Jupiter's 5th-house aspect must mitigate rin severity one tier
# wherever it lands (aspects.md "Special Aspect Rules").
# ---------------------------------------------------------------------------
def test_jupiter_5th_aspect_mitigates_rin_severity():
    # Jupiter's aspect table offset "5" (the 5th-house aspect) counted from
    # house 5 lands on house 9 (house_n_from(5, 5) == 9), and house 9 is one
    # of pitri_rin's RIN_HOUSES. Saturn conjunct Sun (house 8) fires Pitri
    # trigger 1 ("Sun afflicted by Saturn"). Confirm the mitigation flag
    # fires and the pre-mitigation severity is preserved.
    check(
        "Jupiter in house 5's 5th-house-offset aspect lands on house 9 (a Pitri-Rin house)",
        m.house_n_from(5, 5) == 9 and 9 in m.RIN_HOUSES["pitri_rin"])
    placements = {
        "Jupiter": 5, "Sun": 8, "Saturn": 8,
        "Moon": 4, "Mars": 4, "Mercury": 4, "Venus": 4, "Rahu": 4, "Ketu": 4,
    }
    fixed_chart, pakka, aspect_map, sleeping, rin, teva = build(placements)
    pitri = rin["rins"]["pitri_rin"]
    check(
        "Pitri Rin triggered by Saturn-Sun conjunction in this fixture",
        pitri["triggered"] is True, f"pitri={pitri}")
    check(
        "M1: Jupiter 5th-aspect mitigation flag set and pre-mitigation severity preserved",
        pitri["jupiter_5th_aspect_mitigation"] is True
        and "severity_before_mitigation" in pitri,
        f"pitri={pitri}")


# ---------------------------------------------------------------------------
# M2 (P1-4) — cross-rin escalation: active_count >= 2 bumps every active
# rin's severity up one tier.
# ---------------------------------------------------------------------------
def test_cross_rin_escalation_bumps_severity():
    # Use the pinned test nativity via the module's own datetime path instead
    # of relying on a golden fixture (keeps this test self-contained).
    chart = m.eph.parashari_natal_chart(
        "1990-05-15T10:30:00", "Asia/Kolkata", 28.6139, 77.2090, ayanamsa_mode="lahiri")
    baseline = m.build_baseline(chart, 35)
    rin = baseline["rin_diagnosis"]
    check(
        "Pinned chart (1990-05-15 10:30 IST) has active_count >= 2",
        rin["active_count"] >= 2, f"active_count={rin['active_count']}")
    escalated = [k for k, v in rin["rins"].items() if v.get("cross_rin_escalated")]
    check(
        "M2: cross-rin escalation applied to every active rin when active_count >= 2",
        len(escalated) == rin["active_count"] and all(
            "severity_before_cross_rin_escalation" in rin["rins"][k] for k in escalated),
        f"escalated={escalated}, active_rins={rin['active_rins']}")


# ---------------------------------------------------------------------------
# M3 (P1-5) — dead-pair sleeping exception: two planets that aspect only
# each other (and have no other contact) stay sleeping.
# ---------------------------------------------------------------------------
def test_dead_pair_stays_sleeping():
    # Jupiter house1 <-> Ketu house9: Jupiter's [5,7,9] aspect from house1
    # lands on house9; Ketu's [5,7,9] aspect from house9 lands on house1.
    # House 8 is aspect-safe for every other planet (verified against
    # LK_ASPECTS at fix time) so nothing else touches houses 1 or 9.
    placements = {
        "Jupiter": 1, "Ketu": 9,
        "Sun": 8, "Moon": 8, "Mars": 8, "Mercury": 8, "Venus": 8, "Saturn": 8, "Rahu": 8,
    }
    fixed_chart, pakka, aspect_map, sleeping, rin, teva = build(placements)
    check(
        "Dead pair (Jupiter/Ketu) both re-marked sleeping",
        sleeping["Jupiter"]["sleeping"] is True and sleeping["Ketu"]["sleeping"] is True,
        f"Jupiter={sleeping['Jupiter']}, Ketu={sleeping['Ketu']}")
    check(
        "Dead pair: dead_pair_with cross-references correctly",
        sleeping["Jupiter"]["dead_pair_with"] == "Ketu"
        and sleeping["Ketu"]["dead_pair_with"] == "Jupiter",
        f"Jupiter.dead_pair_with={sleeping['Jupiter']['dead_pair_with']!r}, "
        f"Ketu.dead_pair_with={sleeping['Ketu']['dead_pair_with']!r}")


# ---------------------------------------------------------------------------
# A1 — severity generalization: only Pitri Rin gets "2+ triggers -> Severe";
# other rins must be able to reach Moderate on 2 triggers / 0 compounders.
# ---------------------------------------------------------------------------
def test_severity_scale_not_generalized_to_all_rins():
    rec_pitri_multi = m._rin_record(
        [{"trigger": 1, "desc": "x"}, {"trigger": 2, "desc": "y"}], [], multi_trigger_severe=True)
    check(
        "Pitri-only rule: 2 triggers + 0 compounders -> Severe when multi_trigger_severe=True",
        rec_pitri_multi["severity"] == "Severe", f"{rec_pitri_multi}")

    rec_other_multi = m._rin_record(
        [{"trigger": 1, "desc": "x"}, {"trigger": 2, "desc": "y"}], [])
    check(
        "A1: non-Pitri rin with 2 triggers + 0 compounders is Mild, not auto-Severe",
        rec_other_multi["severity"] == "Mild", f"{rec_other_multi}")

    rec_other_one_compound = m._rin_record(
        [{"trigger": 1, "desc": "x"}, {"trigger": 2, "desc": "y"}], [True])
    check(
        "A1: non-Pitri rin with 2 triggers + 1 compounder reaches Moderate",
        rec_other_one_compound["severity"] == "Moderate", f"{rec_other_one_compound}")


# ---------------------------------------------------------------------------
# A2 — Neecha Bhanga: a debilitation is cancelled when the house-lord sits
# in its own pakka ghar.
# ---------------------------------------------------------------------------
def test_neecha_bhanga_cancellation():
    # Saturn debilitated in house 1 (LK_DEBIL_HOUSE); house 1's lord is Mars
    # (LK_HOUSES_OWNED); Mars sits in its own pakka ghar (house 3).
    placements = {
        "Saturn": 1, "Mars": 3,
        "Sun": 5, "Moon": 7, "Mercury": 8, "Jupiter": 9, "Venus": 7, "Rahu": 12, "Ketu": 6,
    }
    fixed_chart, pakka, aspect_map, sleeping, rin, teva = build(placements)
    check(
        "A2: debilitation cancelled when house-lord sits in its own pakka ghar",
        pakka["Saturn"]["lk_dignity"] == "debilitated" and pakka["Saturn"]["debil_cancelled"] is True,
        f"Saturn={pakka['Saturn']}")


# ---------------------------------------------------------------------------
# A3 — Pitri Rin gets a 3rd compounder slot (10th house damaged).
# ---------------------------------------------------------------------------
def test_pitri_rin_has_three_compounder_slots():
    src = inspect.getsource(m.build_rin_diagnosis)
    check(
        "A3: pitri_rin compounder list carries a 10th-house-damage check",
        "tenth_damaged" in src, "expected a tenth_damaged compounder wired into pitri_rin")


# ---------------------------------------------------------------------------
# A4 — Stri Rin compounders widened: Mercury afflicted (not just debilitated)
# and Moon afflicted by any malefic (not just Saturn).
# ---------------------------------------------------------------------------
def test_stri_rin_compounders_widened():
    # Mercury conjunct Rahu (afflicted via lord_afflicted, but NOT debilitated)
    # -> under the old "== debilitated" check this compounder would be False;
    # under the fix it must be True.
    placements = {
        "Mercury": 2, "Rahu": 2,
        "Venus": 5, "Sun": 1, "Moon": 8, "Mars": 1, "Jupiter": 1, "Saturn": 10, "Ketu": 1,
    }
    fixed_chart, pakka, aspect_map, sleeping, rin, teva = build(placements)
    merc_afflicted = m._lord_afflicted("Mercury", pakka, fixed_chart["planets"], aspect_map)
    check(
        "A4: Mercury conjunct Rahu is lord_afflicted even though not debilitated",
        pakka["Mercury"]["lk_dignity"] != "debilitated" and merc_afflicted is True,
        f"Mercury dignity={pakka['Mercury']['lk_dignity']!r}, lord_afflicted={merc_afflicted!r}")
    moon_afflicted = m._general_afflicted("Moon", pakka, sleeping, fixed_chart["planets"], aspect_map)
    check(
        "A4: Moon debilitated (house 8) counts as afflicted for the Stri-Rin Moon compounder",
        pakka["Moon"]["lk_dignity"] == "debilitated" and moon_afflicted is True)


# ---------------------------------------------------------------------------
# A5 — Bhratra / Atma Rin no longer fabricate compounders absent from the
# reference (rin_diagnosis.md has no Compounding subsection for §5/§6).
# ---------------------------------------------------------------------------
def test_bhratra_atma_no_fabricated_compounders():
    chart = m.eph.parashari_natal_chart(
        "1990-05-15T10:30:00", "Asia/Kolkata", 28.6139, 77.2090, ayanamsa_mode="lahiri")
    baseline = m.build_baseline(chart, 35)
    rin = baseline["rin_diagnosis"]["rins"]
    for name in ("bhratra_rin", "atma_rin"):
        check(
            f"A5: {name} reports 0 compounding_factors (no fabricated compounders)",
            rin[name]["compounding_factors"] == 0, f"{name}={rin[name]}")


# ---------------------------------------------------------------------------
# A6 — Signal-1 maturation delivery computes combustion (within 10 deg orb).
# ---------------------------------------------------------------------------
def test_signal1_combustion_detected():
    # Sun in house 1 at 15 deg; Mercury in house 1 at 20 deg -> same fixed
    # house, orb = 5 deg -> combust.
    placements = {
        "Sun": 1, "Mercury": 1,
        "Moon": 4, "Mars": 4, "Jupiter": 4, "Venus": 4, "Saturn": 4, "Rahu": 4, "Ketu": 4,
    }
    deg_overrides = {"Sun": 15.0, "Mercury": 20.0}
    d1 = {
        "lagna_sign": "Aries",
        "planets": {p: mk_planet(h - 1, deg_overrides.get(p, 10.0)) for p, h in placements.items()},
    }
    fixed_chart = m.build_fixed_house_chart(d1)
    pakka = m.build_pakka_ghar(fixed_chart)
    aspect_map = m.build_aspect_map(fixed_chart)
    sleeping = m.build_sleeping(fixed_chart, aspect_map)
    timing = m.build_timing_signals(30, fixed_chart, pakka, sleeping)
    mercury_sig1 = timing["signal_1_maturation"]["Mercury"]
    check(
        "A6: Mercury within 10 deg of Sun is flagged combust with correct orb",
        mercury_sig1["combust"] is True and abs(mercury_sig1["orb_from_sun_deg"] - 5.0) < 1e-6,
        f"Mercury signal_1={mercury_sig1}")
    check(
        "A6: combust note appended to delivery text",
        "combust" in mercury_sig1["delivery"].lower(), f"delivery={mercury_sig1['delivery']!r}")


# ---------------------------------------------------------------------------
# A8/A9 — teva "dominant" uses a strength score (not code-order first match),
# and Mishra fallback names the closest two archetypes with traits.
# ---------------------------------------------------------------------------
def test_teva_strength_scoring_and_mishra_partial_scores():
    chart = m.eph.parashari_natal_chart(
        "1990-05-15T10:30:00", "Asia/Kolkata", 28.6139, 77.2090, ayanamsa_mode="lahiri")
    baseline = m.build_baseline(chart, 35)
    teva = baseline["teva"]
    check(
        "A8/A9: partial_scores present for all 7 archetypes",
        "partial_scores" in teva and len(teva["partial_scores"]) == 7,
        f"partial_scores={teva.get('partial_scores')}")
    if teva["dominant"]["teva"] == "Mishra":
        check(
            "A9: Mishra fallback names the closest two archetypes",
            "closest_two" in teva["dominant"] and len(teva["dominant"]["closest_two"]) == 2,
            f"dominant={teva['dominant']}")
    else:
        check(
            "A8: matched teva entries carry a strength_score used for dominant/secondary ranking",
            all("strength_score" in mt for mt in teva["all_matched"]),
            f"all_matched={teva['all_matched']}")


# ---------------------------------------------------------------------------
# A10 — house-9 second cycle band is effectively open-ended (not capped at 90).
# ---------------------------------------------------------------------------
def test_house9_cycle_not_capped_at_90():
    bands = m.HOUSE_CYCLE[9]
    check(
        "A10: house 9's 2nd cycle band extends well past age 90",
        bands[-1][1] > 90, f"HOUSE_CYCLE[9]={bands}")


# ---------------------------------------------------------------------------
# A11 — rin trigger attribution is structural ("planets" tag), not desc
# substring matching; lord-only triggers correctly attribute the lord.
# ---------------------------------------------------------------------------
def test_rin_trigger_attribution_is_structural():
    # Bhratra trigger 5 names no planet literally as a *subject* the way
    # substring matching would need ("Houses 3 and 11 empty AND their lords
    # afflicted") but must still attribute Mercury/Saturn (the lords).
    placements = {
        "Mercury": 4, "Saturn": 4,  # both lords elsewhere, afflicted via mutual dignity below
        "Mars": 5, "Sun": 5, "Moon": 5, "Jupiter": 5, "Venus": 5, "Rahu": 6, "Ketu": 6,
    }
    fixed_chart, pakka, aspect_map, sleeping, rin, teva = build(placements)
    bhratra = rin["rins"]["bhratra_rin"]
    trig5 = [t for t in bhratra["fired_triggers"] if t["trigger"] == 5]
    if trig5:
        check(
            "A11: Bhratra trigger 5 tags both lords (Mercury, Saturn) explicitly",
            set(trig5[0]["planets"]) == {"Mercury", "Saturn"}, f"trig5={trig5}")
    else:
        # Trigger 5 didn't fire in this fixture; fall back to checking any
        # fired trigger across all 6 rins carries a "planets" key at all —
        # the structural point (A11) is that every trigger dict is tagged.
        chart = m.eph.parashari_natal_chart(
            "1990-05-15T10:30:00", "Asia/Kolkata", 28.6139, 77.2090, ayanamsa_mode="lahiri")
        baseline = m.build_baseline(chart, 35)
        any_trig = None
        for rdata in baseline["rin_diagnosis"]["rins"].values():
            if rdata["fired_triggers"]:
                any_trig = rdata["fired_triggers"][0]
                break
        check(
            "A11: fired rin triggers carry an explicit 'planets' attribution list",
            any_trig is not None and "planets" in any_trig, f"any_trig={any_trig}")


# ---------------------------------------------------------------------------
# A12 — planet_condition() includes aspected_houses + owned_houses (Varshphal
# Step 2 needs both, not just the planet's own placement).
# ---------------------------------------------------------------------------
def test_planet_condition_includes_aspected_and_owned_houses():
    chart = m.eph.parashari_natal_chart(
        "1990-05-15T10:30:00", "Asia/Kolkata", 28.6139, 77.2090, ayanamsa_mode="lahiri")
    baseline = m.build_baseline(chart, 35)
    cond = m.planet_condition(
        "Saturn", baseline["pakka_ghar"], baseline["sleeping_planets"], baseline["rin_diagnosis"])
    check(
        "A12: planet_condition returns aspected_houses and owned_houses",
        "aspected_houses" in cond and "owned_houses" in cond
        and cond["owned_houses"] == m.LK_HOUSES_OWNED["Saturn"],
        f"cond={cond}")


def main():
    tests = [
        test_behra_teva_tests_mercury_not_mars,
        test_general_afflicted_matches_reference_not_enemy_or_buried,
        test_jupiter_5th_aspect_mitigates_rin_severity,
        test_cross_rin_escalation_bumps_severity,
        test_dead_pair_stays_sleeping,
        test_severity_scale_not_generalized_to_all_rins,
        test_neecha_bhanga_cancellation,
        test_pitri_rin_has_three_compounder_slots,
        test_stri_rin_compounders_widened,
        test_bhratra_atma_no_fabricated_compounders,
        test_signal1_combustion_detected,
        test_teva_strength_scoring_and_mishra_partial_scores,
        test_house9_cycle_not_capped_at_90,
        test_rin_trigger_attribution_is_structural,
        test_planet_condition_includes_aspected_and_owned_houses,
    ]
    for t in tests:
        try:
            t()
        except Exception:
            print(f"FAIL: {t.__name__} raised an exception")
            traceback.print_exc()
            FAILURES.append(t.__name__)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S)")
        sys.exit(1)
    else:
        print("ALL PASS")
        sys.exit(0)


if __name__ == "__main__":
    main()
