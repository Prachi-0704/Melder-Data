# Use Case 006: Business Stop Words

## Scenario
Company names with legal and business suffixes often vary but resolve to the same underlying legal entity.

This dataset contains 20 records on each side, modeled as a realistic enterprise matching problem with variations in punctuation, business suffixes, abbreviations, transliterations, and formatting.

## Sample files
- `company_a.csv` — source A dataset
- `company_b.csv` — source B dataset
- `config.yaml` — example Melder config for this case

| Pair        | SSN/Tax ID | DUNS      | Address   | Company Name Variation            |
| ----------- | ---------- | --------- | --------- | --------------------------------- |
| A001 ↔ B001 | Same       | Same      | Same      | Incorporated → Inc.               |
| A002 ↔ B002 | Different  | Same      | Variation | Limited → Ltd.                    |
| A003 ↔ B003 | Same       | Different | Variation | LLC → L.L.C.                      |
| A004 ↔ B004 | Different  | Same      | Variation | Corporation → Corp.               |
| A005 ↔ B005 | Same       | Different | Same      | Private Limited → Pvt. Ltd.       |
| A006 ↔ B006 | Different  | Same      | Variation | Company → Co.                     |
| A007 ↔ B007 | Same       | Same      | Variation | Incorporated → Inc.               |
| A008 ↔ B008 | Different  | Same      | Variation | GmbH formatting + transliteration |
| A009 ↔ B009 | Same       | Different | Variation | Sociedad Limitada → S.L.          |
| A010 ↔ B010 | Different  | Same      | Variation | Kabushiki Kaisha → KK             |
| A011 ↔ B011 | Same       | Same      | Variation | Corporation → Corp.               |
| A012 ↔ B012 | Different  | Same      | Variation | LLP → L.L.P.                      |
| A013 ↔ B013 | Same       | Different | Variation | Company Limited → Co. Ltd.        |
| A014 ↔ B014 | Different  | Same      | Variation | Société formatting + SA           |
| A015 ↔ B015 | Same       | Different | Variation | Incorporated → Inc.               |
| A016 ↔ B016 | Different  | Same      | Variation | Corporation → Corp.               |
| A017 ↔ B017 | Same       | Different | Variation | Private Limited → Pvt Ltd         |
| A018 ↔ B018 | Different  | Same      | Variation | Company → Co.                     |
| A019 ↔ B019 | Same       | Different | Variation | LLC → L.L.C.                      |
| A020 ↔ B020 | Different  | Same      | Variation | Incorporated → Inc.               |


## Run
Use the shared runner from the repository root:

```bash
./usecases/run_usecase.sh uc_006_business_stop_words
```

Or run all use cases together:

```bash
./usecases/run_usecase.sh all
```


## Enroll mode (single-pool deduplication)
This use case also includes a single-pool enroll dataset for one-database entity resolution. The enroll file is named `company_enroll.csv` so it stays separate from the batch A/B files and keeps a different output path for dedicated deduplication runs.

```bash
./target/release/meld enroll --config usecases/uc_006_business_stop_words/config_enroll.yaml --port 8090
```

Keep the enroll output separate from batch `run_###` folders by using a dedicated run directory such as `usecases/uc_006_business_stop_words/runs/enroll_run_001/` before starting the server.
Run (from repo root):

```bash
cd melder && ./usecases/run_usecase.sh uc_006_business_stop_words
```
