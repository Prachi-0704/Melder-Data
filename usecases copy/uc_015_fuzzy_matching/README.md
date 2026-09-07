# Use Case 015: Fuzzy Matching

## Scenario
Names with transposition or missing characters should still match when identifiers align.

This dataset contains 20 records on each side, modeled as a realistic enterprise matching problem with variations in punctuation, business suffixes, abbreviations, transliterations, and formatting.

## Sample files
- `company_a.csv` — source A dataset
- `company_b.csv` — source B dataset
- `config.yaml` — example Melder config for this case

## Run
Use the shared runner from the repository root:

```bash
./usecases/run_usecase.sh uc_015_fuzzy_matching
```

Or run all use cases together:

```bash
./usecases/run_usecase.sh all
```


## Enroll mode (single-pool deduplication)
This use case also includes a single-pool enroll dataset for one-database entity resolution. The enroll file is named `company_enroll.csv` so it stays separate from the batch A/B files and keeps a different output path for dedicated deduplication runs.

```bash
./target/release/meld enroll --config usecases/uc_015_fuzzy_matching/config_enroll.yaml --port 8090
```

Keep the enroll output separate from batch `run_###` folders by using a dedicated run directory such as `usecases/uc_015_fuzzy_matching/runs/enroll_run_001/` before starting the server.
Run (from repo root):

```bash
cd melder && ./usecases/run_usecase.sh uc_015_fuzzy_matching
```
