---
name: data_science
description: >
  Apply opinionated data science defaults for modeling, EDA, and feature engineering.
  Use when building ML models, doing exploratory data analysis, feature engineering,
  or evaluating model performance. Do NOT use for general software engineering or
  non-ML Python work.
---

## Defaults

- **Python preferred** (R only if explicitly requested)
- **Libraries**: Pandas, Polars, NumPy, SciPy, Scikit-Learn, XGBoost, Seaborn, Matplotlib
- **Environment**: uv for deps, ruff/pyright/pytest

## Modeling

- **Default model**: XGBoost with `tree_method="hist"`, low learning rate, early stopping
- **Validation**: Nested — 20% holdout + 10-fold CV on training set
- **Feature importance**: Use `pred_contribs=True` in XGBoost (NOT shap package)

### Prohibitions
- No `shap` package — use XGBoost's built-in `pred_contribs=True`
- No SVMs (don't scale)
- No neural nets unless explicitly requested
- No TensorFlow (use PyTorch if needed)
- No Plotly (use Seaborn/Matplotlib)
- No SMOTE or upsampling (use scale_pos_weight or sample_weight)

## EDA Checklist

**Numeric columns**: count, missing %, min/max, mean/median, quantiles (5/25/50/75/95), std
**Categorical columns**: cardinality, top 5/bottom 5 values, missing %
**Text columns**: cardinality, length distribution (min/median/max chars)
**Target**: distribution, class balance (if classification)

## Feature Engineering

- **Categoricals**: `OrdinalEncoder` (not one-hot for tree models)
- **Text**: sentence-transformers embeddings preferred, TF-IDF as fallback
- **Dates**: extract year, month, day_of_week, is_weekend, days_since_reference
- **Missing**: let XGBoost handle natively (don't impute for tree models)

## Metrics

**Regression**: RMSE + R-squared + FVE (fraction of variance explained)
**Classification**: log loss + confusion matrix + FVE-binomial
**Unsupervised**: Calinski-Harabasz or Davies-Bouldin for cluster quality

## Unsupervised

- PCA / TruncatedSVD for dimensionality reduction
- K-Means++ for clustering
- Always report explained variance ratio for PCA

## Artifacts

Save all outputs to `report_artifacts/`:
- Model files, feature importance plots, validation curves, confusion matrices
- Produce Quarto or Pweave reports when applicable
