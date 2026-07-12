"""
research_engine/exporters/spss_exporter.py
Stage 10 — Export Engine  |  Milestone 1.1.A (SPSS syntax)

Produces a complete SPSS syntax file (.sps) ready for direct import into SPSS.

Blocks generated:
  1. Header comment (study metadata + instructions)
  2. GET DATA (imports the SPSS-ready CSV)
  3. VARIABLE LABELS (all 53+ variables)
  4. VALUE LABELS (categorical + Likert items)
  5. MISSING VALUES (9 for categoricals, 99 for continuous)
  6. FORMATS (F2.0 / F5.2 / F8.2)
  7. VARIABLE LEVEL (NOMINAL / ORDINAL / SCALE)
  8. EXECUTE

Public API
----------
    export_spss_syntax(
        variable_dictionary, spss_maps, output_dir,
        csv_filename, study_title, seed
    ) -> Path
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from research_engine.models.variable import VariableDictionary, MeasurementScale


_MAX_LINE = 76

LIKERT_5_LABELS = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree",
}


def _spss_name(name: str) -> str:
    return name.upper().replace(" ", "_")[:64]


def _q(text: str) -> str:
    return "'" + str(text).replace("'", "''") + "'"


def _section(title: str) -> str:
    bar = "*" + "=" * 70 + "."
    return "\n" + bar + "\n* " + title + "\n" + bar + "\n"


def _wrap_varlist(names: list[str], prefix: str = "  ") -> str:
    lines, line = [], prefix
    for n in names:
        if len(line) + len(n) + 1 > _MAX_LINE:
            lines.append(line)
            line = "    " + n
        else:
            line += " " + n
    if line.strip():
        lines.append(line)
    return "\n".join(lines)


def _is_numeric_coded(codes: dict) -> bool:
    """True if all keys are digit strings — these are auto-coded Likert values, not real labels."""
    return bool(codes) and all(str(k).strip().isdigit() for k in codes)


def _header_comment(study_title: str, csv_filename: str,
                    seed: int, n_vars: int) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return "\n".join([
        "* " + "=" * 70 + ".",
        f"* SPSS Syntax — {study_title}",
        f"* Generated : {now}",
        f"* Seed      : {seed}",
        f"* Variables : {n_vars}",
        f"* Data file : {csv_filename}",
        "*",
        "* INSTRUCTIONS:",
        "*   1. Update the FILE= path below to your CSV location.",
        "*   2. Open SPSS > File > New > Syntax",
        "*   3. Paste this file and click Run > All",
        "* " + "=" * 70 + ".",
        "",
    ])


def _get_data_block(csv_filename: str, spss_names: list[str]) -> str:
    return "\n".join([
        _section("DATA IMPORT"),
        "GET DATA",
        "  /TYPE=TXT",
        f"  /FILE={_q(csv_filename)}",
        "  /ENCODING='UTF8'",
        "  /DELIMITERS=','",
        "  /QUALIFIER='\"'",
        "  /ARRANGEMENT=DELIMITED",
        "  /FIRSTCASE=2",
        _wrap_varlist(spss_names, "  /VARIABLES="),
        "  /MAP.",
        "CACHE.",
        "EXECUTE.",
        "",
    ])


def _variable_labels_block(vd: VariableDictionary) -> str:
    lines = [_section("VARIABLE LABELS"), "VARIABLE LABELS"]
    for var in vd:
        sname = _spss_name(var.name)
        label = var.label or var.name.replace("_", " ").title()
        lines.append(f"  {sname:<22} {_q(label)}")
    lines.append("  .")
    return "\n".join(lines) + "\n"


def _value_labels_block(vd: VariableDictionary, spss_maps: dict) -> str:
    """
    VALUE LABELS block.

    Priority order per variable:
      1. spss_maps (from run.py) — if present and has non-numeric keys
      2. variable.spss_codes — if present and has non-numeric keys
      3. Likert detection: ORDINAL + section A–E + allowed [1,2,3,4,5]
         → apply standard Strongly Disagree…Strongly Agree labels
    """
    blocks = [_section("VALUE LABELS"), "VALUE LABELS"]

    for var in vd:
        sname = _spss_name(var.name)

        # ── Priority 1: explicit spss_maps from run.py ────────
        if var.name in spss_maps:
            codes = {str(lbl): int(code)
                     for lbl, code in spss_maps[var.name].items()}
            if not _is_numeric_coded(codes):
                sorted_c = sorted(codes.items(), key=lambda x: x[1])
                block = "\n".join(
                    [f"  /{sname}"] +
                    [f"    {code} {_q(lbl)}" for lbl, code in sorted_c]
                )
                blocks.append(block)
                continue

        # ── Priority 2: variable.spss_codes (non-numeric keys) ─
        if var.spss_codes and not _is_numeric_coded(var.spss_codes):
            codes = {str(lbl): int(code)
                     for lbl, code in var.spss_codes.items()}
            sorted_c = sorted(codes.items(), key=lambda x: x[1])
            block = "\n".join(
                [f"  /{sname}"] +
                [f"    {code} {_q(lbl)}" for lbl, code in sorted_c]
            )
            blocks.append(block)
            continue

        # ── Priority 3: Likert items ──────────────────────────
        is_likert = (
            var.scale == MeasurementScale.ORDINAL
            and var.section is not None
            and var.section not in ("demographics", "observations",
                                    "observation_environment",
                                    "observation_service")
            and var.allowed_values == [1, 2, 3, 4, 5]
        )
        if is_likert:
            block = "\n".join(
                [f"  /{sname}"] +
                [f"    {code} {_q(label)}"
                 for code, label in LIKERT_5_LABELS.items()]
            )
            blocks.append(block)

    blocks.append("  .")
    return "\n".join(blocks) + "\n"


def _missing_values_block(vd: VariableDictionary) -> str:
    lines = [_section("MISSING VALUES")]
    for var in vd:
        sname = _spss_name(var.name)
        code  = "99" if var.scale == MeasurementScale.SCALE else "9"
        lines.append(f"MISSING VALUES {sname} ({code}).")
    return "\n".join(lines) + "\n"


def _formats_block(vd: VariableDictionary) -> str:
    lines = [_section("VARIABLE FORMATS")]
    for var in vd:
        sname = _spss_name(var.name)
        is_likert_item = (
            var.scale == MeasurementScale.ORDINAL
            and var.section not in (None, "demographics", "observations",
                                    "observation_environment", "observation_service")
        )
        if var.scale == MeasurementScale.SCALE:
            fmt = "F8.2"
        elif is_likert_item:
            fmt = "F5.2"
        else:
            fmt = "F2.0"
        lines.append(f"FORMATS {sname} ({fmt}).")
    return "\n".join(lines) + "\n"


def _variable_level_block(vd: VariableDictionary) -> str:
    nominal, ordinal, scale = [], [], []
    for var in vd:
        sname = _spss_name(var.name)
        if var.scale == MeasurementScale.NOMINAL:
            nominal.append(sname)
        elif var.scale == MeasurementScale.ORDINAL:
            ordinal.append(sname)
        else:
            scale.append(sname)

    lines = [_section("MEASUREMENT LEVELS")]
    for names, level in [(nominal, "NOMINAL"), (ordinal, "ORDINAL"), (scale, "SCALE")]:
        if names:
            lines.append("VARIABLE LEVEL")
            lines.append(_wrap_varlist(names))
            lines.append(f"  ({level}).")
    return "\n".join(lines) + "\n"


def export_spss_syntax(
    variable_dictionary: VariableDictionary,
    spss_maps:           dict,
    output_dir:          str | Path,
    csv_filename:        str = "data.csv",
    study_title:         str = "Research Study",
    seed:                int = 42,
) -> Path:
    """
    Write a complete SPSS syntax file (.sps).

    Parameters
    ----------
    variable_dictionary : all study variables
    spss_maps           : {field: {label: code}} from run.py SPSS_MAPS
    output_dir          : directory to write the .sps file
    csv_filename        : filename of the SPSS CSV (researcher updates path)
    study_title         : study title for the header comment
    seed                : random seed for the header comment

    Returns
    -------
    Path — absolute path to the .sps file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug     = study_title[:30].replace(" ", "_") if study_title else "study"
    filepath = output_dir / f"{slug}_{ts}.sps"

    spss_names = [_spss_name(v.name) for v in variable_dictionary]

    blocks = [
        _header_comment(study_title, csv_filename, seed, len(spss_names)),
        _get_data_block(csv_filename, spss_names),
        _variable_labels_block(variable_dictionary),
        _value_labels_block(variable_dictionary, spss_maps),
        _missing_values_block(variable_dictionary),
        _formats_block(variable_dictionary),
        _variable_level_block(variable_dictionary),
        _section("EXECUTE") + "EXECUTE.\n",
    ]

    filepath.write_text("\n".join(blocks), encoding="utf-8")
    return filepath
