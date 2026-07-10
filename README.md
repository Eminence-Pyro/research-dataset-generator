# Research Analysis Toolkit

A reusable, domain-driven Python toolkit for academic research workflows.

## What This Is

Research Analysis Toolkit (RAT) is a modular software product that covers
the full lifecycle of academic research data work:

| Step | Module |
|------|--------|
| Define your study | `research_engine/models/` — core domain objects |
| Parse questionnaires | `research_engine/parsers/` — Word/JSON instrument import |
| Calculate sample size | `research_engine/generators/sample_size.py` |
| Generate synthetic datasets | `research_engine/generators/` |
| Validate datasets | `research_engine/validators/` |
| Run descriptive analysis | `research_engine/analysis/` |
| Export to Excel/SPSS/PDF/Word | `research_engine/exporters/` |
| Produce Chapter Four tables | `research_engine/reports/` |

## Why This Exists

Generating research data manually is:
- Time consuming and inconsistent
- Prone to unrealistic variable relationships
- Difficult to reproduce when the questionnaire changes
- Disconnected from downstream analysis and reporting

This toolkit solves those problems by treating research as a **domain**,
not a spreadsheet task. Every module works with the same core objects —
`Study`, `Questionnaire`, `Question`, `Variable`, `Respondent`, `Dataset` —
so a malaria study, an HIV study, a school health study, and an
immunization study all use identical workflows.

## Architecture

```
research-analysis-toolkit/
│
├── research_engine/               # Core library
│   ├── models/                    # Domain model — the language of the application
│   │   ├── study.py               # Study, Facility
│   │   ├── questionnaire.py       # Questionnaire, Section, Question
│   │   ├── variable.py            # Variable, VariableDictionary
│   │   ├── respondent.py          # Respondent, Response
│   │   └── dataset.py             # Dataset
│   │
│   ├── parsers/                   # Import instruments and frameworks
│   │   ├── questionnaire_parser.py
│   │   ├── workbook_reader.py
│   │   └── json_loader.py
│   │
│   ├── generators/                # Synthetic data production
│   │   ├── demographics.py
│   │   ├── responses.py
│   │   ├── observations.py
│   │   └── sample_size.py
│   │
│   ├── validators/                # Consistency and quality checks
│   │   └── dataset_validator.py
│   │
│   ├── analysis/                  # Statistical analysis
│   │   ├── frequencies.py
│   │   ├── descriptives.py
│   │   ├── crosstabs.py
│   │   └── charts.py
│   │
│   ├── exporters/                 # Output formats
│   │   ├── excel_exporter.py
│   │   ├── csv_exporter.py
│   │   ├── spss_exporter.py
│   │   ├── pdf_exporter.py
│   │   └── word_exporter.py
│   │
│   └── reports/                   # Chapter Four and summary report builders
│       ├── chapter_four.py
│       └── codebook.py
│
├── studies/                       # One package per research study
│   └── immunization_aba/          # Caregiver satisfaction, Aba North LGA
│
├── output/                        # Generated files — git-ignored
├── main.py                        # CLI entry point
├── requirements.txt
└── PROJECT_JOURNAL.md
```

## Version Roadmap

### v1.0 — Domain Foundation *(current)*
- [ ] Core domain model (`Study`, `Questionnaire`, `Question`, `Variable`, `Respondent`, `Dataset`)
- [ ] JSON-based questionnaire loader
- [ ] Demographics generator (plugs into domain model)
- [ ] Likert response generator with configurable causal model
- [ ] Observation checklist generator
- [ ] Statistical validator
- [ ] Excel exporter (multi-sheet, formatted)
- [ ] CSV and SPSS-ready export
- [ ] Plain-text validation report

### v1.1 — Analysis Layer
- [ ] Frequency tables
- [ ] Descriptive statistics
- [ ] Cross-tabulations
- [ ] Chart generation (bar, pie, histogram)

### v1.2 — Report Generation
- [ ] Chapter Four table builder
- [ ] Codebook generator
- [ ] Word (.docx) export
- [ ] PDF export

### v1.3 — Import Layer
- [ ] Word questionnaire parser
- [ ] Excel analysis framework reader / writer
- [ ] Variable dictionary from questionnaire

### v2.0 — Web Interface
- [ ] Streamlit or FastAPI web UI
- [ ] Study configuration via browser
- [ ] Dataset preview and download

## Quick Start

```bash
git clone https://github.com/Eminence-Pyro/research-analysis-toolkit.git
cd research-analysis-toolkit
pip install -r requirements.txt
python main.py --list
python main.py --study immunization_aba
```

## Current Studies

| Study | Folder | N | Status |
|-------|--------|---|--------|
| Caregiver Satisfaction with Immunization Services, Aba North LGA | `immunization_aba` | 120 | ✅ v0 |

## Technologies

- Python 3.12+
- numpy, pandas, scipy
- openpyxl (Excel)
- python-docx (Word export — v1.2)
- reportlab (PDF export — v1.2)
- rich (optional terminal output)

## License

MIT
