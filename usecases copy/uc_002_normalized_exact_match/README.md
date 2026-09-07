# Use Case 2: Normalized Exact Match / Attribute-Based Entity Resolution

## Use case
This example models a realistic attribute-based company matching scenario where each dataset contains one record per legal entity, but the same entity can appear with slightly different formatting on each side.

The business rule is to match entities when the key attributes agree after normalization:

- company name
- SSN/tax ID
- address line 1
- country code
- DUNS number

This is the normal shape of a master-data or counterparty-reconciliation problem: one legal entity in system A and one legal entity in system B, with different casing, punctuation, and naming style but the same underlying identity.

## Real-world data pattern
In a real entity-resolution project, you usually want:

- one row per legal entity per source system
- unique values for the main identifiers
- no duplicates of the same legal entity within the same input dataset
- only true variants across A/B, not repeated copies of the same record

This is different from a duplicate-heavy test dataset. That type of data may trigger Melder's 1:1 crossmap rule and eliminate extra duplicates.

## Normalization note
Melder's `exact` matcher is case-insensitive, but it does not automatically strip punctuation from values like `123-45-6789` vs `123456789`.

For production use, normalize the source values before loading them into Melder.

Recommended normalization:

- uppercase the company name
- remove whitespace and punctuation from SSN/tax ID values
- standardize street casing and spacing
- trim leading/trailing whitespace
- preserve a canonical DUNS string

After normalization, the same entity can be matched reliably with exact comparison.

## Model used
The example uses Melder's default embedding model:

- `all-MiniLM-L6-v2`

This is configured under the `embeddings` section in the sample YAML.

## Matching techniques used
This use case combines the following methods:

1. `exact_prefilter`
   - validates `ssn_tax_id` and `duns` before scoring
2. `exact` scoring
   - case-insensitive exact comparison on normalized names and identifiers
3. `fuzzy` scoring with `token_sort_ratio`
   - handles name variations such as `JPMorgan Chase & Co.` vs `JPMorgan Chase`
4. `blocking`
   - restricts candidate pairs to the same country before evaluating candidates

## Example data variant set
The realistic sample contains variations such as:

- `Wells Fargo` vs `WELLS FARGO`
- `JPMorgan Chase & Co.` vs `JPMorgan Chase`
- `Bank of America Corporation` vs `Bank of America`
- `Target Corp` vs `Target Corporation`
- `Uber Technologies Inc` vs `Uber Technologies`

These reflect normal enterprise attribute-based entity resolution.

The records are intentionally shuffled across rows so the matching is clearly based on identity values and normalization, not on a simple A[i] → B[i] positional relationship.

## Run
Use the shared runner from the repo root so each execution gets a fresh isolated run folder automatically.

```bash
./usecases/run_usecase.sh uc_002_normalized_exact_match
```

To run all use cases under the `usecases` folder:

```bash
./usecases/run_usecase.sh all
```


## Enroll mode (single-pool deduplication)
This use case also includes a single-pool enroll dataset for one-database entity resolution. The enroll file is named `company_enroll.csv` so it stays separate from the batch A/B files and keeps a different output path for dedicated deduplication runs.

```bash
./target/release/meld enroll --config usecases/uc_002_normalized_exact_match/config_enroll.yaml --port 8090
```

Keep the enroll output separate from batch `run_###` folders by using a dedicated run directory such as `usecases/uc_002_normalized_exact_match/runs/enroll_run_001/` before starting the server.
Run (from repo root):

```bash
cd melder && ./usecases/run_usecase.sh uc_002_normalized_exact_match
```
