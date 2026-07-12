# Examples

Ready-to-run study configurations for common research designs in health sciences.
Each example is a complete study folder — copy it to `studies/` to use it.

## Available Examples

| Example | Design | Variables | N |
|---------|--------|-----------|---|
| [immunization/](immunization/) | Cross-sectional | Caregiver satisfaction, 58 vars | 120 |
| [simple_health_survey/](simple_health_survey/) | Cross-sectional | Basic health service satisfaction | 100 |
| [malaria_kap/](malaria_kap/) | KAP survey | Knowledge, Attitude, Practice | 150 |
| [antenatal_satisfaction/](antenatal_satisfaction/) | Cross-sectional | Maternal health service satisfaction | 200 |

## Using an Example

```bash
# Copy to studies/
cp -r examples/simple_health_survey studies/my_simple_study

# Rename and edit config.json to match your study
# Then run:
python main.py run --study my_simple_study
```
