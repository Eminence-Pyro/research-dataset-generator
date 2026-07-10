"""
research_engine/generators/
Stages 4–7 — Configuration, Population, Response Intelligence, Observation

All generators receive domain objects and return / mutate domain objects.
None of them write files or know about Excel, SPSS, or CSV.

Public API
----------
    from research_engine.generators import (
        generate_respondents,       # Stage 5 — demographics
        generate_responses,         # Stage 6 — Likert responses (causal model)
        generate_observations,      # Stage 7 — facility observation checklist
        sample_size,                # Stage 4 — Cochran, Yamane, Krejcie-Morgan
    )
"""
from research_engine.generators.demographics  import generate as generate_respondents
from research_engine.generators.responses     import generate as generate_responses
from research_engine.generators.observations  import generate as generate_observations
from research_engine.generators               import sample_size

__all__ = [
    "generate_respondents",
    "generate_responses",
    "generate_observations",
    "sample_size",
]
