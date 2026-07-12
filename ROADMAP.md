# ROADMAP

The master plan for the Research Analysis Toolkit.

> **Principle:** Freeze the folder structure from this point. Every commit adds
> working functionality. No more renaming packages. No more moving files.

---

## Version Status

| Version | Status | Focus |
|---------|--------|-------|
| v0.1.0 | ✅ Released | Initial dataset generator (rdg/ package) |
| v1.0.0 | ✅ Released | Full pipeline: domain model → generators → validation → analysis → export → CLI |
| v1.1.0 | 🔄 In progress | Word parser, Chapter Four export, SPSS syntax, Cronbach alpha, schema validation |
| v2.0.0 | 📋 Planned | AI interpretation, charts, web dashboard, REST API, multi-design support |

---

## v1.1.0 — In Progress

**Goal:** Make the output directly usable for thesis submission without manual editing.

### Milestone 1.1.A — Document Output
- [ ] `exporters/word_exporter.py` — Chapter Four tables formatted for thesis submission
  - Frequency tables (APA style)
  - Descriptive statistics table (per-item mean, SD, interpretation)
  - Cross-tabulation tables with chi-square stats
  - Section summary table
- [ ] `exporters/spss_exporter.py` — SPSS syntax file (.sps)
  - `VARIABLE LABELS` block for all variables
  - `VALUE LABELS` block for all categorical variables
  - `MISSING VALUES` declarations

### Milestone 1.1.B — Reliability Analysis
- [ ] `analysis/reliability.py` — Cronbach's alpha
  - Per-section alpha coefficient
  - Item-total correlation
  - "Alpha if item deleted" statistics
  - Interpretation: < 0.6 poor, 0.6–0.7 acceptable, 0.7–0.8 good, > 0.8 excellent

### Milestone 1.1.C — Schema Validation
- [ ] `parsers/json_loader.py` — validate all four study JSON files against `schemas/`
  before running the pipeline
- [ ] `jsonschema` added to `requirements.txt`

### Milestone 1.1.D — Tests
- [ ] `tests/models/test_variable.py` — expand to cover all Variable fields ✅ scaffolded
- [ ] `tests/models/test_questionnaire.py` ✅ scaffolded
- [ ] `tests/workflow/test_pipeline.py` — end-to-end Pipeline test ✅ scaffolded
- [ ] `tests/generators/test_sample_size.py` — Cochran/Yamane/Krejcie edge cases
- [ ] `tests/validators/test_dataset_validator.py` — each of the 14 checks
- [ ] `tests/analysis/test_frequencies.py`, `test_descriptives.py`, `test_crosstabs.py`
- [ ] CI: `pytest` in GitHub Actions on every push

---

## v2.0.0 — Planned

**Goal:** A framework useful to researchers beyond the original author.

### 2.A — AI-Assisted Questionnaire Interpretation
- [ ] `parsers/questionnaire_parser.py` — parse real Word .docx instruments
  - Extract section headings, question numbers, question text
  - Auto-identify Likert scale type from response options
  - Build VariableDictionary from parsed instrument
- [ ] LLM integration — map free-text questions to construct categories
- [ ] Output: auto-generated `questionnaire.json` from real instrument

### 2.B — Extended Analysis
- [ ] `analysis/reliability.py` — Cronbach's alpha (moved from v1.1 if delayed)
- [ ] `analysis/correlation.py` — Pearson/Spearman correlation matrix
- [ ] `analysis/regression.py` — binary logistic regression (satisfied vs not)
- [ ] `analysis/anova.py` — one-way ANOVA (satisfaction by education group)

### 2.C — Chart Generation
- [ ] `analysis/charts.py` — matplotlib-based chart builders
  - Bar chart: frequency distributions
  - Grouped bar: crosstab visualisation
  - Box plot: Likert distributions by demographic group
  - Heat map: correlation matrix

### 2.D — PDF Report
- [ ] `exporters/pdf_exporter.py` — auto-generated research summary PDF
  - Study metadata cover page
  - Methods section (auto-generated from config.json)
  - Chapter Four tables (from AnalysisBundle)
  - Charts embedded
  - Validation summary

### 2.E — Web Dashboard
- [ ] `web_app/` — Streamlit application
  - Upload or select a study
  - Configure seed, N, and output formats
  - Live preview of frequency tables and charts
  - One-click download of all output files

### 2.F — REST API
- [ ] `api/` — FastAPI application
  - `POST /studies/{id}/run` — run a study pipeline
  - `GET  /studies/{id}/results` — retrieve last run results
  - `GET  /studies` — list available studies
  - Stateless: each request runs a fresh pipeline with a given seed

### 2.G — Multi-Study Design Support
- [ ] New generator plugins for different study types:
  - `generators/kap_responses.py` — Knowledge, Attitude, Practice surveys
  - `generators/prevalence.py` — prevalence/screening studies
  - `generators/cohort.py` — longitudinal cohort data
- [ ] Study type field in `config.json`: `"design_type": "cross_sectional" | "kap" | "cohort"`
- [ ] Pipeline selects appropriate generator plugin by design type

### 2.H — Plugin Ecosystem
- [ ] `plugins/` auto-discovery — scan a `plugins/` directory on startup
- [ ] Plugin documentation template
- [ ] Example community plugin: Google Sheets exporter

### 2.I — Multi-Language Support
- [ ] Variable labels, question text, and interpretation strings are i18n strings
- [ ] `locale/` directory: `en.json`, `fr.json`, `ha.json`, `yo.json`, `ig.json`
- [ ] `--language` flag on CLI

---

## Frozen Architecture

As of v1.1.0-dev, the folder structure is frozen.

```
research-analysis-toolkit/
├── main.py
├── requirements.txt
├── ROADMAP.md
├── README.md
├── CHANGELOG.md
├── PROJECT_JOURNAL.md
├── LEARNING_JOURNAL.md
│
├── research_engine/          ← Core engine — never imports from interfaces
│   ├── models/
│   ├── parsers/
│   ├── generators/
│   ├── validators/
│   ├── analysis/
│   ├── exporters/
│   ├── reports/
│   ├── workflow/
│   ├── plugins/
│   └── cli/
│
├── studies/                  ← Study configs — no engine changes needed
│   └── immunization_aba/
│
├── examples/                 ← Study templates for common designs
│   ├── simple_health_survey/
│   └── malaria_kap/
│
├── tests/                    ← All tests mirror research_engine/ structure
│   ├── models/
│   ├── parsers/
│   ├── generators/
│   ├── validators/
│   ├── analysis/
│   ├── exporters/
│   └── workflow/
│
├── schemas/                  ← JSON Schema files for study config validation
│   ├── study.schema.json
│   ├── questionnaire.schema.json
│   ├── demographics.schema.json
│   └── observation.schema.json
│
├── docs/                     ← Technical documentation
│   ├── architecture/
│   │   ├── overview.md
│   │   ├── workflow.md
│   │   ├── plugins.md
│   │   └── study-schema.md
│   └── adr/
│       ├── README.md
│       └── 001-005-*.md
│
├── legacy/                   ← Archived v0 code (rdg/ package)
│   └── rdg/
│
└── output/                   ← Generated files (gitignored)
```

**Do not create new top-level directories unless this ROADMAP is updated first.**
