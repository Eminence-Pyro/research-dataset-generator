# Contributing

The Research Analysis Toolkit welcomes contributions — new study configurations,
additional exporters, new analysis methods, and bug fixes.

---

## Where Things Live

| What you want to do | Where to work |
|--------------------|--------------|
| Add a new study | `studies/your_study/` — no engine changes needed |
| Add a new exporter | `research_engine/exporters/` + register as a plugin |
| Add a new analysis method | `research_engine/analysis/` |
| Add a new demographic distribution | `research_engine/generators/demographics.py` |
| Add a new study design (cohort, KAP) | `research_engine/generators/` + new study template |
| Fix a bug | Wherever the bug is — fix at the source, not the consumer |
| Improve documentation | `docs/` for technical detail, `README.md` for product overview |

---

## Code Standards

- **Python 3.10+** — use `match/case`, `X | Y` union types, `from __future__ import annotations`
- **Type hints everywhere** — function signatures, dataclass fields, return types
- **Dataclasses for result objects** — `@dataclass` for `FrequencyTable`, `DescriptiveStats`, etc.
- **No DataFrames in the engine** — analysis results are structured objects with `.to_rows()`
- **Docstrings on every public function** — describe parameters, return type, and one example
- **No study-specific logic in `research_engine/`** — the engine is study-agnostic

---

## Adding an Exporter Plugin

```python
# research_engine/exporters/my_format.py
from research_engine.plugins import registry

@registry.exporter("my_format")
class MyFormatExporter:
    def export(self, dataset, questionnaire, variable_dictionary,
               validation_report, output_dir, **kwargs):
        ...
        return output_path
```

Then import it anywhere before calling `Pipeline.export()` and it will be available.

---

## Reporting Issues

Open an issue on GitHub with:
- The command you ran (including `--seed`)
- The error message or unexpected output
- Your Python version and OS
