# 🎬 CineMood
### Multilingual Movie Review Sentiment Analysis Using WEKA

CineMood is a machine learning project that classifies movie reviews as **positive** or **negative** using Natural Language Processing (NLP) and WEKA.

The project evaluates two classification algorithms, **Naive Bayes** and **Sequential Minimal Optimization (SMO)**, on English and Hindi movie reviews to compare their sentiment classification performance.

## Project Objectives

- Perform sentiment analysis on English and Hindi movie reviews.
- Prepare and preprocess multilingual text datasets.
- Train and evaluate Naive Bayes and SMO classifiers using WEKA.
- Compare accuracy, precision, recall, F1-score, and confusion matrices.
- Document the experimental methodology and results for reproducibility.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.10+ | Dataset preparation and validation |
| Java 17 | Running WEKA |
| WEKA 3.8.7 | Machine learning classification |
| StringToWordVector | Text-to-feature conversion |
| Naive Bayes | Probabilistic classification |
| SMO | Support Vector Machine classification |
| Git and GitHub | Version control and collaboration |

## Dataset Information

| Language | Reviews | Negative | Positive |
|---|---:|---:|---:|
| English | 1,993 | 996 | 997 |
| Hindi | 2,227 | 946 | 1,281 |
| **Total** | **4,220** | **1,942** | **2,278** |

The datasets use WEKA's ARFF format with two attributes:

- `review` — the movie review text.
- `sentiment` — the classification label (`negative` or `positive`).

Research review text remains local and is excluded from Git. Refer to the dataset source documentation for citations and usage terms.

## Methodology

1. Acquire and preprocess English and Hindi movie reviews.
2. Convert the cleaned datasets into WEKA-compatible ARFF files.
3. Convert review text into numerical features using `StringToWordVector`.
4. Train Naive Bayes and SMO classifiers using `FilteredClassifier`.
5. Evaluate each classifier using stratified 10-fold cross-validation with random seed 42.
6. Compare model performance using accuracy, precision, recall, F1-score, and confusion matrices.
7. Save trained models and experimental results.

The text-vectorization filter is applied within `FilteredClassifier` during cross-validation to avoid fitting the vocabulary on the full dataset before evaluation.

## Experimental Results

| Language | Classifier | Accuracy | Weighted Precision | Weighted Recall | Weighted F1 |
|---|---|---:|---:|---:|---:|
| English | Naive Bayes | **80.43%** | 0.805 | 0.804 | **0.804** |
| English | SMO | 78.17% | 0.782 | 0.782 | 0.782 |
| Hindi | Naive Bayes | 63.36% | 0.632 | 0.634 | 0.605 |
| Hindi | SMO | **69.96%** | 0.698 | 0.700 | **0.699** |

### Key Findings

- **Naive Bayes performed best on English reviews**, achieving 80.43% accuracy.
- **SMO performed best on Hindi reviews**, achieving 69.96% accuracy.
- Naive Bayes outperformed SMO on English by approximately 2.26 percentage points.
- SMO outperformed Naive Bayes on Hindi by approximately 6.60 percentage points.
- Hindi Naive Bayes showed weaker recall for negative reviews than Hindi SMO.

These results describe performance on the respective datasets under the tested configurations. They do not establish that one language is inherently more difficult to classify.

## Project Structure

```text
CineMood/
├── configs/          # WEKA experiment commands
├── data/             # Dataset preparation outputs and metadata
├── docs/             # Dataset documentation
├── models/           # Saved WEKA classifiers
├── report/           # Member 2 PDF report
├── reports/          # Member 1 documentation and statistics
├── results/          # WEKA evaluation outputs
├── scripts/          # Dataset preparation and validation
├── README.md
├── problem_statement.md
└── team_plan.md
```

## How to Run

### 1. Prepare the datasets

Python 3.10 or later is required. The preparation script does not require third-party Python packages.

```bash
python3 scripts/prepare_data.py --download
```

### 2. Configure WEKA

Install Java 17 and WEKA 3.8.7. Set `WEKA_JAR` to the location of your WEKA JAR file.

Example for macOS:

```bash
export WEKA_JAR="/Applications/weka-3.8.7.app/Contents/app/weka.jar"
```

### 3. Reproduce the experiments

Refer to [Experiment Commands](configs/experiment_commands.txt) for the Naive Bayes and SMO evaluation commands.

### 4. Review the results

The evaluation outputs are available in the [`results/`](results/) folder, and the saved models are available in [`models/`](models/).

## Project Documentation

- [Problem Statement and Scope](problem_statement.md)
- [Two-Member Work Plan](team_plan.md)
- [Dataset Sources and Citations](docs/dataset_sources.md)
- [Data Preparation Instructions](docs/data_preparation.md)
- [Member 1 Report](reports/member1_report.md)
- [Dataset Statistics](reports/data_summary.json)
- [Member 2 Models and Evaluation Report](report/CineMood_Member2_Models_and_Evaluation_Report.pdf)

## Team Contributions

**Member 1 — Dataset Preparation and Documentation**

Responsible for dataset sourcing, preprocessing, dataset generation, validation, and data preparation documentation.

**Member 2 — Models and Evaluation**

Responsible for WEKA classifier training, stratified 10-fold cross-validation, evaluation metrics, confusion matrices, model comparison, saving trained classifiers, and evaluation reporting.

## Conclusion

CineMood demonstrates a reproducible workflow for multilingual movie-review sentiment classification using WEKA. The experiments show that Naive Bayes and SMO perform differently across the two datasets, highlighting the importance of evaluating multiple algorithms rather than assuming one classifier will perform best in every setting.