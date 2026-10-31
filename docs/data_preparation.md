# Data preparation and Member 2 handoff

## Reproduce the prepared data

Python 3.10 or later is sufficient; no Python packages are required. Run from the project root:

```bash
python3 scripts/prepare_data.py --download
python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

The first command downloads missing archives, verifies their hashes, and produces cleaned files. On this workspace the archives and exports already exist, so `python3 scripts/prepare_data.py` reruns preparation offline. A mirror can become unavailable; manually downloaded archives must have the names and hashes in [source_lock.json](../data/source_lock.json). Never silently substitute a different dataset version.

The complete checked-in source lock is required, including URLs, sizes, and SHA-256 hashes. Missing or incomplete locks stop preparation rather than accepting new sources automatically. Downloaded bytes are verified before being cached. All languages must pass the class-support check before exports are replaced; serialization is staged and each completed output file is replaced atomically.

| Local output | Purpose |
| --- | --- |
| `data/processed/en_reviews.arff` | English WEKA input |
| `data/processed/hi_reviews.arff` | Hindi WEKA input |
| `data/processed/en_reviews.csv`, `hi_reviews.csv` | Equivalent two-column text exports |
| `data/processed/en_metadata.csv`, `hi_metadata.csv` | Row-to-source traceability; excluded from classifier input |
| `reports/data_summary.json` | Tracked counts, cleaning totals, class support, lengths, and output hashes |
| `reports/local_audit.json` | Local source IDs and reasons for every dropped record, plus near-duplicate pairs |

ARFF attributes are exactly `review` (string) and `sentiment` (nominal `{negative,positive}`), with the class last. Files are UTF-8. Use ARFF in WEKA: CSV import can infer an unsuitable type for review strings. Both source and derived review text are intentionally ignored by Git; do not add them with `git add -f` as part of the handoff.

## Cleaning rules

1. Read the source files strictly, with the documented label mapping. Unknown labels or malformed CSV records stop preparation.
2. Apply Unicode NFC normalization and collapse whitespace. Preserve Hindi combining marks and joiners; do not use an ASCII-only word expression or strip non-English characters.
3. Exclude neutral records rather than assigning them a positive or negative label. Drop text with no word tokens.
4. Tokenize by replacing punctuation and symbols with spaces, keeping letters, combining marks, numbers, and internal apostrophes. Normalize curly apostrophes to straight apostrophes. Preserve negation such as `not`, `don't`, `नहीं`, and `मत`. No translation, stemming, or stop-word removal is used in this baseline.
5. Group exact matches on the case-folded, tokenized text so punctuation-only variations cannot become duplicate model inputs. Retain all group members' labels while checking near-duplicate links, including contradictory labels.
6. For records with at least 20 tokens, find pairs with Jaccard similarity ≥0.90 over sets of consecutive five-token shingles. Use connected components of exact and near-duplicate groups: keep the earliest record for a same-label component, and exclude the entire component if any labels conflict. An exact conflict also excludes its near-duplicate neighbors. This conservative rule removes very similar copies, not every paraphrase or copied fragment. Local audit IDs preserve the decisions.
7. Export deterministic CSV/ARFF and a separate metadata file. Assert that each final class has at least ten records before recommending ten folds.

Selection is deterministic: English paths are sorted; Hindi source priority is train, valid, then test. Duplicate handling is corpus hygiene and does not select predictive vocabulary. No sampling or class balancing is applied. All word dictionaries, feature selection, and IDF statistics must still be learned inside training folds.

## Text-processing settings for WEKA

Use the same initial settings for both classifiers and both languages. These are proposed baseline settings for Member 2 to configure and save, not fitted models.

