param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId
)

Write-Host "Granting storage permissions to the default compute service account..." -ForegroundColor Cyan

$SA = "638364788058-compute@developer.gserviceaccount.com"

# Grant storage.objectAdmin on the specific build buckets
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

Write-Host "`nDone! Try deploying again." -ForegroundColor Cyan
