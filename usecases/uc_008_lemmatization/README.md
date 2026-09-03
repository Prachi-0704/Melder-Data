# Use Case 008: Lemmatization

## Scenario
Morphological variants of a company’s name should resolve to the same legal entity.

This dataset contains 20 records on each side, modeled as a realistic enterprise matching problem with variations in punctuation, business suffixes, abbreviations, transliterations, and formatting.

## Sample files
- `company_a.csv` — source A dataset
- `company_b.csv` — source B dataset
- `config.yaml` — example Melder config for this case

| Identifier Pattern                 | Records                                                    |
| ---------------------------------- | ---------------------------------------------------------- |
| **Same SSN + Same DUNS**           | A001, A007, A011, A015, A017, A019                         |
| **Same SSN + Different DUNS**      | A003, A005, A009, A013                                     |
| **Different SSN + Same DUNS**      | A002, A004, A006, A008, A010, A012, A014, A016, A018, A020 |
| **Different SSN + Different DUNS** | None                                                       |
| **Total**                          | A001–A020                                                  |


## Run
Use the shared runner from the repository root:

```bash
./usecases/run_usecase.sh uc_008_lemmatization
```

Or run all use cases together:

```bash
./usecases/run_usecase.sh all
```


## Enroll mode (single-pool deduplication)
This use case also includes a single-pool enroll dataset for one-database entity resolution. The enroll file is named `company_enroll.csv` so it stays separate from the batch A/B files and keeps a different output path for dedicated deduplication runs.

```bash
./target/release/meld enroll --config usecases/uc_008_lemmatization/config_enroll.yaml --port 8090
```

Keep the enroll output separate from batch `run_###` folders by using a dedicated run directory such as `usecases/uc_008_lemmatization/runs/enroll_run_001/` before starting the server.
Run (from repo root):

```bash
cd melder && ./usecases/run_usecase.sh uc_008_lemmatization
```
