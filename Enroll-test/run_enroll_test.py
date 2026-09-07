import csv
import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "enterprise_enroll_50.csv"
OUTPUT_DIR = BASE_DIR / "output"

BASE_URL = "http://localhost:8090"
ENROLL_BATCH_ENDPOINT = f"{BASE_URL}/api/v1/enroll-batch"
FLUSH_ENDPOINT = f"{BASE_URL}/api/v1/admin/flush"
HEALTH_ENDPOINT = f"{BASE_URL}/api/v1/health"

# Expected columns in your exact CSV
EXPECTED_COLUMNS = [
    "entity_id",
    "company_name",
    "ssn_tax_id",
    "address_line1",
    "country_code",
    "duns",
]


# ============================================================
# Helper: HTTP POST
# ============================================================

def post_json(url, payload=None):
    """
    Send a JSON POST request and return:
        status_code, response_json
    """

    data = None

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=300) as response:
            status_code = response.status
            response_body = response.read().decode("utf-8")

            if not response_body:
                return status_code, {}

            try:
                return status_code, json.loads(response_body)
            except json.JSONDecodeError:
                return status_code, response_body

    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")

        print(f"\nHTTP ERROR {e.code}")
        print(error_body)

        raise

    except URLError as e:
        print("\nCould not connect to Melder.")
        print(f"URL: {url}")
        print(f"Error: {e.reason}")
        raise


# ============================================================
# Check Melder
# ============================================================

def check_melder():
    print("Checking Melder server...")

    try:
        request = Request(
            HEALTH_ENDPOINT,
            headers={"Accept": "application/json"},
            method="GET",
        )

        with urlopen(request, timeout=10) as response:
            print(f"✓ Melder is running ({response.status})")
            return True

    except Exception:
        print()
        print("ERROR: Melder is not reachable.")
        print()
        print("Start Melder first using:")
        print()
        print(
            "  .\\target\\release\\meld.exe "
            "enroll --config test-data/Enroll-test/config-enroll.yaml --port 8090"
        )
        print()

        return False


# ============================================================
# Read CSV
# ============================================================

def read_csv_records():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"Input CSV not found:\n{CSV_FILE}"
        )

    print(f"Reading CSV:")
    print(f"  {CSV_FILE}")

    with CSV_FILE.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        actual_columns = reader.fieldnames or []

        print()
        print("CSV columns:")
        for column in actual_columns:
            print(f"  - {column}")

        # ----------------------------------------------------
        # Validate columns
        # ----------------------------------------------------

        missing_columns = [
            column
            for column in EXPECTED_COLUMNS
            if column not in actual_columns
        ]

        if missing_columns:
            raise ValueError(
                "\nMissing required CSV columns:\n"
                + "\n".join(f"  - {c}" for c in missing_columns)
            )

        records = []

        for row_number, row in enumerate(reader, start=2):

            # Remove any accidental whitespace around values
            record = {
                key: value.strip() if isinstance(value, str) else value
                for key, value in row.items()
            }

            # Validate entity ID
            if not record["entity_id"]:
                raise ValueError(
                    f"Row {row_number}: entity_id is empty"
                )

            records.append(record)

    return records


# ============================================================
# Validate records
# ============================================================

def validate_records(records):
    print()
    print("Validating records...")

    if not records:
        raise ValueError("CSV contains no records.")

    entity_ids = set()

    for record in records:

        entity_id = record["entity_id"]

        if entity_id in entity_ids:
            raise ValueError(
                f"Duplicate entity_id found: {entity_id}"
            )

        entity_ids.add(entity_id)

    print(f"✓ Records found: {len(records)}")
    print(f"✓ Unique entity IDs: {len(entity_ids)}")

    # Your expected test dataset size
    if len(records) != 50:
        print()
        print(
            f"WARNING: Expected 50 records, "
            f"but found {len(records)}."
        )


# ============================================================
# Enroll records
# ============================================================

