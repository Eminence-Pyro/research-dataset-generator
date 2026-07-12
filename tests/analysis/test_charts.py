"""
tests/analysis/test_charts.py

Unit and integration tests for research_engine/analysis/charts.py

Tests verify:
  - Each chart function returns a matplotlib Figure without error
  - Saved PNG files are non-empty and > 10 KB
  - all_charts() produces the expected number of files
  - Dark theme is applied (figure facecolor)
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ── Fixtures ──────────────────────────────────────────────────

STUDY_DIR = Path(__file__).parent.parent.parent / "studies" / "immunization_aba"


@pytest.fixture(scope="module")
def pipeline(tmp_path_factory):
    """Full pipeline (analyse stage only) — shared across all chart tests."""
    pytest.importorskip("matplotlib")
    from research_engine.workflow import Pipeline

    out = tmp_path_factory.mktemp("charts_pipeline")
    p = Pipeline(STUDY_DIR, output_dir=out, seed=42)
    p.analyse()
    p.analysis.reliability = p.reliability
    return p


@pytest.fixture(scope="module")
def likert_summary(pipeline):
    return pipeline.analysis.likert_summary


@pytest.fixture(scope="module")
def freq_tables(pipeline):
    return pipeline.analysis.freq_tables


@pytest.fixture(scope="module")
def reliability_report(pipeline):
    return pipeline.reliability


@pytest.fixture(scope="module")
def dataset(pipeline):
    return pipeline.dataset


@pytest.fixture(scope="module")
def questionnaire(pipeline):
    return pipeline.bundle.questionnaire


# ── Helpers ───────────────────────────────────────────────────

def is_valid_figure(fig) -> bool:
    import matplotlib.figure
    return isinstance(fig, matplotlib.figure.Figure)


# ══════════════════════════════════════════════════════════════
# Chart generation tests
# ══════════════════════════════════════════════════════════════

class TestLikertBarChart:
    def test_returns_figure(self, likert_summary):
        from research_engine.analysis.charts import likert_bar_chart
        fig = likert_bar_chart(likert_summary, section_key="A")
        assert is_valid_figure(fig)

    def test_has_correct_title(self, likert_summary):
        from research_engine.analysis.charts import likert_bar_chart
        fig = likert_bar_chart(likert_summary, section_key="A")
        ax = fig.axes[0]
        assert "A" in ax.get_title()

    def test_correct_number_of_bars(self, likert_summary):
        from research_engine.analysis.charts import likert_bar_chart
        fig = likert_bar_chart(likert_summary, section_key="A")
        ax = fig.axes[0]
        n_items = len(likert_summary.items_for_section("A"))
        assert len(ax.patches) == n_items

    def test_dark_background(self, likert_summary):
        from research_engine.analysis.charts import likert_bar_chart
        fig = likert_bar_chart(likert_summary, section_key="A")
        fc = fig.get_facecolor()
        # Should not be white — dark theme applied
        assert fc != (1.0, 1.0, 1.0, 1.0)

    def test_works_without_section_key(self, likert_summary):
        from research_engine.analysis.charts import likert_bar_chart
        fig = likert_bar_chart(likert_summary)
        assert is_valid_figure(fig)


class TestDemographicPieChart:
    def test_returns_figure(self, freq_tables):
        from research_engine.analysis.charts import demographic_pie_chart
        ft = next(ft for ft in freq_tables if "gender" in ft.variable_name.lower())
        fig = demographic_pie_chart(ft)
        assert is_valid_figure(fig)

    def test_title_is_set(self, freq_tables):
        from research_engine.analysis.charts import demographic_pie_chart
        ft = next(ft for ft in freq_tables if "education" in ft.variable_name.lower())
        fig = demographic_pie_chart(ft, title="Education Level")
        assert "Education" in fig.axes[0].get_title()


class TestDemographicBarChart:
    def test_returns_figure(self, freq_tables):
        from research_engine.analysis.charts import demographic_bar_chart
        ft = next(ft for ft in freq_tables if "occupation" in ft.variable_name.lower())
        fig = demographic_bar_chart(ft)
        assert is_valid_figure(fig)

    def test_bar_count_matches_categories(self, freq_tables):
        from research_engine.analysis.charts import demographic_bar_chart
        ft = next(ft for ft in freq_tables if "occupation" in ft.variable_name.lower())
        n_cats = len([r for r in ft.rows if str(r.value) not in ("Total","Missing","TOTAL")])
        fig = demographic_bar_chart(ft)
        ax = fig.axes[0]
        assert len(ax.patches) == n_cats


class TestReliabilityBarChart:
    def test_returns_figure(self, reliability_report):
        from research_engine.analysis.charts import reliability_bar_chart
        fig = reliability_bar_chart(reliability_report)
        assert is_valid_figure(fig)

    def test_bar_count_matches_sections(self, reliability_report):
        from research_engine.analysis.charts import reliability_bar_chart
        valid_sections = [s for s in reliability_report.sections
                         if s.alpha == s.alpha]  # not nan
        fig = reliability_bar_chart(reliability_report)
        ax = fig.axes[0]
        assert len(ax.patches) == len(valid_sections)


class TestSatisfactionHeatmap:
    def test_returns_figure(self, dataset, questionnaire):
        from research_engine.analysis.charts import satisfaction_heatmap
        fig = satisfaction_heatmap(dataset, questionnaire)
        assert is_valid_figure(fig)


# ══════════════════════════════════════════════════════════════
# File save tests
# ══════════════════════════════════════════════════════════════

class TestSaveChart:
    def test_saves_png_file(self, tmp_path, likert_summary):
        from research_engine.analysis.charts import likert_bar_chart, save_chart
        fig  = likert_bar_chart(likert_summary, section_key="B")
        path = save_chart(fig, tmp_path, "test_chart")
        assert path.exists()
        assert path.suffix == ".png"
        assert path.stat().st_size > 10_000   # > 10 KB

    def test_creates_output_dir(self, tmp_path, likert_summary):
        from research_engine.analysis.charts import likert_bar_chart, save_chart
        nested = tmp_path / "a" / "b" / "charts"
        fig    = likert_bar_chart(likert_summary, section_key="C")
        path   = save_chart(fig, nested, "nested_chart")
        assert path.exists()


# ══════════════════════════════════════════════════════════════
# all_charts() integration test
# ══════════════════════════════════════════════════════════════

class TestAllCharts:
    def test_produces_multiple_charts(self, tmp_path, pipeline):
        from research_engine.analysis.charts import all_charts
        paths = all_charts(pipeline.analysis, tmp_path)
        # At least 5 likert sections + several demographic charts + reliability
        assert len(paths) >= 10

    def test_all_files_are_png(self, tmp_path, pipeline):
        from research_engine.analysis.charts import all_charts
        paths = all_charts(pipeline.analysis, tmp_path / "all_check")
        for p in paths:
            assert p.suffix == ".png", f"Non-PNG file: {p}"

    def test_all_files_are_nonzero(self, tmp_path, pipeline):
        from research_engine.analysis.charts import all_charts
        paths = all_charts(pipeline.analysis, tmp_path / "size_check")
        for p in paths:
            assert p.stat().st_size > 10_000, f"File too small: {p} ({p.stat().st_size} bytes)"
