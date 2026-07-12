# ADR 005 — Plugin Registry for Extensibility

**Status:** Accepted
**Date:** July 2026

## Context

Built-in exporters (Excel, CSV, SPSS) were hardcoded in `Pipeline.export()`.
Adding a new export format required modifying the core engine.

## Decision

A `PluginRegistry` allows exporters, generators, analysis methods, and parsers
to be registered by name and retrieved at runtime.

```python
@registry.exporter("word")
class WordExporter:
    def export(self, dataset, output_dir, **kwargs): ...
```

## Consequences

- New formats can be added without touching `research_engine/`
- Community plugins are possible in v2
- Built-in exporters will register themselves as plugins in v1.2
- The registry is populated at import time — no dynamic file scanning needed
