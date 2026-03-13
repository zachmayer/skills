---
name: kaggle-cli
description: >
  Kaggle CLI for competitions, datasets, submissions, and notebooks. Use when
  the user says "download Kaggle data", "submit to Kaggle", "list competitions",
  "Kaggle dataset", "check leaderboard", or any Kaggle task. Covers competition
  data, submissions, datasets, and kernels/notebooks. Do NOT use for general
  data science tasks that don't involve Kaggle (use data-science skill instead).
allowed-tools: Bash(kaggle *)
---

Kaggle CLI reference. Docs: https://github.com/Kaggle/kaggle-api

## Install

```bash
pip install kaggle
```

Global install — the `kaggle` binary must be on `$PATH`.

## Auth

1. Go to https://www.kaggle.com/settings → **Create New Token**
2. Save the downloaded `kaggle.json` to `~/.kaggle/kaggle.json`
3. Restrict permissions:

```bash
chmod 600 ~/.kaggle/kaggle.json
```

The file contains `{"username": "...", "key": "..."}`. Alternatively, set `KAGGLE_USERNAME` and `KAGGLE_KEY` env vars.

## Competitions

### Browse and search

```bash
kaggle competitions list                          # active competitions
kaggle competitions list -s "titanic"             # search by keyword
kaggle competitions list --sort-by latestDeadline # sort options: grouped, prize, earliestDeadline, latestDeadline, numberOfTeams, recentlyCreated
kaggle competitions list --category featured      # categories: all, featured, research, recruitment, gettingStarted, masters, playground
```

### Download data

```bash
kaggle competitions download -c <competition>                    # download all files
kaggle competitions download -c <competition> -f train.csv       # single file
kaggle competitions download -c <competition> -p ./data/         # to specific path
```

Files download as zip — unzip after downloading.

### Leaderboard

```bash
kaggle competitions leaderboard <competition> --show             # view leaderboard
kaggle competitions leaderboard <competition> --download         # download as CSV
```

### Submissions

```bash
kaggle competitions submit -c <competition> -f submission.csv -m "first attempt"
kaggle competitions submissions -c <competition>                 # list past submissions
```

**Always confirm with the user before submitting** — submissions may be limited.

## Datasets

### Search and download

```bash
kaggle datasets list -s "housing prices"                         # search
kaggle datasets list --sort-by hottest                           # sort: hottest, votes, updated, active, published
kaggle datasets download -d <owner>/<dataset-name>               # download
kaggle datasets download -d <owner>/<dataset-name> -p ./data/    # to specific path
kaggle datasets download -d <owner>/<dataset-name> --unzip       # auto-unzip
```

### Create and version

```bash
kaggle datasets init -p ./my-dataset/                            # create metadata file
kaggle datasets create -p ./my-dataset/                          # upload new dataset
kaggle datasets version -p ./my-dataset/ -m "added new column"   # new version
```

## Kernels (Notebooks)

```bash
kaggle kernels list -s "titanic"                                 # search
kaggle kernels list --mine                                       # your notebooks
kaggle kernels pull <owner>/<kernel-name> -p ./notebooks/        # download
kaggle kernels push -p ./my-kernel/                              # upload/run
kaggle kernels output <owner>/<kernel-name> -p ./output/         # download output
kaggle kernels status <owner>/<kernel-name>                      # check run status
```

## Key Flags

| Flag | Description |
|------|-------------|
| `-s, --search` | Search/filter by keyword |
| `-p, --path` | Download/upload directory |
| `-f, --file` | Specific file (download) or submission file |
| `-m, --message` | Version/submission message |
| `-c, --competition` | Competition name (from URL slug) |
| `-d, --dataset` | Dataset ref as `owner/dataset-name` |
| `--sort-by` | Sort results |
| `--csv` | Output as CSV instead of formatted table |
| `-v, --verbose` | Verbose output |
| `--unzip` | Auto-unzip after download |
| `--force` | Overwrite existing files |

## Tips

- Competition names are the URL slug: `kaggle.com/c/titanic` → `-c titanic`
- Dataset refs are `owner/dataset-name` from the URL
- Most downloads are zipped — use `--unzip` or unzip manually
- Use `--csv` to pipe output to other tools
- You must accept competition rules on kaggle.com before downloading data
