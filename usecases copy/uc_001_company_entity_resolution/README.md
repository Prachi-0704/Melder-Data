# Entity resolution test scenario

## Use case
This dataset is designed to validate entity resolution for company records across multiple source systems. The goal is to match records that refer to the same legal entity while handling common data quality issues such as:

- case differences (`BANK OF AMERICA` vs `Bank of America`)
- punctuation and formatting differences (`Johnson and Johnson` vs `Johnson & Johnson`)
- token reordering (`America Bank Of` vs `Bank of America`)
- minor address formatting differences
- high-confidence exact identifier matches (`ssn_tax_id`, `duns`)

This is a realistic master-data or counterparty-matching scenario where two systems contain overlapping company records that should be linked to a single canonical entity.

## Model used
The configuration uses Melder's default embedding model:

- `all-MiniLM-L6-v2`

This is configured in the YAML under the `embeddings` section and runs on CPU by default for this lightweight test.

## Matching techniques used
The matching config combines several methods:

1. `exact` matching for stable identifiers and normalized fields
   - `ssn_tax_id`
   - `duns`
   - `country_code`
   - `address_line1`
   - `company_name` (case-insensitive exact comparison)
2. `fuzzy` matching with `token_sort_ratio`
   - used for company names where word order differs but the underlying entity is the same
3. `exact_prefilter`
   - high-confidence exact checks on tax ID and DUNS before blocking/scoring
4. `blocking`
   - restricts candidate pairs to records in the same country before full match scoring

## Example expected behavior
- `A1` and `B1` should match as the same company even though the name casing differs.
- `A1` and `B3` should match via token-order fuzzy similarity, even though the tokens are reordered.
- `A5` and `B8` should match because they are the same company with a punctuation variation in the name.
- `A6` and `B9` should match due to the same legal entity with minor naming variations.
- `A4` and `B7` should match as the same legal entity with `Ltd` added in one dataset.

## Run
Use the shared runner from the repo root:

```bash
./usecases/run_usecase.sh uc_001_company_entity_resolution
```

To run every use case in the folder:

```bash
./usecases/run_usecase.sh all
```


## Enroll mode (single-pool deduplication)
This use case also includes a single-pool enroll dataset for one-database entity resolution. The enroll file is named `company_enroll.csv` so it stays separate from the batch A/B files and keeps a different output path for dedicated deduplication runs.

```bash
./target/release/meld enroll --config usecases/uc_001_company_entity_resolution/config_enroll.yaml --port 8090
```

Keep the enroll output separate from batch `run_###` folders by using a dedicated run directory such as `usecases/uc_001_company_entity_resolution/runs/enroll_run_001/` before starting the server.
Run (from repo root):

```bash
cd melder && ./usecases/run_usecase.sh uc_001_company_entity_resolution
```
