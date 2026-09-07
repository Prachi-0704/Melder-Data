# Melder Enroll Mode — Test Run Instructions

This document explains how to run the `enterprise_enroll_50.csv` test dataset through Melder's **Enroll Mode** using the Python test script.

## Prerequisites

Before starting:

* Run the commands from the **Melder repository root**.
* Make sure the Melder release binary has been built.
* Make sure the following files exist:

```text
test-data/
└── Enroll-test/
    ├── config-enroll.yaml
    ├── enterprise_enroll_50.csv
    └── run_enroll_test.py
```

The `config-enroll.yaml` should use the CSV's actual field names:

```text
entity_id
company_name
ssn_tax_id
address_line1
country_code
duns
```

For this test, the enrollment pool starts empty, so the `dataset:` section should be omitted from the Enroll configuration.

---

# 1. Terminal 1 — Start Melder

From the **repository root**, start Melder in Enroll Mode:

```powershell
.\target\release\meld.exe enroll --config test-data/Enroll-test/config-enroll.yaml --port 8090
```

Leave this terminal running.

Melder should start the Enroll Mode server on:

```text
http://localhost:8090
```

The Python script in Terminal 2 will communicate with this server.

---

# 2. Terminal 2 — Run the Python Script

Open a **second terminal**.

Make sure you are also in the **repository root**.

Run:

```powershell
python test-data/Enroll-test/run_enroll_test.py
```

The script will read:

```text
test-data/Enroll-test/enterprise_enroll_50.csv
```

and send the records to Melder.

---

# 3. Enrollment Flow

The complete flow is:

```text
enterprise_enroll_50.csv
        |
        v
Read 50 records
        |
        v
Validate entity_id
        |
        v
POST /api/v1/enroll-batch
        |
        v
N001 -> no previous records -> edges []
        |
        v
N002 -> compare with N001
        |
        v
N003 -> compare with N001, N002
        |
        v
...
        |
        v
N050 -> compare with N001 ... N049
        |
        v
POST /api/v1/admin/flush
        |
        v
Generate Melder output
        |
        v
output/
```

## Important: the enrollment pool grows during the batch

Enroll Mode maintains a **growing pool**.

The current record is scored against records that have already been enrolled. After scoring, the current record is added to the pool.

For example:

```text
Before N001:

Pool = []

N001 is enrolled.

Pool = [N001]
```

Then:

```text
N002 is scored against:

Pool = [N001]

N002 is enrolled.

Pool = [N001, N002]
```

Then:

```text
N003 is scored against:

Pool = [N001, N002]

N003 is enrolled.

Pool = [N001, N002, N003]
```

This continues until N050.

Therefore, a record is scored **before it is added to the pool**, meaning it cannot match itself.

---

# 4. Dataset Overview

The test dataset contains **50 records**.

It contains both:

1. Intended positive duplicate groups
2. Deliberately constructed hard negatives

This allows us to test both:

```text
True duplicate detection
```

and:

```text
False-positive resistance
```

---

# 5. Expected Positive Match Groups

The following records are intended to represent the same underlying entity.

| Entity Group                   | Records         |
| ------------------------------ | --------------- |
| Acme Technologies              | N001–N005       |
| Northstar Financial            | N006–N010       |
| Greenfield Manufacturing       | N011–N015       |
| Vertex Software Solutions      | N016–N020       |
| Pacific Logistics              | N021–N023       |
| Silverline Property Management | N026–N029       |
| Bluewater Energy               | N030–N032       |
| Metro Transportation           | N035–N037       |
| Evergreen Healthcare           | N040–N042       |
| Capital Investment Management  | N045–N047, N050 |

The records intentionally contain variations such as:

* `Inc` vs `Incorporated`
* `Corp` vs `Corporation`
* `Ltd` vs `Limited`
* `Mgmt` vs `Management`
* `Mfg` vs `Manufacturing`
* `Ave` vs `Avenue`
* `Dr` vs `Drive`
* `Pkwy` vs `Parkway`
* punctuation differences
* shortened company names

