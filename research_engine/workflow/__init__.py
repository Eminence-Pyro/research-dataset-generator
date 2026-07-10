"""
research_engine/workflow/
v2 Architecture — Workflow / Orchestration Layer

The Pipeline coordinates all stages. CLIs, web apps, and APIs call
Pipeline — they never call generators or exporters directly.

Public API
----------
    from research_engine.workflow import Pipeline, PipelineResult, AnalysisBundle
"""
from research_engine.workflow.pipeline import Pipeline, PipelineResult, AnalysisBundle

__all__ = ["Pipeline", "PipelineResult", "AnalysisBundle"]
