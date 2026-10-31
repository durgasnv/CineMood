# CineMood — Movie Review Sentiment Analysis Using WEKA

## Problem Statement

Movie reviews contain opinions that help viewers understand whether a movie is liked or disliked. Reading and classifying many reviews manually takes time and may produce inconsistent results. An automated approach can help identify the overall sentiment expressed in these reviews.

CineMood is a college project that uses the WEKA tool to classify movie reviews as **positive** or **negative**. Movies may come from any language or region, including Hindi, Telugu, Tamil, Malayalam, Kannada, and English cinema. The language of a movie and the language of its reviews are separate: for example, a Telugu movie may have reviews written in Telugu or English. The project will use labelled reviews in at least two selected review languages, subject to dataset availability, convert text into numerical features, and compare machine learning classifiers.

## Objectives

- Prepare labelled datasets of positive and negative reviews covering movies beyond English cinema and at least two selected review languages.
- Convert text into numerical features using WEKA's StringToWordVector filter.
- Train and compare Naive Bayes and SMO classifiers.
- Evaluate performance using accuracy, precision, recall, F1-score, and a confusion matrix.
- Identify the better-performing classifier for each selected review language and document differences in performance.

## Proposed Approach

1. Select at least two review languages based on the availability of suitably labelled datasets. Include reviews of movies beyond English cinema and document movie-language coverage where metadata is available.
2. Remove empty reviews and duplicate records, record review language, and prepare UTF-8 datasets in a WEKA-compatible format. Keep language metadata for reporting rather than using it as a text feature.
3. Use StringToWordVector for word-based feature extraction. Apply lowercasing where relevant, test tokenization on each selected script, and use a documented language-specific stop-word list where available. Preserve sentiment-bearing negation words.
4. Train separate Naive Bayes and SMO models for each review language using the same evaluation setup within that language. Direct classification will use the original review text without mandatory translation.
5. Use 10-fold cross-validation, fitting the text-processing filter within each training fold through FilteredClassifier to prevent data leakage.
6. Compare results within each language, report dataset sizes and class balance, and document observations. Differences across languages may reflect dataset differences as well as language effects.

## Input and Output

**Input:** Movie review text in the selected review languages, with positive or negative labels for training and evaluation. Movies are not restricted to English cinema.

**Output:** Predicted sentiment labels and a comparison of classifier performance.

## Scope

The project focuses on binary sentiment classification in WEKA Explorer for movies from any language or region. Initial implementation will cover at least two review languages, selected after checking dataset availability and text-processing compatibility. This does not imply support for every language. Neutral reviews, mixed-language reviews within a single record, automatic translation, live review collection, and a separate web or mobile application are outside the initial scope.

## Tools and Requirements

- WEKA with a compatible Java runtime.
- Labelled movie review datasets for the selected review languages.
- UTF-8 CSV or ARFF files for storing the datasets.
- Documented tokenization and optional stop-word lists appropriate to the selected languages.

## Expected Outcome

A reproducible WEKA experiment that classifies movie reviews as positive or negative and compares two classifiers using standard evaluation metrics. Actual performance will be reported after testing; no accuracy target is assumed in advance.

## Limitations

Sarcasm, mixed opinions, and context-dependent expressions may be misclassified. Results depend on dataset quality, class balance, and the vocabulary represented in the training data. Tokenization quality varies across scripts, and a model trained for one review language is not assumed to work on another. Movie-language coverage can only be verified when source metadata supports it.
