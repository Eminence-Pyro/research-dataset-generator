# Research Analysis Toolkit (RAT)

> **Synthetic Research Dataset Generator & Statistical Analysis Engine**
>
> Build statistically valid, reproducible datasets for academic research —
> from questionnaire design to formatted Excel output — in a single command.

[![Version](https://img.shields.io/badge/version-1.1.0--dev-orange)](#)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![License](https://img.shields.io/badge/license-MIT-green)](#)
[![v1.0.0 Release](https://img.shields.io/badge/stable-v1.0.0-brightgreen)](https://github.com/Eminence-Pyro/research-analysis-toolkit/releases/tag/v1.0.0)

---

## What This Is

The Research Analysis Toolkit is a Python framework for generating, validating,
and exporting synthetic research datasets that are statistically coherent and
academically defensible.

It was built to support health-science research where:

- The study instrument is finalised but data collection is ongoing
- A complete, realistic dataset is needed for analysis planning and code testing
- Outputs must match SPSS/Excel formats expected by supervisors and examiners

The toolkit deliberately separates the **engine** (domain model, generators,
validators, analysis, exporters) from any **interface** (CLI, web app, API).
The same engine can power all of them without modification.

---

## Quick Start

```bash
git clone https://github.com/Eminence-Pyro/research-analysis-toolkit.git
cd research-analysis-toolkit
pip install -r requirements.txt

# Run the full pipeline
python main.py run --study immunization_aba

# Explore other commands
python main.py list
python main.py info   --study immunization_aba
python main.py sample --population 1200
```

---

## Feature Status

> Features are explicitly labelled to reflect the actual state of the codebase.
> ✅ = implemented and tested · 🔄 = in progress · 📋 = planned

### Core Engine

| Feature | Status | Notes |
|---------|--------|-------|
| Domain model (Study, Questionnaire, Respondent, Dataset) | ✅ | 10 typed domain classes |
| JSON study config loader (`load_all()`) | ✅ | Returns `StudyBundle` |
| Excel workbook reader | ✅ | Lazy-loaded, study-agnostic |
| Sample size engine (Cochran, Yamane, Krejcie-Morgan) | ✅ | `recommend()` auto-selects formula |
| Demographic generator | ✅ | Normal, exponential, categorical distributions |
| **Causal response model** | ✅ | Education/income/distance → satisfaction |
| Facility observation generator | ✅ | Env/service consistency enforced |
| Validation engine (14 checks) | ✅ | `ValidationReport` with structured results |
| Frequency tables | ✅ | Cumulative %, sort by value or frequency |
| Descriptive statistics | ✅ | Mean, SD, Likert interpretation |
| Cross-tabulation + chi-square | ✅ | Cramer's V effect size |
| 9-sheet Excel exporter | ✅ | Raw, demographics, Likert, obs, descriptives, freq, crosstabs, codebook, validation |
| Raw CSV exporter | ✅ | All labelled values |
| SPSS-ready CSV exporter | ✅ | Numeric codes + label file |
| CLI (5 commands) | ✅ | `run`, `list`, `info`, `validate`, `sample` |
| **Workflow / orchestration layer** | ✅ | `Pipeline` class, interface-agnostic |
| **Plugin registry** | ✅ | Foundation for custom exporters/generators |
| Schema versioning in study configs | ✅ | `schema_version: "1.0"` in all study JSONs |

### In Progress (v1.1)

| Feature | Status | Notes |
|---------|--------|-------|
| Word (.docx) questionnaire parser | 🔄 | Auto-extract variables from real instruments |
| Word (.docx) Chapter Four export | 🔄 | APA-formatted tables for thesis submission |
| SPSS syntax (.sps) generator | 🔄 | Direct SPSS import with variable labels |
| Cronbach's alpha reliability analysis | 🔄 | Per-section internal consistency |

### Planned (v2.0)

| Feature | Status | Notes |
|---------|--------|-------|
| AI-assisted questionnaire interpretation | 📋 | LLM reads instrument → builds VariableDictionary |
| Correlation matrix (Pearson/Spearman) | 📋 | Between-scale variable relationships |
| ANOVA | 📋 | Satisfaction scores by demographic group |
| Logistic/linear regression | 📋 | Predictors of overall satisfaction |
| Chart generation (bar, pie, histogram) | 📋 | Matplotlib/plotly output |
| PDF report | 📋 | Auto-generated research summary |
| Web dashboard (Streamlit) | 📋 | Point-and-click generation + visualisation |
| Desktop application | 📋 | Same engine, GUI interface |
| REST API | 📋 | `POST /studies/{id}/run` |
| Multi-language support | 📋 | i18n for questionnaire labels |
| Study template scaffolding | 📋 | `python main.py new --template health_satisfaction` |
| Multiple study designs | 📋 | Cohort, case-control, KAP, prevalence |
| Plugin marketplace | 📋 | Community-contributed generators/exporters |

---

## Architecture

```
research-analysis-toolkit/
│
├── main.py                           ← Single CLI entry point
├── requirements.txt
│
├── research_engine/                  ← Core engine (interface-agnostic)
│   ├── models/                       ← Domain model (Stage 1)
│   │   ├── variable.py               ← Variable, VariableDictionary, MeasurementScale
│   │   ├── questionnaire.py          ← Question, Section, Questionnaire
│   │   ├── study.py                  ← Study, Facility, StudyDesign
│   │   ├── respondent.py             ← Respondent, Response, Observation
│   │   └── dataset.py                ← Dataset
│   │
│   ├── parsers/                      ← Readers (Stage 2)
│   │   ├── json_loader.py            ← load_all() → StudyBundle
│   │   ├── workbook_reader.py        ← Excel framework reader
│   │   └── questionnaire_parser.py   ← 🔄 Word/PDF instrument parser
│   │
│   ├── generators/                   ← Data generators (Stages 3–7)
│   │   ├── sample_size.py            ← Cochran, Yamane, Krejcie-Morgan
│   │   ├── demographics.py           ← Respondent objects from distributions
│   │   ├── responses.py              ← Causal response model ⭐
│   │   └── observations.py           ← Facility observation checklists
│   │
│   ├── validators/                   ← Data quality (Stage 8)
│   │   └── dataset_validator.py      ← 14 checks, ValidationReport
│   │
│   ├── analysis/                     ← Statistics (Stage 9)
│   │   ├── frequencies.py            ← FrequencyTable, cumulative %
│   │   ├── descriptives.py           ← DescriptiveStats, LikertSummary
│   │   └── crosstabs.py              ← CrosstabResult, chi-square, Cramer's V
│   │
│   ├── exporters/                    ← File output (Stage 10)
│   │   ├── excel_exporter.py         ← 9-sheet .xlsx workbook
│   │   ├── csv_exporter.py           ← Raw CSV + SPSS CSV + label file
│   │   ├── word_exporter.py          ← 🔄 Chapter Four .docx tables
│   │   └── spss_exporter.py          ← 🔄 SPSS syntax (.sps) generator
│   │
│   ├── workflow/                     ← Orchestration layer ✅ NEW
│   │   └── pipeline.py               ← Pipeline class — all 5 stages
│   │
│   ├── plugins/                      ← Plugin system ✅ NEW
│   │   └── registry.py               ← PluginRegistry — decorator + lookup
│   │
│   ├── reports/                      ← Report builders
│   │   ├── chapter_four.py           ← 🔄 Chapter Four table generator
│   │   └── codebook.py               ← Codebook document builder
│   │
│   └── cli/                          ← CLI (Stage 11)
│       └── interface.py              ← run, list, info, validate, sample
│
├── studies/                          ← Study configurations (study-agnostic engine)
│   └── immunization_aba/
│       ├── config.json               ← Study metadata (schema_version: "1.0")
│       ├── questionnaire.json
│       ├── demographics.json
│       ├── observation.json
│       └── run.py                    ← Study-specific maps and pipeline call
│
└── output/                           ← Generated files (gitignored)
```

### Future interface layout (v2)

```
research-analysis-toolkit/
├── research_engine/    ← Shared engine (unchanged)
├── cli/                ← Current CLI
├── web_app/            ← 📋 Streamlit dashboard
├── desktop_app/        ← 📋 GUI application
├── api/                ← 📋 REST API (FastAPI)
└── studies/
```

---

## The Causal Response Model

The Response Intelligence Engine models the known causal relationships
in health-service satisfaction research:

```
Education level    ──► base satisfaction   (+0.15 per rank above median)
Income level       ──► base satisfaction   (+0.08 per rank above median)
Previous visits    ──► base satisfaction   (+0.12 — familiarity effect)
Facility effect    ──► base satisfaction   (configurable ±0.0 to ±0.5)
Distance to PHC    ──► environment section  (penalty up to −0.5)
Distance to PHC    ──► waiting-time item    (penalty up to −1.0)
Gaussian noise     ──► each item           (SD=0.55 — realistic variance)
```

Validated correlations (seed=42, N=120):
- r(education, satisfaction) = **+0.601** ✓ (expected: positive)
- r(distance, satisfaction)  = **−0.027** ✓ (expected: negative)
- r(environment, obs_count)  = **+0.365** ✓ (expected: positive)

---

## CLI Commands

```bash
# Full pipeline: generate → validate → analyse → export
python main.py run      --study immunization_aba [--seed N] [--output DIR]

# Discover studies
python main.py list

# Study metadata (no generation)
python main.py info     --study immunization_aba

# Validate without exporting
python main.py validate --study immunization_aba [--seed N]

# Sample size calculator
python main.py sample   --population N [--confidence 0.95] [--margin 0.05]
```

---

## Adding a New Study

1. Create `studies/your_study/`
2. Add four JSON files (copy from `studies/immunization_aba/` and adapt):
   `config.json`, `questionnaire.json`, `demographics.json`, `observation.json`
3. Set `"schema_version": "1.0"` in `config.json`
4. Copy `studies/immunization_aba/run.py` → `studies/your_study/run.py`
5. Update `ORDINAL_MAPS`, `SPSS_MAPS`, `CROSSTAB_PAIRS`
6. Run: `python main.py run --study your_study`

**No changes to `research_engine/` are needed for a new study.**

---

## Validation Checks (14)

| # | Check | Threshold |
|---|-------|-----------|
| 1 | Sample size | n ≥ target |
| 2 | Unique IDs | 0 duplicates |
| 3 | Likert range | All items 1–5 |
| 4 | Education–satisfaction correlation | r > 0 |
| 5 | Distance–satisfaction correlation | r < 0 |
| 6 | Observation–environment consistency | r > 0 |
| 7 | Missing values | 0 |
| 8 | Satisfaction distribution | Counts reported |
| 9–13 | Section means (×5) | Mean + SD per section |
| 14 | Facility representation | All facilities present |

---

## Current Study: Immunization Satisfaction, Aba North

| | |
|-|-|
| Title | Pattern of Caregiver Satisfaction with Immunization Services |
| Design | Cross-sectional |
| Setting | Urban PHCs, Wards I–IV, Aba North LGA, Abia State |
| Population | Caregivers of children 0–23 months |
| Sample | 120 (30 per facility × 4 PHCs) |
| Sampling | Consecutive |
| Instrument | 25 Likert items, 5 sections |
| Derived variables | Section means + overall mean + satisfaction category |
| Observations | 10-item facility checklist |
| **Total variables** | **58** |

---

## Dependencies

```
numpy>=1.24.0
openpyxl>=3.1.0
scipy>=1.11.0
```

---

## Version History

| Version | Date | Summary |
|---------|------|---------|
| v1.1.0-dev | July 2026 | Workflow/orchestration layer, plugin registry, schema versioning |
| v1.0.0 | July 2026 | Full pipeline: domain model → generators → validation → analysis → export → CLI |
| v0.1.0 | June 2026 | Initial dataset generator (rdg/ package) |

---

## License

MIT — see [LICENSE](LICENSE)