def enroll_records(records):
    print()
    print("=" * 60)
    print("Submitting records to /api/v1/enroll-batch")
    print("=" * 60)

    payload = {
        "records": records
    }

    print()
    print(f"Sending {len(records)} records...")
    print()

    status_code, response = post_json(
        ENROLL_BATCH_ENDPOINT,
        payload
    )

    print(f"HTTP status: {status_code}")

    if status_code < 200 or status_code >= 300:
        raise RuntimeError(
            f"Enroll batch failed with HTTP {status_code}"
        )

    # Save raw response for debugging/auditing
    response_file = BASE_DIR / "enroll_response.json"

    with response_file.open(
        mode="w",
        encoding="utf-8"
    ) as file:

        json.dump(
            response,
            file,
            indent=2
        )

    print(f"✓ Enrollment request completed")
    print(f"✓ Raw API response saved to:")
    print(f"  {response_file}")

    # --------------------------------------------------------
    # Parse results
    # --------------------------------------------------------

    results = []

    if isinstance(response, dict):
        results = response.get("results", [])

    if results:
        total_edges = 0
        records_with_edges = 0
        records_without_edges = 0

        for result in results:

            edges = result.get("edges", [])

            total_edges += len(edges)

            if edges:
                records_with_edges += 1
            else:
                records_without_edges += 1

        print()
        print("Enrollment summary:")
        print(f"  Records returned : {len(results)}")
        print(f"  Records with edges : {records_with_edges}")
        print(f"  Records without edges : {records_without_edges}")
        print(f"  Total edges : {total_edges}")

        print()
        print("First few results:")

        for result in results[:10]:

            entity_id = result.get("id")
            edges = result.get("edges", [])

            print(
                f"  {entity_id}: "
                f"{len(edges)} edge(s)"
            )

    else:
        print()
        print(
            "WARNING: Response did not contain a "
            "'results' array."
        )

        print()
        print("Response:")
        print(json.dumps(response, indent=2))

    return response


# ============================================================
# Flush output
# ============================================================

def flush_output():
    print()
    print("=" * 60)
    print("Flushing Melder output")
    print("=" * 60)

    status_code, response = post_json(
        FLUSH_ENDPOINT
    )

    print()
    print(f"HTTP status: {status_code}")

    if status_code != 202:
        print()
        print("WARNING:")
        print(
            f"Expected HTTP 202 from /admin/flush "
            f"but received {status_code}"
        )

    else:
        print("✓ Flush request accepted")

    # Save flush response
    flush_response_file = BASE_DIR / "flush_response.json"

    with flush_response_file.open(
        mode="w",
        encoding="utf-8"
    ) as file:

        json.dump(
            response,
            file,
            indent=2
        )

    print()
    print("Flush response:")

    print(
        json.dumps(
            response,
            indent=2
        )
    )

    print()
    print(
        "Melder builds the configured outputs asynchronously."
    )

    return response


# ============================================================
# Wait for output
# ============================================================

def wait_for_output(timeout_seconds=60):
    print()
    print("=" * 60)
    print("Waiting for output files")
    print("=" * 60)

    start_time = time.time()

    while time.time() - start_time < timeout_seconds:

        if OUTPUT_DIR.exists():

            files = [
                path
                for path in OUTPUT_DIR.rglob("*")
                if path.is_file()
            ]

            if files:

                print()
                print("✓ Output files detected:")

                for file in files:
                    print(
                        f"  {file.relative_to(BASE_DIR)}"
                    )

                return True

        time.sleep(2)

        print(".", end="", flush=True)

    print()
    print()
    print(
        "WARNING: No output files detected within "
        f"{timeout_seconds} seconds."
    )

    print()
    print(
        "The flush may still be processing, or the configured "
        "output path may differ."
    )

    return False


# ============================================================
# Main
# ============================================================

def main():

    print()
    print("=" * 60)
    print("        MELDER ENROLL MODE TEST")
    print("=" * 60)
    print()

    print(f"Input CSV : {CSV_FILE}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"API       : {BASE_URL}")

    # --------------------------------------------------------
    # 1. Check Melder
    # --------------------------------------------------------

    if not check_melder():
        sys.exit(1)

    # --------------------------------------------------------
    # 2. Read CSV
    # --------------------------------------------------------

    try:
        records = read_csv_records()
        validate_records(records)

    except Exception as e:
        print()
        print("ERROR while reading/validating CSV:")
        print(e)
        sys.exit(1)

    # --------------------------------------------------------
    # 3. Enroll batch
    # --------------------------------------------------------

    try:
        enroll_records(records)

    except Exception as e:
        print()
        print("ERROR during enrollment:")
        print(e)
        sys.exit(1)

    # --------------------------------------------------------
    # 4. Flush
    # --------------------------------------------------------

    try:
        flush_output()

    except Exception as e:
        print()
        print("ERROR while flushing output:")
        print(e)
        sys.exit(1)

    # --------------------------------------------------------
    # 5. Wait for output
    # --------------------------------------------------------

    wait_for_output()

    # --------------------------------------------------------
    # Done
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("                 TEST COMPLETE")
    print("=" * 60)

    print()
    print("Input:")
    print(f"  {CSV_FILE}")

    print()
    print("Output:")
    print(f"  {OUTPUT_DIR}")

    print()
    print("API response:")
    print(
        f"  {BASE_DIR / 'enroll_response.json'}"
    )

    print()
    print("Flush response:")
    print(
        f"  {BASE_DIR / 'flush_response.json'}"
    )

    print()


if __name__ == "__main__":
    main()