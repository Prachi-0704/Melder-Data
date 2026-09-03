# Use Case 005: Stop Word Removal

## Scenario
Extra stop words should not prevent valid entity matching when the substantive name is the same.

This dataset contains 20 records on each side, modeled as a realistic enterprise matching problem with variations in punctuation, business suffixes, abbreviations, transliterations, and formatting.

## Sample files
- `company_a.csv` — source A dataset
- `company_b.csv` — source B dataset
- `config.yaml` — example Melder config for this case
| Dataset A | Dataset B | SSN/Tax ID | DUNS      | Address   | Scenario                |
| --------- | --------- | ---------- | --------- | --------- | ----------------------- |
| A001      | B001      | Same       | Same      | Same      | Strong identifier match |
| A002      | B002      | Different  | Same      | Same      | DUNS match              |
| A003      | B003      | Same       | Different | Variation | SSN match               |
| A004      | B004      | Different  | Same      | Variation | DUNS match              |
| A005      | B005      | Same       | Different | Same      | SSN match               |
| A006      | B006      | Different  | Same      | Variation | DUNS match              |
| A007      | B007      | Same       | Same      | Same      | Strong identifier match |
| A008      | B008      | Different  | Same      | Same      | DUNS match              |
| A009      | B009      | Same       | Different | Same      | SSN match               |
| A010      | B010      | Different  | Same      | Variation | DUNS match              |
| A011      | B011      | Same       | Same      | Same      | Strong identifier match |
| A012      | B012      | Different  | Same      | Variation | DUNS match              |
| A013      | B013      | Same       | Different | Variation | SSN match               |
| A014      | B014      | Different  | Same      | Same      | DUNS match              |
| A015      | B015      | Same       | Different | Same      | SSN match               |
| A016      | B016      | Different  | Same      | Same      | DUNS match              |
| A017      | B017      | Same       | Same      | Same      | Strong identifier match |
| A018      | B018      | Different  | Same      | Variation | DUNS match              |
| A019      | B019      | Same       | Same      | Same      | Strong identifier match |
| A020      | B020      | Different  | Same      | Variation | DUNS match              |


## Run
Use the shared runner from the repository root:

```bash
./usecases/run_usecase.sh uc_005_stop_word_removal
```

Or run all use cases together:

```bash
./usecases/run_usecase.sh all
```


## Enroll mode (single-pool deduplication)
This use case also includes a single-pool enroll dataset for one-database entity resolution. The enroll file is named `company_enroll.csv` so it stays separate from the batch A/B files and keeps a different output path for dedicated deduplication runs.

```bash
./target/release/meld enroll --config usecases/uc_005_stop_word_removal/config_enroll.yaml --port 8090
```

Keep the enroll output separate from batch `run_###` folders by using a dedicated run directory such as `usecases/uc_005_stop_word_removal/runs/enroll_run_001/` before starting the server.
Run (from repo root):

```bash
cd melder && ./usecases/run_usecase.sh uc_005_stop_word_removal
```
