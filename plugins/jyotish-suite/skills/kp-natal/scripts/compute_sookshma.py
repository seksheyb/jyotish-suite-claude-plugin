#!/usr/bin/env python3
"""
Sookshma Dasha Computation
===========================
Given a Moon sidereal longitude AT BIRTH and a target window (or current moment),
computes the running Mahadasha-Bhukti-Antara-Sookshma at any specified date,
or generates the full Sookshma sequence inside a given Antara.

Usage (compute current DBA-Sookshma):
    python compute_sookshma.py \
      --moon_long 321.387 \
      --birth_datetime "1991-07-30T10:20:00" \
      --tz "Asia/Kolkata" \
      --target_datetime "2026-05-01T22:30:00"

Usage (list all Sookshmas in a specific Antara):
    python compute_sookshma.py \
      --moon_long 321.387 \
      --birth_datetime "1991-07-30T10:20:00" \
      --tz "Asia/Kolkata" \
      --list_antara "Mercury-Venus-Saturn"
"""

import argparse
import json
from datetime import datetime, timedelta
import pytz


VIM_SEQ = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
             "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
NAK_ARC = 360.0 / 27.0
TOTAL = 120

NAKSHATRAS = [
    ("Ashwini", "Ketu"), ("Bharani", "Venus"), ("Krittika", "Sun"),
    ("Rohini", "Moon"), ("Mrigashira", "Mars"), ("Ardra", "Rahu"),
    ("Punarvasu", "Jupiter"), ("Pushya", "Saturn"), ("Ashlesha", "Mercury"),
    ("Magha", "Ketu"), ("Purva Phalguni", "Venus"), ("Uttara Phalguni", "Sun"),
    ("Hasta", "Moon"), ("Chitra", "Mars"), ("Swati", "Rahu"),
    ("Vishakha", "Jupiter"), ("Anuradha", "Saturn"), ("Jyestha", "Mercury"),
    ("Mula", "Ketu"), ("Purva Ashadha", "Venus"), ("Uttara Ashadha", "Sun"),
    ("Shravana", "Moon"), ("Dhanishtha", "Mars"), ("Shatabhisha", "Rahu"),
    ("Purva Bhadrapada", "Jupiter"), ("Uttara Bhadrapada", "Saturn"), ("Revati", "Mercury"),
]


