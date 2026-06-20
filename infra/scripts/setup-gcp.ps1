param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,
    [Parameter(Mandatory = $false)]
    [string]$Region = "asia-south1"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Arth-Sutradhar GCP Setup" -ForegroundColor Cyan
Write-Host "  Project: $ProjectId" -ForegroundColor Cyan
Write-Host "  Region:  $Region" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Set active project
Write-Host "`n[1/5] Setting active project..." -ForegroundColor Yellow
gcloud config set project $ProjectId
if ($LASTEXITCODE -ne 0) { exit 1 }

# Step 2: Enable APIs
Write-Host "`n[2/5] Enabling required APIs..." -ForegroundColor Yellow
& "$PSScriptRoot\enable-apis.ps1" -ProjectId $ProjectId
if ($LASTEXITCODE -ne 0) { exit 1 }

# Step 3: Create Terraform state bucket
Write-Host "`n[3/5] Creating Terraform state bucket..." -ForegroundColor Yellow
$tfBucket = "${ProjectId}-tfstate"
gsutil ls "gs://$tfBucket" 2>$null
if ($LASTEXITCODE -ne 0) {
    gcloud storage buckets create "gs://$tfBucket" --location=$Region --uniform-bucket-level-access --versioning
    Write-Host "  Bucket $tfBucket created" -ForegroundColor Green
} else {
    Write-Host "  Bucket $tfBucket already exists" -ForegroundColor Green
}

# Step 4: Configure Docker for Artifact Registry
Write-Host "`n[4/5] Configuring Docker for Artifact Registry..." -ForegroundColor Yellow
gcloud auth configure-docker ${Region}-docker.pkg.dev
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Docker configured" -ForegroundColor Green
}

# Step 5: Verify setup
Write-Host "`n[5/5] Verifying setup..." -ForegroundColor Yellow
gcloud config list
gcloud services list --enabled --project $ProjectId | Select-String -Pattern "aiplatform|bigquery|cloudrun"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  GCP Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:"
Write-Host "  1. cd infra/terraform"
Write-Host "  2. Copy terraform.tfvars.example to terraform.tfvars"
Write-Host "  3. Run: terraform init"
Write-Host "  4. Run: terraform plan"
Write-Host "  5. Run: terraform apply"
