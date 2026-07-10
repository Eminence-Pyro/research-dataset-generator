# Changelog — Research Analysis Toolkit

All notable changes are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — July 2026

### Added — Full pipeline from domain model to export

**Stage 1 — Core Domain Model**
- `Variable`, `MeasurementScale`, `MissingValueStrategy`, `VariableDictionary`
- `Question`, `QuestionType`, `Section`, `Questionnaire`
- `Facility`, `Study`, `StudyDesign`, `SamplingTechnique`
- `Response`, `Observation`, `Respondent`
- `Dataset`

**Stage 2 — Readers**
- `json_loader.py` — `load_all(study_dir)` → `StudyBundle`
- `workbook_reader.py` — Excel framework reader, lazy-loaded
- `studies/immunization_aba/config.json` — study metadata in JSON

**Stage 3 — Sample Size Engine**
- `sample_size.py` — Cochran (1977), Yamane (1967), Krejcie-Morgan (1970)
- `recommend()` — auto-selects appropriate formula

**Stages 5–7 — Generators**
- `demographics.py` — Respondent objects from distribution configs
- `responses.py` — Response Intelligence Engine (causal model)
- `observations.py` — Facility observation checklist generator

**Stage 8 — Validation Engine**
- `dataset_validator.py` — 14 validation checks, `ValidationReport`

**Stage 9 — Analysis Engine**
- `frequencies.py` — `FrequencyTable`, cumulative percentages
- `descriptives.py` — `DescriptiveStats`, `LikertSummary` (Chapter Four table)
- `crosstabs.py` — `CrosstabResult`, chi-square, Cramer's V

**Stage 10 — Export Engine**
- `excel_exporter.py` — 9-sheet formatted .xlsx workbook
- `csv_exporter.py` — raw CSV + SPSS-ready CSV + label file

**Stage 11 — CLI**
- `cli/interface.py` — `run`, `list`, `info`, `validate`, `sample` commands
- `main.py` — single entry point

**Documentation**
- `README.md` — complete project documentation with architecture, causal model, roadmap
- `PROJECT_JOURNAL.md` — 9 development entries (entries #001–#009)
- `LEARNING_JOURNAL.md` — 12 engineering lessons
- `CHANGELOG.md` — this file

---

## [0.1.0] — June 2026

### Added — Initial dataset generator (v0)
- `rdg/` package — plain dict-based dataset generator
- `generator/demographics.py` — demographic data generation
- `generator/questionnaire.py` — Likert response generation
- `generator/observation.py` — facility observation generation
- `generator/exporter.py` — Excel and CSV export
- `config/` — study configuration in JSON files
- `main.py` — basic runner script (no CLI)

### Known limitations (resolved in v1.0)
- No domain model — all data as plain dicts
- No causal model — random Likert values
- No validation engine
- No analysis engine (no frequencies, descriptives, or crosstabs)
- No CLI — single hardcoded script
- Study config in Python files requiring import
