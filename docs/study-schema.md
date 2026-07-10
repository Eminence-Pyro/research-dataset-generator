# Study Schema Reference (v1.0)

Each study lives in its own folder under `studies/` and is defined by four JSON files.
The engine reads these files; no Python changes are needed to add a new study.

---

## config.json

Study-level metadata, facility definitions, and pipeline parameters.

```json
{
  "schema_version": "1.0",
  "rat_version":    "1.0.0",

  "title":               "Pattern of Caregiver Satisfaction with Immunization Services",
  "design":              "Cross-sectional",
  "setting":             "Urban PHCs, Wards I-IV, Aba North LGA, Abia State",
  "population":          "Caregivers of children 0-23 months attending immunization clinics",
  "sampling_technique":  "Consecutive sampling",
  "target_n":            120,

  "facilities": [
    { "id": 1, "name": "Ward I PHC",   "satisfaction_effect":  0.3 },
    { "id": 2, "name": "Ward II PHC",  "satisfaction_effect":  0.0 },
    { "id": 3, "name": "Ward III PHC", "satisfaction_effect":  0.2 },
    { "id": 4, "name": "Ward IV PHC",  "satisfaction_effect": -0.1 }
  ]
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | ✅ | Always `"1.0"` for this format |
| `rat_version` | string | — | Toolkit version used to create the study |
| `title` | string | ✅ | Full study title |
| `design` | string | ✅ | Study design (e.g. Cross-sectional, Cohort) |
| `setting` | string | ✅ | Geographic and institutional setting |
| `population` | string | ✅ | Target population description |
| `sampling_technique` | string | ✅ | Sampling method used |
| `target_n` | integer | ✅ | Required sample size |
| `facilities` | array | ✅ | List of study sites |
| `facilities[].id` | integer | ✅ | Unique facility identifier |
| `facilities[].name` | string | ✅ | Facility display name |
| `facilities[].satisfaction_effect` | float | ✅ | Causal model offset (±0.0–0.5 typical) |

---

## questionnaire.json

The study instrument — sections and Likert items.

```json
{
  "schema_version": "1.0",
  "title": "Caregiver Satisfaction with Immunization Services Questionnaire",

  "sections": {
    "A": {
      "title": "Satisfaction with Reception / Registration",
      "construct": "reception_satisfaction",
      "items": [
        {
          "number": "A1",
          "variable_name": "saq1",
          "text": "The registration process was quick and efficient.",
          "scale": "Likert5"
        }
      ]
    }
  }
}
```

**Section fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `title` | ✅ | Section heading |
| `construct` | — | Latent construct label (used in analysis) |
| `items` | ✅ | Array of question objects |

**Item fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `number` | ✅ | Question number (e.g. `A1`, `B3`) |
| `variable_name` | ✅ | Column name in dataset (e.g. `saq1`) |
| `text` | ✅ | Full question text |
| `scale` | ✅ | `"Likert5"` (1–5) or `"Likert4"` (1–4) |

---

## demographics.json

Population demographic distributions. The generator draws samples from these.

```json
{
  "schema_version": "1.0",
  "variables": [
    {
      "name": "age",
      "label": "Age of caregiver (years)",
      "distribution": "normal",
      "params": { "mean": 27, "std": 6, "min": 15, "max": 55 },
      "type": "continuous"
    },
    {
      "name": "gender",
      "label": "Gender",
      "distribution": "categorical",
      "params": { "Female": 0.78, "Male": 0.22 },
      "type": "categorical"
    }
  ]
}
```

**Supported distributions:**

| Distribution | Required params | Use for |
|-------------|----------------|---------|
| `normal` | `mean`, `std`, `min`, `max` | Age, distance, continuous measures |
| `exponential` | `scale`, `min`, `max` | Skewed continuous (e.g. wait times) |
| `categorical` | `{label: probability, ...}` | Gender, education, occupation |
| `uniform` | `min`, `max` | Uniformly distributed integers |

---

## observation.json

Facility environment checklist — observed Yes/No items.

```json
{
  "schema_version": "1.0",
  "checklist": [
    {
      "variable_name": "cleanliness",
      "label": "Facility is visibly clean",
      "anchor": "environment",
      "base_probability": 0.7
    },
    {
      "variable_name": "waiting_time",
      "label": "Waiting time is acceptable",
      "anchor": "service",
      "distance_sensitive": true,
      "base_probability": 0.65
    }
  ]
}
```

**Item fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `variable_name` | ✅ | Column name in dataset |
| `label` | ✅ | Observation item text |
| `anchor` | ✅ | `"environment"` or `"service"` — links to satisfaction sections |
| `base_probability` | ✅ | Baseline P(Yes) across facilities |
| `distance_sensitive` | — | If `true`, distance reduces P(Yes) |

---

## Adding a New Study

1. Create `studies/your_study_name/`
2. Add the four JSON files above (copy from `studies/immunization_aba/` and adapt)
3. Ensure `"schema_version": "1.0"` is present in all four files
4. Copy `studies/immunization_aba/run.py` and update `ORDINAL_MAPS`, `SPSS_MAPS`, `CROSSTAB_PAIRS`
5. Run: `python main.py run --study your_study_name`

No changes to `research_engine/` are needed.
