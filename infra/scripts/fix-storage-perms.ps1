param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId
)

Write-Host "Granting storage permissions to default compute service account..." -ForegroundColor Cyan

$ProjectNumber = gcloud projects describe $ProjectId --format="value(projectNumber)" 2>$null
if (-not $ProjectNumber) {
    Write-Host "  Could not determine project number. Aborting." -ForegroundColor Red
    exit 1
}

$SA = "${ProjectNumber}-compute@developer.gserviceaccount.com"

$buckets = @(
    "run-sources-${ProjectId}-asia-south1",
    "${ProjectId}_cloudbuild"
)

foreach ($bucket in $buckets) {
    Write-Host "  Granting access to gs://$bucket ..." -ForegroundColor Yellow
    gsutil iam ch "serviceAccount:${SA}:objectAdmin" "gs://$bucket" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK" -ForegroundColor Green
    } else {
        Write-Host "    Bucket may not exist yet, skipping" -ForegroundColor Yellow
    }
}

Write-Host "`nDone!" -ForegroundColor Cyan