These variations are intended to exercise the configured company-name and address matching logic.

---

# 6. Hard Negative Groups

The dataset also contains records that are intentionally similar to positive entities but have different identifying values.

| Similar Entity                | Hard Negative Records | Main Difference                   |
| ----------------------------- | --------------------- | --------------------------------- |
| Pacific Logistics             | N024, N025            | Different `ssn_tax_id`            |
| Bluewater Energy              | N033, N034            | Different `ssn_tax_id` and `duns` |
| Metro Transportation          | N038, N039            | Different `ssn_tax_id` and `duns` |
| Evergreen Healthcare          | N043, N044            | Different `ssn_tax_id` and `duns` |
| Capital Investment Management | N048, N049            | Different `ssn_tax_id` and `duns` |

These records are important because they have very similar names and addresses.

The test should therefore verify whether the configured matching weights and thresholds can distinguish:

```text
same entity
```

from:

```text
similar-looking but different entity
```

---

# 7. Expected Behavior by Record Group

The exact similarity scores and returned edges depend on the Melder configuration, embedding model, blocking configuration, and thresholds.

Therefore, the expected results below describe the **intended behavior**, not guaranteed exact scores.

## N001 — First Record

Expected:

```text
N001 -> edges []
```

This is expected because N001 is the first record and there are no previously enrolled records.

---

## N002–N005 — Acme Technologies

Expected to find candidate edges to earlier Acme records.

Conceptually:

```text
N002 -> N001

N003 -> N001 / N002

N004 -> earlier Acme records

N005 -> earlier Acme records
```

The exact edges and scores depend on the configured `review_floor` and matching configuration.

---

## N006–N010 — Northstar Financial

Expected:

```text
N006 -> no earlier Northstar record

N007 -> N006

N008 -> N006 / N007

N009 -> earlier Northstar records

N010 -> earlier Northstar records
```

---

## N011–N015 — Greenfield Manufacturing

Expected positive group:

```text
N011–N015 -> Greenfield Manufacturing
```

Later records should be compared against previously enrolled Greenfield records.

---

## N016–N020 — Vertex Software Solutions

Expected positive group:

```text
N016–N020 -> Vertex Software Solutions
```

---

## N021–N025 — Pacific Logistics

This is an important section of the test.

Intended positives:

```text
N021
N022
N023
```

Hard negatives:

```text
N024
N025
```

N024 and N025 have similar company names and addresses but different `ssn_tax_id` values.

These records should be inspected carefully for false-positive matches.

---

## N026–N029 — Silverline Property Management

Expected positive group:

```text
N026–N029
```

---

## N030–N034 — Bluewater Energy

Intended positives:

```text
N030
N031
N032
```

Hard negatives:

```text
N033
N034
```

N033 and N034 use different identifying values and should be evaluated separately from the intended Bluewater duplicate group.

---

## N035–N039 — Metro Transportation

Intended positives:

```text
N035
N036
N037
```

Hard negatives:

```text
N038
N039
```

---

## N040–N044 — Evergreen Healthcare

Intended positives:

```text
N040
N041
N042
```

Hard negatives:

```text
N043
N044
```

---

## N045–N050 — Capital Investment Management

Intended positives:

```text
N045
N046
N047
N050
```

Hard negatives:

```text
N048
N049
```

N050 is particularly useful because it occurs **after** the hard-negative records.

It should be evaluated against the complete previously enrolled pool.

---

# 8. What the Python Script Should Report

The script should report that:

```text
50 records
```

were processed successfully.

For each record, inspect:

```text
enrolled
edge_count
matched_ids
match_scores
error
```

For example:

```text
N001 -> enrolled=true, edge_count=0

N002 -> enrolled=true, edge_count=1
        matched_ids=N001

N003 -> enrolled=true, edge_count=2
        matched_ids=N001;N002
```

The exact number of edges depends on the configured `review_floor` and `top_n`.

---

# 9. Understanding Edges

An important point is:

```text
edge exists
    !=
confirmed duplicate
```

An edge represents a **scored candidate relationship**.

For example:

