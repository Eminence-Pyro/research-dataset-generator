"""
studies/immunization_aba/run.py

Study-specific runner for:
  "Pattern of Patient (Caregiver) Satisfaction with Immunization Services
   at Urban Primary Health Centers in Wards I–IV, Aba North LGA, Abia State"

This file is the ONLY thing you need to touch to customise the run.
The core generator modules in rdg/core/ are untouched.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np

from rdg.core import demographics as demo_gen
from rdg.core import questionnaire as q_gen
from rdg.core import observation   as obs_gen
from rdg.core import validator
from rdg.core import exporter
from studies.immunization_aba.config import (
    STUDY_TITLE, STUDY_SETTING, N_RESPONDENTS,
    FACILITIES, RESPONDENTS_PER_FACILITY, FACILITY_EFFECTS,
)

STUDY_DIR  = Path(__file__).parent
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output" / "immunization_aba"

# Ordinal encoding maps for demographics
ORDINAL_MAPS = {
    "education": {
        "No formal education": 1,
        "Primary":             2,
        "Secondary":           3,
        "Tertiary":            4,
    },
    "income_monthly_naira": {
        "No income (<10,000)":      1,
        "Low (10,000\u201330,000)": 2,
        "Middle (30,001\u201370,000)": 3,
        "High (>70,000)":           4,
    },
    "previous_visits": {
        "1 (first visit)": 1,
        "2\u20133":        2,
        "4\u20135":        3,
        "6+":             4,
    },
}

# SPSS numeric encoding maps (for every categorical field)
SPSS_MAPS = {
    "gender":         {"Male": 1, "Female": 2},
    "marital_status": {"Married":1,"Single":2,"Widowed":3,"Divorced/Separated":4},
    "education":      {"No formal education":1,"Primary":2,"Secondary":3,"Tertiary":4},
    "occupation":     {"Trader/Business":1,"Civil servant":2,"Housewife":3,
                       "Student":4,"Artisan":5,"Unemployed":6},
    "income_monthly_naira": {
        "No income (<10,000)":1,"Low (10,000\u201330,000)":2,
        "Middle (30,001\u201370,000)":3,"High (>70,000)":4,
    },
    "number_of_children": {"1":1,"2":2,"3":3,"4":4,"5+":5},
    "previous_visits":    {"1 (first visit)":1,"2\u20133":2,"4\u20135":3,"6+":4},
    "satisfaction_category": {
        "Highly Dissatisfied":1,"Dissatisfied":2,"Neutral":3,
        "Satisfied":4,"Highly Satisfied":5,
    },
}

CODEBOOK = [
    ("respondent_id",      "Respondent ID",             "String",  "Nominal", "R001–R120",        "Unique identifier"),
    ("age",                "Age of respondent",          "Integer", "Scale",   "18–55",            "Years"),
    ("gender",             "Gender",                     "String",  "Nominal", "Male/Female",      ""),
    ("marital_status",     "Marital status",             "String",  "Nominal", "4 categories",     ""),
    ("education",          "Highest education level",    "String",  "Ordinal", "4 levels",         ""),
    ("education_rank",     "Education rank (numeric)",   "Integer", "Ordinal", "1–4",              "1=None, 4=Tertiary"),
    ("occupation",         "Occupation",                 "String",  "Nominal", "6 categories",     ""),
    ("income_monthly_naira","Monthly income (Naira)",    "String",  "Ordinal", "4 bands",          ""),
    ("distance_to_facility_km","Distance to PHC (km)",  "Float",   "Scale",   "0.1–20",           "Exponential distribution"),
    ("number_of_children", "Number of children",         "String",  "Ordinal", "1/2/3/4/5+",       ""),
    ("child_age_months",   "Index child age (months)",   "Integer", "Scale",   "0–23",             ""),
    ("previous_visits",    "Previous facility visits",   "String",  "Ordinal", "4 categories",     ""),
    ("SAQ1–SEQ5",          "Questionnaire responses",    "Integer", "Ordinal", "1–5",              "1=V.Dissatisfied, 5=V.Satisfied"),
    ("mean_A–mean_E",      "Section mean score",         "Float",   "Scale",   "1.00–5.00",        "Mean of 5 items per section"),
    ("overall_mean",       "Overall satisfaction mean",  "Float",   "Scale",   "1.00–5.00",        "Mean of all 25 items"),
    ("satisfaction_category","Satisfaction category",    "String",  "Ordinal", "5 categories",     "Derived from overall_mean"),
    ("cleanliness…",       "Observation checklist items","String",  "Nominal", "Yes/No",           "Facility observation"),
    ("obs_yes_count",      "Total observation Yes count","Integer", "Scale",   "0–10",             ""),
]


def run(seed: int | None = None) -> None:
    """
    Run the full generation pipeline for this study.
    Pass a different seed to regenerate a statistically equivalent but distinct dataset.
    """
    from rdg.utils.console import banner, step, done
    import time

    seed = seed or 42
    rng  = np.random.default_rng(seed)

    banner(STUDY_TITLE, STUDY_SETTING)

    # ── Facility assignments ──────────────────────────────────
    facility_ids: list[int] = []
    for fac in FACILITIES:
        facility_ids.extend([fac["id"]] * RESPONDENTS_PER_FACILITY)

    # ── Step 1: Demographics ──────────────────────────────────
    step(1, 5, "Generating demographics")
    t = time.time()
    respondents = demo_gen.generate(
        n           = N_RESPONDENTS,
        config_path = STUDY_DIR / "demographics.json",
        rng         = rng,
        ordinal_maps = ORDINAL_MAPS,
    )
    print(f"     {len(respondents)} respondents  ({time.time()-t:.1f}s)")

    # ── Step 2: Questionnaire ─────────────────────────────────
    step(2, 5, "Generating questionnaire responses")
    t = time.time()
    q_rows = q_gen.generate(
        respondents          = respondents,
        questionnaire_path   = STUDY_DIR / "questionnaire.json",
        rng                  = rng,
        facility_assignments = facility_ids,
        facility_effects     = FACILITY_EFFECTS,
    )
    print(f"     25 items × {len(q_rows)} respondents  ({time.time()-t:.1f}s)")

    # ── Step 3: Observation ───────────────────────────────────
    step(3, 5, "Generating observation checklist")
    t = time.time()
    obs_rows = obs_gen.generate(
        respondents          = respondents,
        questionnaire_rows   = q_rows,
        facility_assignments = facility_ids,
        observation_path     = STUDY_DIR / "observation.json",
        rng                  = rng,
    )
    print(f"     10 items × {len(obs_rows)} visits  ({time.time()-t:.1f}s)")

    # ── Step 4: Validate ──────────────────────────────────────
    step(4, 5, "Validating dataset")
    report = validator.run(
        demographics        = respondents,
        questionnaire_rows  = q_rows,
        observations        = obs_rows,
        expected_n          = N_RESPONDENTS,
        edu_rank_field      = "education_rank",
        distance_field      = "distance_to_facility_km",
    )
    s = report["summary"]
    print(f"     ✓ {s['n_passed']} passed  ⚠ {s['n_warnings']} warnings  ✗ {s['n_errors']} errors")
    if not s["ready_to_export"]:
        print("\n  ✗ Validation failed. Check errors above. Aborting export.")
        for e in report["errors"]:
            print(f"    • {e}")
        return

    # ── Step 5: Export ────────────────────────────────────────
    step(5, 5, "Exporting outputs")
    paths = exporter.export(
        demographics        = respondents,
        questionnaire_rows  = q_rows,
        observations        = obs_rows,
        validation_report   = report,
        output_dir          = OUTPUT_DIR,
        study_title         = STUDY_TITLE,
        seed                = seed,
        spss_maps           = SPSS_MAPS,
        codebook_rows       = CODEBOOK,
    )
    done(paths)
