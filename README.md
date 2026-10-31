# CineMood

A college project using WEKA to classify movie reviews as positive or negative and compare Naive Bayes with SMO. Movies are not restricted to English cinema; the initial experiment will cover at least two selected review languages.

- [Problem statement and scope](problem_statement.md)
- [Two-member work plan and schedule](team_plan.md)

Member 1's data preparation is implemented for **English and Hindi review text**, including coverage beyond English cinema.

- [Dataset sources, terms, citations, and coverage](docs/dataset_sources.md)
- [Preparation instructions and Member 2 handoff](docs/data_preparation.md)
- [Member 1 report and remaining dependencies](reports/member1_report.md)
- [Generated dataset statistics](reports/data_summary.json)

To acquire the research datasets and regenerate local CSV/ARFF files:

```bash
python3 scripts/prepare_data.py --download
```

Python 3.10 or later is required; no Python packages are needed. Research review text stays local and is excluded from Git. See the source register for usage terms. Model training and performance evaluation remain Member 2's work.