```json
{
  "id": "N002",
  "enrolled": true,
  "edges": [
    {
      "id": "N001",
      "score": 0.91
    }
  ]
}
```

means that Melder found N001 as a candidate match for N002 with a score of `0.91`.

The caller is responsible for deciding whether that candidate represents a true entity match.

This distinction is especially important for the hard-negative records.

---

# 10. Output Files

The Python script should generate test artifacts under:

```text
test-data/Enroll-test/
```

For example:

```text
test-data/
└── Enroll-test/
    ├── config-enroll.yaml
    ├── enterprise_enroll_50.csv
    ├── run_enroll_test.py
    ├── enroll_response.json
    ├── flush_response.json
    └── output/
```

The `output/` directory contains the Melder-generated output according to the configured output settings.

---

# 11. Validation Checklist

After the test finishes, verify:

* [ ] Melder started successfully on port `8090`.
* [ ] Python connected successfully to Melder.
* [ ] Exactly 50 records were read.
* [ ] `entity_id` validation succeeded.
* [ ] N001 produced no edges.
* [ ] Later records were compared against previously enrolled records.
* [ ] Positive duplicate groups produced candidate edges where expected.
* [ ] Hard negatives are inspected for unexpected high-scoring edges.
* [ ] `/api/v1/admin/flush` completed successfully.
* [ ] Melder output files were generated.
* [ ] No records reported an error.

---

# 12. Troubleshooting

## Connection refused

If the Python script cannot connect to Melder, make sure Terminal 1 is still running:

```powershell
.\target\release\meld.exe enroll --config test-data/Enroll-test/config-enroll.yaml --port 8090
```

Then rerun the Python script.

---

## File not found

Make sure you are running the command from the **repository root**:

```powershell
python test-data/Enroll-test/run_enroll_test.py
```

Also verify that:

```text
test-data/Enroll-test/enterprise_enroll_50.csv
```

exists.

---

## Field/configuration errors

The CSV and Melder configuration must use matching field names.

The CSV contains:

```text
entity_id
company_name
ssn_tax_id
address_line1
country_code
duns
```

Do not use old field names such as:

```text
client_id
client_name
legal_trade_name
country
tax_id
```

unless those fields actually exist in the input CSV.

---

## Unexpected matches

If a hard negative receives an unexpectedly high score, inspect:

1. `match_scores`
2. field-level scores in `enroll_response.json`
3. `review_floor`
4. field weights
5. exact identifier fields
6. company-name embedding similarity
7. address similarity

Do not evaluate the result using only the overall score.

The field-level scores help explain **why** an edge was generated.

---

# 13. Stopping Melder

After the test is complete, Melder can be stopped from Terminal 1 with:

```text
Ctrl + C
```

For a graceful Enroll Mode shutdown through the API, use:

```text
POST /api/v1/admin/shutdown
```

The shutdown operation finalizes the enrollment output.

---

# 14. Complete Test Flow

The complete process can be summarized as:

```text
Terminal 1
    |
    +--> Start Melder Enroll Mode
    |
    +--> Keep server running
             |
             v
Terminal 2
    |
    +--> Read enterprise_enroll_50.csv
    |
    +--> Validate entity_id
    |
    +--> POST /api/v1/enroll-batch
    |
    +--> N001 -> no previous records
    |
    +--> N002 -> compare against N001
    |
    +--> N003 -> compare against N001, N002
    |
    +--> ...
    |
    +--> N050 -> compare against N001 ... N049
    |
    +--> POST /api/v1/admin/flush
    |
    +--> Verify output/
    |
    +--> Analyze positive matches and hard negatives
```

## Key takeaway

The purpose of this test is not simply to verify that all 50 records can be uploaded.

It is to verify that Melder:

1. Maintains a growing enrollment pool.
2. Scores each new record against previously enrolled records.
3. Finds intended duplicate relationships.
4. Handles variations in company names and addresses.
5. Uses identifying fields to help distinguish hard negatives.
6. Produces explainable scores and edges.
7. Successfully flushes the enrollment results to the configured output.
