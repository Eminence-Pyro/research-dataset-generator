# PROJECT_JOURNAL.md
## Research Analysis Toolkit — Living Development Log

> Updated after every significant stage. Permanent record of every
> architectural decision, naming convention, design pattern, and lesson learned.
>
> Unlike code comments (which explain *what*), this file explains *why*
> — the reasoning behind every structural choice.

---

## Entry #001 — Project Genesis

**Date:** July 2026
**Stage:** 0 — Conception and Scope Definition
**Status:** ✅ Complete

### From Dataset Generator to Research Analysis Toolkit

The project began as a dataset generator for a single study (caregiver
satisfaction with immunization services, Aba North LGA). A working
v0 was produced — 120 respondents, 25 Likert items, observation checklist,
13/13 validation checks passing, Excel/CSV/SPSS output.

The scope was then deliberately broadened.

**The key insight:** Dataset generation is one step in a larger workflow.
Researchers need:
1. A way to define their study (questionnaire, variables, population)
2. Sample size calculation
3. Synthetic dataset generation
4. Statistical validation
5. Descriptive analysis (frequencies, crosstabs, descriptive stats)
6. Export to multiple formats (Excel, SPSS, PDF, Word)
7. Chapter Four table production

All of those steps belong to the same domain. Building them as isolated
scripts means rebuilding the same plumbing repeatedly. Building them as
a unified toolkit means each new study gets all of them for free.

---

## Entry #002 — Architecture Decision: Domain Model First

**Date:** July 2026
**Stage:** 1 — Architecture
**Status:** ✅ Complete

### The Decision

The first code written will not touch Excel, CSV, or any file format.
It will define the core research domain objects:

```
Study          — the research project itself
Questionnaire  — the instrument used to collect data
Section        — a grouping of related questions
Question       — a single item (Likert, open-ended, categorical, etc.)
Variable       — the analytical representation of a question
VariableDictionary — the complete mapping from question to variable
Respondent     — one participant in the study
Response       — one respondent's answer to one question
Dataset        — the full collection of respondent records
Facility       — a study site (PHC, hospital, school, etc.)
```

### Why This Matters

Every other module — parsers, generators, validators, exporters,
analysis — will receive and return these objects. They will never
directly manipulate raw dicts, DataFrames, or spreadsheet rows
unless they are the exporter that produces the final file.

This means:

- A new study takes exactly one step: instantiate a Study with its
  Questionnaire. Nothing else changes.
- Exporters can be swapped (Word instead of PDF) without touching
  the analysis layer.
- Validators check the domain objects, not raw CSV rows.
- The same analysis functions work for a malaria study, a maternal
  health study, and a school health study.

### The Anti-Pattern Being Avoided

The v0 generator worked directly with Python dicts throughout. This
meant that every module had to know the internal structure of every
other module's output — a fragile coupling. If the demographics
generator renamed a field, every downstream module broke.

Domain objects with defined interfaces prevent this entirely.

---

## Entry #003 — Naming and Package Structure

**Date:** July 2026
**Stage:** 1 — Architecture
**Status:** ✅ Complete

### Why `research_engine/` not `generator/`

The original package was called `generator/`. This is now too narrow.
The toolkit does much more than generate data.

`research_engine/` signals that this is the core analytical engine of the
product — the part that will grow to cover the full research workflow.

### Why `models/` is the first sub-package

In software architecture, the models (or domain) layer is conventionally
written before everything else because it defines the shared vocabulary
of the entire codebase. All other layers depend on it; it depends on nothing.

This is sometimes called "domain-driven design" — building software around
the real-world concepts of the domain rather than around technical
conveniences (like spreadsheet rows or database tables).

### Package structure and what each layer does

```
research_engine/
├── models/        The core domain — defines what things ARE
├── parsers/       Reads external formats into domain objects
├── generators/    Creates domain objects synthetically
├── validators/    Checks domain objects for consistency
├── analysis/      Computes statistics on domain objects
├── exporters/     Writes domain objects to external formats
└── reports/       Produces structured research documents
```

The data flow is:
  parsers / generators
        ↓
    domain objects (models)
        ↓
   validators → analysis
        ↓
  exporters → reports

Nothing in `analysis/` knows about Excel.
Nothing in `exporters/` knows how data was generated or parsed.
This separation is the most important structural property of the project.

---

## What's Next

**Stage 2 — Domain Model Implementation**

Define and implement all domain model classes in `research_engine/models/`.
This is the most important design decision in the project. The quality of
this layer determines how cleanly every other module can be written.

Priority order:
1. `variable.py`     — Variable and VariableDictionary (most fundamental)
2. `questionnaire.py` — Questionnaire, Section, Question
3. `study.py`        — Study, Facility
4. `respondent.py`   — Respondent, Response
5. `dataset.py`      — Dataset

No parsers, no generators, no exporters until the domain model is complete
and reviewed.

---

## Changelog

| Entry | Stage | Description |
|-------|-------|-------------|
| #001  | 0     | Project genesis — scope broadened to Research Analysis Toolkit |
| #002  | 1     | Architecture decision — domain model first |
| #003  | 1     | Package structure — `research_engine/`, layer responsibilities |
