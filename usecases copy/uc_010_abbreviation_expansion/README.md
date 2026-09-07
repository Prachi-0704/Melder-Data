# Use Case 010: Abbreviation Expansion

## Scenario
Common company abbreviations should map to their expanded legal names while preserving the same identifiers.

This dataset contains 20 records on each side, modeled as a realistic enterprise matching problem with variations in punctuation, business suffixes, abbreviations, transliterations, and formatting.

## Sample files
- `company_a.csv` — source A dataset
- `company_b.csv` — source B dataset
- `config.yaml` — example Melder config for this case

# Abbreviation Coverage

| Full Form                | Abbreviation | Example                          |
| ------------------------ | ------------ | -------------------------------- |
| Mount                    | Mt           | `Mount View → Mt View`           |
| International            | Intl         | `International → Intl`           |
| Manufacturing            | Mfg          | `Manufacturing → Mfg`            |
| Corporation              | Corp         | `Corporation → Corp`             |
| Services                 | Svcs         | `Services → Svcs`                |
| Management               | Mgmt         | `Management → Mgmt`              |
| Department               | Dept         | `Department → Dept`              |
| Technologies             | Tech         | `Technologies → Tech`            |
| Company                  | Co           | `Company → Co`                   |
| Center                   | Ctr          | `Center → Ctr`                   |
| Industries               | Inds         | `Industries → Inds`              |
| Information              | Info         | `Information → Info`             |
| Research and Development | R&D          | `Research and Development → R&D` |
| Road                     | Rd           | Address abbreviation             |
| Street                   | St           | Address abbreviation             |
| Avenue                   | Ave          | Address abbreviation             |
| Boulevard                | Blvd         | Address abbreviation             |
| Drive                    | Dr           | Address abbreviation             |


## Run
Use the shared runner from the repository root:

```bash
./usecases/run_usecase.sh uc_010_abbreviation_expansion
```

Or run all use cases together:

```bash
./usecases/run_usecase.sh all
```


## Enroll mode (single-pool deduplication)
This use case also includes a single-pool enroll dataset for one-database entity resolution. The enroll file is named `company_enroll.csv` so it stays separate from the batch A/B files and keeps a different output path for dedicated deduplication runs.

```bash
./target/release/meld enroll --config usecases/uc_010_abbreviation_expansion/config_enroll.yaml --port 8090
```

Keep the enroll output separate from batch `run_###` folders by using a dedicated run directory such as `usecases/uc_010_abbreviation_expansion/runs/enroll_run_001/` before starting the server.
Run (from repo root):

```bash
cd melder && ./usecases/run_usecase.sh uc_010_abbreviation_expansion
```
