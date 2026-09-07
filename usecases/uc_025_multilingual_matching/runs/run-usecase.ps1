param (
    [Parameter(Mandatory = $true)]
    [string]$Target
)

$ErrorActionPreference = "Stop"

# Get script directory
$USECASES_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Repository root
$REPO_ROOT = Split-Path -Parent $USECASES_DIR

# Melder binary
$MELDER_BIN = Join-Path $REPO_ROOT "target\release\meld.exe"


function Show-Usage {
    Write-Host "Usage: .\run-usecase.ps1 <usecase-folder-name|all>"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run-usecase.ps1 uc_001_company_entity_resolution"
    Write-Host "  .\run-usecase.ps1 uc_002_normalized_exact_match"
    Write-Host "  .\run-usecase.ps1 all"
    exit 1
}


# Check Melder binary
if (-not (Test-Path $MELDER_BIN)) {
    Write-Host "Melder binary not found: $MELDER_BIN"
    Write-Host "Build it first with:"
    Write-Host "  cargo build --release"
    exit 1
}


function Run-Case {

    param (
        [string]$CaseName
    )

    $case_dir = Join-Path $USECASES_DIR $CaseName
    $config_file = Join-Path $case_dir "config.yaml"

    # Check use case folder
    if (-not (Test-Path $case_dir -PathType Container)) {
        Write-Host "Use case folder not found: $case_dir"
        return
    }

    # Check config file
    if (-not (Test-Path $config_file -PathType Leaf)) {
        Write-Host "Config file not found in $case_dir"
        return
    }

    # Create runs and cache directories
    $runs_dir = Join-Path $case_dir "runs"
    $cache_dir = Join-Path $case_dir "cache"

    New-Item -ItemType Directory -Force -Path $runs_dir | Out-Null
    New-Item -ItemType Directory -Force -Path $cache_dir | Out-Null


    # Find the latest run number
    $last_run = 0

    $runFolders = Get-ChildItem -Path $runs_dir -Directory -ErrorAction SilentlyContinue

    foreach ($folder in $runFolders) {

        if ($folder.Name -match '^run_(\d+)$') {

            $run_num = [int]$Matches[1]

            if ($run_num -gt $last_run) {
                $last_run = $run_num
            }
        }
    }


    # Create next run directory
    $next_run = $last_run + 1

    $run_name = "run_{0:D3}" -f $next_run
    $run_dir = Join-Path $runs_dir $run_name

    New-Item -ItemType Directory -Force -Path $run_dir | Out-Null


    # Create temporary config
    $temp_dir = [System.IO.Path]::GetTempPath()

    $tmp_config = Join-Path `
        $temp_dir `
        ("melder_config_{0}.yaml" -f [System.Guid]::NewGuid().ToString())


    # Read original config
    $config_content = Get-Content $config_file -Raw


    # Convert Windows paths to forward slashes for YAML/config compatibility
    $run_dir_config = $run_dir -replace '\\', '/'


    # Replace crossmap.csv path
    $config_content = $config_content -replace `
        'path: .*?/runs/crossmap\.csv',
        "path: $run_dir_config/crossmap.csv"


    # Replace csv_dir_path
    $config_content = $config_content -replace `
        'csv_dir_path: .*',
        "csv_dir_path: $run_dir_config"


    # Write temporary config
    Set-Content `
        -Path $tmp_config `
        -Value $config_content `
        -Encoding UTF8


    try {

        Write-Host ""
        Write-Host "Starting Melder run for $CaseName"
        Write-Host "Config: $config_file"
        Write-Host "Using run config: $tmp_config"
        Write-Host ""


        # Validate
        & $MELDER_BIN validate --config $tmp_config

        if ($LASTEXITCODE -ne 0) {
            throw "Validation failed for $CaseName"
        }


        # Run
        & $MELDER_BIN run --config $tmp_config

        if ($LASTEXITCODE -ne 0) {
            throw "Melder run failed for $CaseName"
        }


        Write-Host ""
        Write-Host "Run completed: $run_dir"
    }
    finally {

        # Remove temporary config
        if (Test-Path $tmp_config) {
            Remove-Item $tmp_config -Force
        }
    }
}


# Run all use cases
if ($Target -eq "all") {

    Get-ChildItem -Path $USECASES_DIR -Directory | ForEach-Object {

        $config_file = Join-Path $_.FullName "config.yaml"

        if (Test-Path $config_file) {
            Run-Case $_.Name
        }
    }

}
else {

    Run-Case $Target

}
