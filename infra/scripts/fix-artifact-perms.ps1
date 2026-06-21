param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId
)

Write-Host "Granting Artifact Registry permissions to Cloud Build service account..." -ForegroundColor Cyan

# Cloud Build SA uses project NUMBER, not project ID
$ProjectNumber = gcloud projects describe $ProjectId --format="value(projectNumber)" 2>$null
if (-not $ProjectNumber) {
    Write-Host "  Could not determine project number. Aborting." -ForegroundColor Red
    exit 1
}

$CB_SA = "${ProjectNumber}@cloudbuild.gserviceaccount.com"

Write-Host "  Project: $ProjectId ($ProjectNumber)" -ForegroundColor Yellow
Write-Host "  Service Account: $CB_SA" -ForegroundColor Yellow

gcloud projects add-iam-policy-binding $ProjectId `
    --member="serviceAccount:$CB_SA" `
    --role="roles/artifactregistry.writer" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK - artifactregistry.writer granted" -ForegroundColor Green
} else {
    Write-Host "  Failed via project-level. Trying repository-level..." -ForegroundColor Yellow
    gcloud artifacts repositories add-iam-policy-binding arth-sutradhar `
        --location=asia-south1 `
        --project=$ProjectId `
        --member="serviceAccount:$CB_SA" `
        --role="roles/artifactregistry.writer" 2>&1
}

Write-Host "`nDone! Try deploying again." -ForegroundColor Cyan
