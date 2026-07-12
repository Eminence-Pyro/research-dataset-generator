"""
research_engine/parsers/schema_validator.py
Stage 4 — Schema Validation

Validates study configuration JSON files against their JSON Schema
definitions before the loader constructs domain objects.

This prevents cryptic KeyError / AttributeError failures deep in the
generation pipeline. Bad config is caught at the door, not mid-run.

Public API
----------
    validate_config(data, schema_name)   → ValidationResult
    validate_study_dir(study_dir)        → dict[str, ValidationResult]
    assert_valid_study_dir(study_dir)    → None  (raises on failure)

Schemas live in  <repo_root>/schemas/*.schema.json.
The loader locates them relative to this file's location.

Dependencies
------------
    jsonschema >= 4.0   (pip install jsonschema)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── Locate schemas directory ──────────────────────────────────
# This file: research_engine/parsers/schema_validator.py
# schemas/:  <repo_root>/schemas/
_THIS_FILE   = Path(__file__).resolve()
_REPO_ROOT   = _THIS_FILE.parent.parent.parent
_SCHEMAS_DIR = _REPO_ROOT / "schemas"


# ── Schema name → filename map ────────────────────────────────
_SCHEMA_FILES: dict[str, str] = {
    "study":         "study.schema.json",
    "questionnaire": "questionnaire.schema.json",
    "demographics":  "demographics.schema.json",
    "observation":   "observation.schema.json",
}

# ── Config file → schema name map ────────────────────────────
_CONFIG_SCHEMAS: dict[str, str] = {
    "config.json":        "study",
    "questionnaire.json": "questionnaire",
    "demographics.json":  "demographics",
    "observation.json":   "observation",
}


# ══════════════════════════════════════════════════════════════
# Result object
# ══════════════════════════════════════════════════════════════

@dataclass
class ValidationResult:
    """
    Result of a JSON Schema validation check for one config file.

    Attributes
    ----------
    config_name : filename being validated (e.g. "config.json")
    schema_name : schema used (e.g. "study")
    valid       : True if no errors were found
    errors      : list of human-readable error messages
    warnings    : list of non-fatal notices (e.g. optional field missing)
    """
    config_name: str
    schema_name: str
    valid:       bool
    errors:      list[str] = field(default_factory=list)
    warnings:    list[str] = field(default_factory=list)

    def summary(self) -> str:
        status = "PASS" if self.valid else "FAIL"
        detail = f" ({len(self.errors)} error(s))" if not self.valid else ""
        return f"[{status}] {self.config_name}{detail}"

    def __repr__(self) -> str:
        return (
            f"ValidationResult(config={self.config_name!r}, "
            f"valid={self.valid}, errors={len(self.errors)})"
        )


# ══════════════════════════════════════════════════════════════
# Core validation
# ══════════════════════════════════════════════════════════════

def _load_schema(schema_name: str) -> dict:
    """Load a JSON Schema from the schemas/ directory."""
    filename = _SCHEMA_FILES.get(schema_name)
    if filename is None:
        raise ValueError(
            f"Unknown schema name: {schema_name!r}. "
            f"Valid names: {list(_SCHEMA_FILES)}"
        )
    path = _SCHEMAS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Schema file not found: {path}. "
            f"Expected at {_SCHEMAS_DIR}/"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def validate_config(
    data:        dict | Any,
    schema_name: str,
    config_name: str = "",
) -> ValidationResult:
    """
    Validate a config dict against the named JSON Schema.

    Parameters
    ----------
    data        : the parsed JSON data (dict)
    schema_name : one of "study", "questionnaire", "demographics", "observation"
    config_name : display name for error messages (e.g. "config.json")

    Returns
    -------
    ValidationResult — always returns, never raises.
                       Check .valid and .errors on the result.
    """
    try:
        import jsonschema
        from jsonschema import Draft7Validator
    except ImportError:
        return ValidationResult(
            config_name = config_name or schema_name,
            schema_name = schema_name,
            valid       = True,
            warnings    = ["jsonschema not installed — schema validation skipped. "
                           "Run: pip install jsonschema"],
        )

    try:
        schema = _load_schema(schema_name)
    except (ValueError, FileNotFoundError) as exc:
        return ValidationResult(
            config_name = config_name or schema_name,
            schema_name = schema_name,
            valid       = False,
            errors      = [str(exc)],
        )

    validator = Draft7Validator(schema)
    errors    = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
    error_msgs = []
    for err in errors:
        path = " → ".join(str(p) for p in err.path) if err.path else "(root)"
        error_msgs.append(f"  {path}: {err.message}")

    return ValidationResult(
        config_name = config_name or schema_name,
        schema_name = schema_name,
        valid       = len(error_msgs) == 0,
        errors      = error_msgs,
    )


def validate_study_dir(study_dir: str | Path) -> dict[str, ValidationResult]:
    """
    Validate all recognised config files in a study directory.

    Parameters
    ----------
    study_dir : path to the study directory
                (e.g. studies/immunization_aba/)

    Returns
    -------
    dict[str, ValidationResult] — keys are config filenames
    """
    study_dir = Path(study_dir)
    results: dict[str, ValidationResult] = {}

    for filename, schema_name in _CONFIG_SCHEMAS.items():
        config_path = study_dir / filename
        if not config_path.exists():
            # observation.json is optional for studies without observations
            if filename == "observation.json":
                continue
            results[filename] = ValidationResult(
                config_name = filename,
                schema_name = schema_name,
                valid       = False,
                errors      = [f"Required file not found: {config_path}"],
            )
            continue

        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            results[filename] = ValidationResult(
                config_name = filename,
                schema_name = schema_name,
                valid       = False,
                errors      = [f"Invalid JSON: {exc}"],
            )
            continue

        results[filename] = validate_config(data, schema_name, filename)

    return results


def assert_valid_study_dir(study_dir: str | Path) -> None:
    """
    Validate a study directory and raise ConfigValidationError if any
    config file fails schema validation.

    Parameters
    ----------
    study_dir : path to the study directory

    Raises
    ------
    ConfigValidationError — with a detailed error message listing
                            all failing files and their errors.
    """
    results = validate_study_dir(study_dir)
    failures = {f: r for f, r in results.items() if not r.valid}

    if not failures:
        return  # all valid

    lines = ["Study configuration validation failed:", ""]
    for filename, result in failures.items():
        lines.append(f"  ✗ {filename}")
        for err in result.errors:
            lines.append(f"      {err}")
        lines.append("")

    raise ConfigValidationError("\n".join(lines))


class ConfigValidationError(ValueError):
    """
    Raised when a study configuration file fails JSON Schema validation.

    Attributes
    ----------
    message : detailed description of all validation failures
    """
    pass
