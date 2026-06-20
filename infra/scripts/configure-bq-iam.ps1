param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId
)

$ServiceAccount = "bqcx-638364788058-k6d7@gcp-sa-bigquery-condel.iam.gserviceaccount.com"
$Role = "roles/aiplatform.user"

Write-Host "Configuring BigQuery Vertex AI IAM permissions..." -ForegroundColor Cyan
Write-Host "  Service Account: $ServiceAccount" -ForegroundColor Yellow
Write-Host "  Role: $Role" -ForegroundColor Yellow

Write-Host "`n[1/2] Granting IAM role..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $ProjectId `
    --member="serviceAccount:$ServiceAccount" `
    --role=$Role `
    --condition=None 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  IAM permission granted!" -ForegroundColor Green
} else {
    Write-Host "  Project-level binding failed." -ForegroundColor Yellow
    Write-Host "`n  Alternative - grant at the BigQuery dataset level:" -ForegroundColor Yellow
    Write-Host "  1. Open https://console.cloud.google.com/bigquery?project=$ProjectId" -ForegroundColor White
    Write-Host "  2. Go to the 'arth_sutradhar' dataset" -ForegroundColor White
    Write-Host "  3. Share dataset and add:" -ForegroundColor White
    Write-Host "     Principal: $ServiceAccount" -ForegroundColor White
    Write-Host "     Role: Vertex AI User" -ForegroundColor White
}

Write-Host "`n[2/2] Verifying..." -ForegroundColor Yellow
gcloud projects get-iam-policy $ProjectId --format=json 2>$null | Select-String -Pattern $ServiceAccount
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Permission verified!" -ForegroundColor Green
} else {
    Write-Host "  Check the GCP console to confirm." -ForegroundColor Yellow
}

Write-Host "`nDone!" -ForegroundColor Cyan
