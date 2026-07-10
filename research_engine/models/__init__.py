"""
research_engine/models/
The domain model — the core language of the Research Analysis Toolkit.

Every other package (parsers, generators, validators, exporters, analysis,
reports) works with objects defined here. Nothing in this package depends
on any other package in the project.

Modules
-------
variable.py        — Variable, MeasurementScale, VariableDictionary
questionnaire.py   — Questionnaire, Section, Question
study.py           — Study, Facility
respondent.py      — Respondent, Response
dataset.py         — Dataset
"""