def compute_birth_dasha_state(moon_long_sid, birth_dt):
    """Compute MD lord at birth + remaining MD years."""
    nak_idx = int(moon_long_sid // NAK_ARC)
    nak_start = nak_idx * NAK_ARC
    star_lord = NAKSHATRAS[nak_idx][1]
    pos_in_nak = moon_long_sid - nak_start
    fraction = pos_in_nak / NAK_ARC
    md_total = VIM_YEARS[star_lord]
    md_remaining = md_total * (1 - fraction)
    md_elapsed = md_total * fraction
    md_started = birth_dt - timedelta(days=md_elapsed * 365.25)
    return star_lord, md_started, md_total


def build_dasha_tree(moon_long_sid, birth_dt, n_md=4):
    """Build full DBA-Sookshma tree starting from birth."""
    star_lord, md0_start, md0_total = compute_birth_dasha_state(moon_long_sid, birth_dt)

    tree = []
    md_lord = star_lord
    md_idx = VIM_SEQ.index(md_lord)
    md_start = md0_start

    for i in range(n_md):
        cur_lord = VIM_SEQ[(md_idx + i) % 9]
        cur_yrs = VIM_YEARS[cur_lord]
        md_end = md_start + timedelta(days=cur_yrs * 365.25)

        bhuktis = []
        bd_idx = VIM_SEQ.index(cur_lord)
        bd_start = md_start
        for bd_off in range(9):
            bd_lord = VIM_SEQ[(bd_idx + bd_off) % 9]
            bd_yrs = VIM_YEARS[bd_lord]
            bd_dur_days = (cur_yrs * bd_yrs / 120) * 365.25
            bd_end = bd_start + timedelta(days=bd_dur_days)

            antaras = []
            ad_idx = VIM_SEQ.index(bd_lord)
            ad_start = bd_start
            for ad_off in range(9):
                ad_lord = VIM_SEQ[(ad_idx + ad_off) % 9]
                ad_yrs = VIM_YEARS[ad_lord]
                ad_dur_days = (bd_dur_days * ad_yrs / 120)
                ad_end = ad_start + timedelta(days=ad_dur_days)

                sookshmas = []
                sd_idx = VIM_SEQ.index(ad_lord)
                sd_start = ad_start
                for sd_off in range(9):
                    sd_lord = VIM_SEQ[(sd_idx + sd_off) % 9]
                    sd_yrs = VIM_YEARS[sd_lord]
                    sd_dur_days = (ad_dur_days * sd_yrs / 120)
                    sd_end = sd_start + timedelta(days=sd_dur_days)
                    sookshmas.append({
                        "sd_lord": sd_lord,
                        "start": sd_start.isoformat(),
                        "end": sd_end.isoformat(),
                        "duration_days": round(sd_dur_days, 2),
                    })
                    sd_start = sd_end

                antaras.append({
                    "ad_lord": ad_lord,
                    "start": ad_start.isoformat(),
                    "end": ad_end.isoformat(),
                    "duration_days": round(ad_dur_days, 2),
                    "sookshmas": sookshmas,
                })
                ad_start = ad_end

            bhuktis.append({
                "bd_lord": bd_lord,
                "start": bd_start.isoformat(),
                "end": bd_end.isoformat(),
                "duration_days": round(bd_dur_days, 2),
                "antaras": antaras,
            })
            bd_start = bd_end

        tree.append({
            "md_lord": cur_lord,
            "md_total_years": cur_yrs,
            "start": md_start.isoformat(),
            "end": md_end.isoformat(),
            "bhuktis": bhuktis,
        })
        md_start = md_end

    return tree


def find_running(tree, target_dt):
    """Find running MD-BD-AD-SD at target_dt."""
    for md in tree:
        if datetime.fromisoformat(md["start"]) <= target_dt < datetime.fromisoformat(md["end"]):
            for bd in md["bhuktis"]:
                if datetime.fromisoformat(bd["start"]) <= target_dt < datetime.fromisoformat(bd["end"]):
                    for ad in bd["antaras"]:
                        if datetime.fromisoformat(ad["start"]) <= target_dt < datetime.fromisoformat(ad["end"]):
                            for sd in ad["sookshmas"]:
                                if datetime.fromisoformat(sd["start"]) <= target_dt < datetime.fromisoformat(sd["end"]):
                                    return {
                                        "md": md["md_lord"], "md_period": (md["start"], md["end"]),
                                        "bd": bd["bd_lord"], "bd_period": (bd["start"], bd["end"]),
                                        "ad": ad["ad_lord"], "ad_period": (ad["start"], ad["end"]),
                                        "sd": sd["sd_lord"], "sd_period": (sd["start"], sd["end"]),
                                        "sd_duration_days": sd["duration_days"],
                                    }
    return None


def find_antara(tree, md_name, bd_name, ad_name):
    """Return the named antara block with all its sookshmas."""
    for md in tree:
        if md["md_lord"] != md_name:
            continue
        for bd in md["bhuktis"]:
            if bd["bd_lord"] != bd_name:
                continue
            for ad in bd["antaras"]:
                if ad["ad_lord"] == ad_name:
                    return {
                        "md": md_name, "bd": bd_name, "ad": ad_name,
                        "ad_start": ad["start"], "ad_end": ad["end"],
                        "ad_duration_days": ad["duration_days"],
                        "sookshmas": ad["sookshmas"],
                    }
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--moon_long", type=float, required=True,
                       help="Moon sidereal longitude at birth, in decimal degrees")
    parser.add_argument("--birth_datetime", required=True)
    parser.add_argument("--tz", required=True)
    parser.add_argument("--target_datetime", default=None,
                       help="Find running DBA-SD at this moment")
    parser.add_argument("--list_antara", default=None,
                       help='List all sookshmas in "MD-BD-AD" format e.g. "Mercury-Mercury-Saturn"')
    parser.add_argument("--n_md", type=int, default=5)
    args = parser.parse_args()

    tz = pytz.timezone(args.tz)
    birth_dt = tz.localize(datetime.fromisoformat(args.birth_datetime)).astimezone(pytz.UTC).replace(tzinfo=None)

    tree = build_dasha_tree(args.moon_long, birth_dt, n_md=args.n_md)

    out = {"birth": args.birth_datetime, "moon_long_sid": args.moon_long}

    if args.target_datetime:
        target = tz.localize(datetime.fromisoformat(args.target_datetime)).astimezone(pytz.UTC).replace(tzinfo=None)
        running = find_running(tree, target)
        out["target"] = args.target_datetime
        out["running"] = running

    if args.list_antara:
        parts = args.list_antara.split("-")
        if len(parts) != 3:
            print("ERROR: --list_antara must be MD-BD-AD format")
            return
        antara = find_antara(tree, parts[0], parts[1], parts[2])
        out["antara_query"] = args.list_antara
        out["antara_breakdown"] = antara

    if not args.target_datetime and not args.list_antara:
        # Default: print first 4 MDs summary
        out["mahadasha_summary"] = [
            {"md": md["md_lord"], "start": md["start"], "end": md["end"]}
            for md in tree
        ]

    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
