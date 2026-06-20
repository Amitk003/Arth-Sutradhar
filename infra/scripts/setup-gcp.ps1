param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $false)]
    [string]$Region = "asia-south1"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Arth-Sutradhar GCP Setup"
Write-Host "  Project: $ProjectId"
Write-Host "  Region:  $Region"
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[1/5] Setting active project..." -ForegroundColor Yellow
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n[2/5] Enabling required APIs..." -ForegroundColor Yellow
& "$PSScriptRoot\enable-apis.ps1" -ProjectId $ProjectId
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n[3/5] Creating Terraform state bucket..." -ForegroundColor Yellow
$tfBucket = "${ProjectId}-tfstate"
gsutil ls "gs://$tfBucket" 2>$null
if ($LASTEXITCODE -ne 0) {
    gcloud storage buckets create "gs://$tfBucket" --location=$Region --uniform-bucket-level-access
    gcloud storage buckets update "gs://$tfBucket" --versioning
    Write-Host "  Bucket $tfBucket created" -ForegroundColor Green
} else {
    Write-Host "  Bucket $tfBucket already exists" -ForegroundColor Green
}

Write-Host "`n[4/5] Configuring Docker for Artifact Registry..." -ForegroundColor Yellow
gcloud auth configure-docker ${Region}-docker.pkg.dev --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Docker configured" -ForegroundColor Green
}

Write-Host "`n[5/5] Verifying setup..." -ForegroundColor Yellow
gcloud config list
gcloud services list --enabled --project $ProjectId | Select-String -Pattern "aiplatform|bigquery|cloudrun"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  GCP Setup Complete!"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:"
Write-Host "  1. cd infra/terraform"
Write-Host "  2. Copy terraform.tfvars.example to terraform.tfvars"
Write-Host "  3. Run: terraform init"
Write-Host "  4. Run: terraform plan"
Write-Host "  5. Run: terraform apply"
