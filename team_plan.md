# CineMood — Two-Member Project Plan

## Goal

Build a reproducible WEKA experiment that classifies movie reviews as positive or negative and compares Naive Bayes with SMO. Include movies beyond English cinema and reviews in at least two selected languages. Choose the review languages after checking dataset availability; English and one Indian language are a possible starting point, not a fixed requirement.

## Responsibilities

| Work area | Member 1: Data and preprocessing | Member 2: Models and evaluation |
| --- | --- | --- |
| Dataset selection | Find labelled datasets; record sources, usage terms, review languages, and available movie metadata | Check label consistency, class counts, and suitability for evaluation |
| Data preparation | Remove empty and duplicate reviews; standardize labels; export UTF-8 ARFF files | Verify imports, class selection, and exclusion of metadata from model features |
| Text processing | Test tokenization on each script; prepare optional language-specific stop-word lists | Configure StringToWordVector inside FilteredClassifier and record all settings |
| Experiments | Review sample predictions and preprocessing errors | Train and evaluate Naive Bayes and SMO separately for each review language |
| Analysis | Explain dataset limitations and language-specific error examples | Produce metric tables, confusion matrices, and classifier comparisons |
| Submission | Write dataset and preprocessing sections | Write methodology, results, and reproduction instructions |
| Shared work | Review each other's work; integrate the report; prepare slides and practise the demonstration | Review each other's work; integrate the report; prepare slides and practise the demonstration |

## Four-Week Schedule

| Period | Member 1 | Member 2 | Completion checkpoint |
| --- | --- | --- | --- |
| Week 1 | Shortlist datasets for at least two review languages; inspect labels, scripts, and movie coverage | Set up WEKA and Java; test a small sample import and both classifiers | Agree on languages, sources, dataset sizes, label mapping, and evaluation protocol |
| Week 2 | Clean data; document duplicates and class counts; export one dataset per language | Build and save both FilteredClassifier configurations; verify text features and class handling | Every selected language imports correctly and runs through both pipelines |
| Week 3 | Inspect misclassified reviews and language-specific preprocessing issues | Run final 10-fold cross-validation; export results and confusion matrices | Complete at least four runs: two classifiers multiplied by two languages |
| Week 4 | Complete data documentation, limitations, and example reviews | Complete results tables and reproducibility steps | Jointly verify the saved workflow, finish the report and slides, and rehearse the demonstration |

## Shared Experiment Rules

- Use the same cleaned dataset, fold count, random seed, and preprocessing settings for both classifiers within each review language. Record the seed and all options.
- Fit StringToWordVector inside FilteredClassifier so each cross-validation training fold learns its own vocabulary.
- Exclude review-language tags, movie identifiers, ratings used to derive labels, and other metadata from classifier inputs.
- Remove duplicate reviews before evaluation. If translated or near-duplicate versions of the same review exist across sources, keep them from appearing on both sides of an evaluation split.
- Check that each class has enough examples for 10-fold evaluation. Record any reduced fold count required for a small dataset and use it consistently for both classifiers.
- Report accuracy, per-class precision, recall, F1-score, and confusion matrices for every run, along with class counts and dataset size.
- Compare classifiers within each language. Treat cross-language differences cautiously because datasets may differ in size, topic, and difficulty.
- Do not select settings using final evaluation scores repeatedly. If tuning is needed, use a separate development split or nested evaluation and document the protocol.

## Deliverables

| Deliverable | Owner |
| --- | --- |
| Dataset source register, label mapping, coverage, and cleaning notes | Member 1 |
| Clean UTF-8 ARFF datasets, or acquisition instructions if redistribution is restricted | Member 1 |
| Tokenization checks and preprocessing settings for each language | Member 1, reviewed by Member 2 |
| Saved WEKA experiment configurations, software versions, and reproduction steps | Member 2 |
| Results table and confusion matrices for each language/classifier pair | Member 2 |
| Error analysis, final report, presentation, and demonstration | Both |

## Completion Criteria

The project is complete when both members can reproduce the documented experiments, every selected review language has results for both classifiers, coverage beyond English cinema is documented, and the report explains which classifier performs better on each dataset without claiming support for untested languages.
