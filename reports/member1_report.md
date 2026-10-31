# Member 1 — Data and preprocessing report

## Delivered

Selected Hindi and English review sources, acquired the archives, recorded source hashes and terms, and created a repeatable preparation script. Local outputs include UTF-8 ARFF files, CSV equivalents, source metadata sidecars, and an audit of dropped records. Raw and derived review text is excluded from Git; acquisition instructions are included for the other team member.

| Review language | Raw | Positive retained | Negative retained | Retained total | Removed |
| --- | ---: | ---: | ---: | ---: | ---: |
| English | 2,000 | 997 | 996 | 1,993 | 2 exact duplicates; 5 near-duplicates |
| Hindi | 3,100 | 1,281 | 946 | 2,227 | 867 neutral; 6 exact duplicates |

Both retained classes in each language support ten-fold cross-validation. Counts and output hashes are generated in [data_summary.json](data_summary.json). The Hindi mirror is a variant attributed to IIT Patna and differs from the dataset size and labels in the original publication; this distinction must remain in the final report.

## Submission-ready dataset description

CineMood uses two separately prepared review-language datasets. English review documents come from Cornell's sentiment polarity dataset v2.0. Hindi text comes from the Kaggle IIT Patna Movie Reviews Hindi mirror, which contains short passages and longer reviews. The project uses the source-provided positive and negative labels and excludes neutral Hindi records. Hindi reviews mention Indian films, providing evidence that the project is not limited to English cinema. Complete movie-language metadata is unavailable, so no exhaustive industry-level coverage claim is made. Sources, citations, usage terms, and version caveats appear in the [source register](../docs/dataset_sources.md).

## Submission-ready preprocessing description

Text is normalized to Unicode NFC, whitespace is collapsed, and deterministic token boundaries are prepared while preserving Hindi combining marks and English/Hindi negation. Empty text, exact duplicates, and highly similar five-token-shingle duplicates are removed using documented rules; contradictory duplicate groups are excluded. Each language is exported separately with review text and nominal sentiment as the only WEKA attributes. The proposed baseline uses a whitespace tokenizer without stop-word removal or stemming. StringToWordVector must learn its vocabulary within each training fold through FilteredClassifier. Detailed settings and reproduction commands appear in the [handoff](../docs/data_preparation.md).

## Preprocessing review and future error analysis

Automated checks cover Devanagari marks, curly apostrophes, English contractions, Hindi negation, duplicate-label conflicts, and near-duplicate candidate coverage against a brute-force reference. Synthetic tokenization examples are checks only and never enter the dataset. WEKA validates both complete ARFF files and their token boundaries.

Manual source inspection found very short Hindi excerpts and longer records with film-credit text. These need contextual interpretation in the final error analysis. Neither source supplies uniform movie identifiers, and Hindi source provenance does not fully explain its differences from the paper. These limitations are documented rather than hidden by reporting only aggregate counts.

Prediction-error analysis is pending Member 2's evaluated predictions. No misclassification examples, model rankings, or performance metrics are fabricated. When predictions arrive, Member 1 should inspect false positives and false negatives in each language for negation, sarcasm, mixed opinions, missing context, names/credits, tokenization problems, and potential label errors. Keep original labels unless a separately documented adjudication process approves corrections.

## Status

- Complete: source selection, acquisition, terms and citations, label mapping, cleaning, local exports, preprocessing documentation, tokenization/import checks, dataset limitations, and draft data/preprocessing report sections.
- Pending Member 2: independent review of the handoff, saved classifier configurations, evaluated predictions, and metric tables.
- Pending joint work: prediction-error analysis after evaluation, integration of the final report, slides, and demonstration.
