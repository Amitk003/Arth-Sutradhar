param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $false)]
    [string]$Region = "asia-south1",
    [Parameter(Mandatory = $false)]
    [string]$ServiceName = "arth-sutradhar-api"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deploying Arth-Sutradhar to Cloud Run"
Write-Host "  Using: gcloud run deploy --source"
Write-Host "========================================" -ForegroundColor Cyan

# Grant Cloud Build service account storage access first
Write-Host "`n[1/3] Granting Cloud Build storage permissions..." -ForegroundColor Yellow
$CB_SA = "${ProjectId}@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding $ProjectId `
    --member="serviceAccount:$CB_SA" `
    --role="roles/storage.objectAdmin" `
    --condition=None 2>&1 | Out-Null
Write-Host "  Permissions granted (may already exist)" -ForegroundColor Green

# Deploy using --source (Cloud Build handles the Docker build)
Write-Host "`n[2/3] Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --source $RepoRoot `
    --region $Region `
    --project $ProjectId `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --min-instances 0 `
    --max-instances 10 `
    --concurrency 80 `
    --timeout 300 `
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$ProjectId,PROJECT_ID=$ProjectId,REGION=$Region,BQ_DATASET=arth_sutradhar,BQ_TABLE=land_records_chunks,BQ_MODEL=land_records_embedding_model"
if ($LASTEXITCODE -ne 0) { exit 1 }

# Get the service URL
Write-Host "`n[3/3] Getting service URL..." -ForegroundColor Yellow
$Url = gcloud run services describe $ServiceName --region=$Region --project=$ProjectId --format="value(status.url)"
Write-Host "  Service URL: $Url" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTest with:"
Write-Host '  curl -X POST ${Url}/query -H "Content-Type: application/json" -d "{\"text\": \"How will inflation affect cotton farmers in Gujarat?\"}"'
