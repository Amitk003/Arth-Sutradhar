param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $false)]
    [string]$Region = "asia-south1",
    [Parameter(Mandatory = $false)]
    [string]$ServiceName = "arth-sutradhar-api",
    [Parameter(Mandatory = $false)]
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deploying Arth-Sutradhar to Cloud Run"
Write-Host "  Project: $ProjectId"
Write-Host "  Region:  $Region"
Write-Host "  Service: $ServiceName"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n[1/2] Building & pushing via Cloud Build (see logs at URL below)..." -ForegroundColor Yellow

gcloud builds submit $RepoRoot `
    --config "$RepoRoot\cloudbuild.yaml" `
    --project $ProjectId `
    --substitutions "_TAG=$ImageTag,_REGION=$Region,_SERVICE=$ServiceName"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Build failed. Check logs in Cloud Console." -ForegroundColor Red
    exit 1
}

Write-Host "  Build succeeded!" -ForegroundColor Green

$ImageName = "${Region}-docker.pkg.dev/${ProjectId}/arth-sutradhar/${ServiceName}:${ImageTag}"

Write-Host "`n[2/2] Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $ImageName `
    --region $Region `
    --project $ProjectId `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --min-instances 0 `
    --max-instances 10 `
    --concurrency 80 `
    --timeout 300 `
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$ProjectId,PROJECT_ID=$ProjectId,REGION=$Region,BQ_DATASET=arth_sutradhar,BQ_TABLE=land_records_chunks,BQ_MODEL=land_records_embedding_model,GEMINI_LOCATION=us-central1"

if ($LASTEXITCODE -ne 0) { exit 1 }

$Url = gcloud run services describe $ServiceName --region=$Region --project=$ProjectId --format="value(status.url)"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Cyan
Write-Host "  URL: $Url"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTest with:"
Write-Host '  curl -X POST ${Url}/query -H "Content-Type: application/json" -d "{""text"": ""How will inflation affect cotton farmers in Gujarat?""}"'
