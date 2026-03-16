---
name: kaggle
description: >
  Kaggle CLI for downloading competition/dataset data and managing submissions.
  Use when the user says "kaggle", "download dataset", "submit to competition",
  "kaggle competition", or works with Kaggle data/competitions.
  Do NOT use for general data science tasks (use data-science skill) or
  non-Kaggle data sources.
allowed-tools: Bash(kaggle *)
---

## Setup

The Kaggle CLI is installed via `uv tool install kaggle` (included in `make install`). If missing:

```bash
uv tool install kaggle
```

**Authentication** — requires a Kaggle API token:

1. Go to kaggle.com → Account → "Create New Token"
2. This downloads `kaggle.json` — move it:

```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

Verify: `kaggle competitions list` should return results without error.

## Competition Data

```bash
kaggle competitions list                              # browse active competitions
kaggle competitions list -s "search term"             # search competitions
kaggle competitions files <competition>               # list available files
kaggle competitions download <competition> -p ./data  # download all files
kaggle competitions download <competition> -f <file>  # download single file
kaggle competitions leaderboard <competition>         # view leaderboard
```

The competition slug is the URL suffix (e.g. `titanic` from `kaggle.com/competitions/titanic`).

## Datasets

```bash
kaggle datasets list -s "search term"                        # search datasets
kaggle datasets files <owner>/<dataset>                      # list files
kaggle datasets download <owner>/<dataset> -p ./data --unzip # download + extract
```

Dataset slug format: `<owner>/<dataset-name>` (e.g. `zillow/zecon`).

## Submissions

```bash
kaggle competitions submit <competition> -f submission.csv -m "description"
kaggle competitions submissions <competition>  # list past submissions
```

## Config

```bash
kaggle config set competition <slug>  # set default competition (omit -c flag)
kaggle config view                    # show current config
```
