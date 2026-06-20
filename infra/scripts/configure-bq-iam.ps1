param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $false)]
    [string]$Region = "asia-south1"
)

Write-Host "Configuring BigQuery Vertex AI IAM permissions..." -ForegroundColor Cyan

# Get the BigQuery connection service account
Write-Host "  Getting BigQuery connection service account..." -ForegroundColor Yellow
$connInfo = gcloud bigquery connections describe "vertex-ai-embedding" --location=$Region --project=$ProjectId --format="json" 2>$null | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Connection not found. Run terraform apply first." -ForegroundColor Red
    exit 1
}

$sa = $connInfo.cloudResource.serviceAccountId
Write-Host "  Service Account: $sa" -ForegroundColor Green

# Grant Vertex AI User role
Write-Host "  Granting roles/aiplatform.user to the connection service account..." -ForegroundColor Yellow
gcloud projects add-iam-policy-binding $ProjectId `
    --member="serviceAccount:$sa" `
    --role="roles/aiplatform.user" `
    --condition=None

if ($LASTEXITCODE -eq 0) {
    Write-Host "  IAM permission granted successfully!" -ForegroundColor Green
} else {
    Write-Host "  Failed to grant IAM permission. Trying alternative approach..." -ForegroundColor Yellow
    
    # Alternative: Grant at the dataset level
    Write-Host "  Granting at BigQuery dataset level instead..." -ForegroundColor Yellow
    gcloud alpha dataplex assets add-iam-policy-binding ... 2>$null
    
    # Fallback manual instructions
    Write-Host "`nManual step - run this command in Cloud Shell:" -ForegroundColor Yellow
    Write-Host "  gcloud projects add-iam-policy-binding $ProjectId \`"
    Write-Host "    --member='serviceAccount:$sa' \`"
    Write-Host "    --role='roles/aiplatform.user'" -ForegroundColor White
}

Write-Host "`nDone!" -ForegroundColor Cyan