| Setting | Value |
| --- | --- |
| Outer classifier | `weka.classifiers.meta.FilteredClassifier` |
| Filter | `weka.filters.unsupervised.attribute.StringToWordVector` |
| Text attribute | First attribute only (`attributeIndices=1`) |
| Tokenizer | `weka.core.tokenizers.WordTokenizer`, delimiters set to whitespace only: space, carriage return, newline, tab |
| Lowercase tokens | `true` |
| Stop-word handler | `weka.core.stopwords.Null` for both languages |
| Stemmer | `weka.core.stemmers.NullStemmer` |
| Word counts | `outputWordCounts=true` |
| TF / IDF transforms | Both `false` for the initial count baseline |
| Vocabulary limit | `wordsToKeep=1000`, `doNotOperateOnPerClassBasis=true` |
| Minimum term frequency | `minTermFreq=1` |
| Document-length normalization | None (`normalizeDocLength=0`) |

Whitespace tokenization is essential because the Python preparation step already sets token boundaries and retains English contractions. WEKA's default punctuation delimiters include apostrophes. In Explorer, edit the tokenizer delimiters to whitespace only; do not accept that default inadvertently. Consult the [WEKA tokenizer](https://weka.sourceforge.io/doc.dev/weka/core/tokenizers/WordTokenizer.html) and [StringToWordVector reference](https://weka.sourceforge.io/doc.dev/weka/filters/unsupervised/attribute/StringToWordVector.html) for property names and behavior.

No language-specific stop-word list is needed for the selected baseline. This avoids accidentally removing sentiment-bearing negation. An optional later stop-word experiment needs separately documented lists and development-only tuning; an English list must not be applied blindly to Hindi.

## Verify with WEKA

The exports were parsed using WEKA 3.8.6 and OpenJDK 21. To repeat with a local WEKA 3.8.6 JAR and Java 11 or later:

```bash
java -Dfile.encoding=UTF-8 -cp /path/to/weka.jar scripts/ValidateData.java
```

The validator checks the relation and attribute names, string review type, ordered nominal class values, at least ten records per class, missing values, and unchanged token boundaries under the specified WEKA tokenizer. It also checks Hindi combining marks and English/Hindi negation. Empty files and incorrect class schemas fail validation. This is input validation, not an evaluation of classifier accuracy. [Validation evidence](../reports/data_validation.txt).

To include real-WEKA success and failure cases in the automated regression suite:

```bash
WEKA_JAR=/path/to/weka.jar python3 -m unittest discover -s scripts -p 'test_*.py' -v
```

Without `WEKA_JAR`, the two Java-dependent regression tests are explicitly skipped; the standard-library preparation tests still run.

## Evaluation handoff

- Load one language's ARFF at a time. Select `sentiment` as the class.
- Put StringToWordVector **inside** FilteredClassifier. Do not apply a fitted text vector filter to the whole dataset in Explorer's Preprocess tab before cross-validation.
- Use ten-fold cross-validation with seed 42, identical data and filter settings for Naive Bayes and SMO. Save the final actual settings and WEKA version with results.
- Hindi source train/valid/test files have been pooled for this project's fresh cross-validation protocol. The sidecar retains original split labels. This is not the original paper's split or a held-out benchmark score; do not use this pooled file to claim either.
- If tuning parameters, use a separate development protocol or nested evaluation, not repeated selection on the final cross-validation score.
- Return per-record predictions with source-row alignment to Member 1 for error analysis. Include actual and predicted labels, fold, class probabilities if available, and the exact dataset hash.

## Limitations to include in the report

Hindi and English corpora differ in origin, review length, class balance, and annotation history. A cross-language accuracy difference cannot isolate language difficulty. Hindi includes short excerpts alongside full reviews; short text can lack context. Some named entities and credits remain inside review text, even though metadata columns are excluded. Source labels can be noisy, and residual ratings may remain in the English text. The current pipeline does not guarantee removal of every rating expression or source-specific shortcut.

Near-duplicate matching does not detect all paraphrases, translations, short overlaps, or reviews of the same movie. Movie IDs and original article grouping are unavailable, so movie-disjoint or article-disjoint evaluation cannot be guaranteed. Review language is inherited from source identity, not independently certified by native speakers; borrowed terms and code-mixed records may remain. Human language review and prediction-error analysis should accompany the final model evaluation.

Punctuation/symbol removal also discards emoji and emphasis signals. Future review predictions must pass through the same `normalize` and `tokenize` functions used for preparation before entering the saved WEKA pipeline; otherwise preprocessing differs between training and prediction.
