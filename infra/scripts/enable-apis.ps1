# Enable GCP APIs for Arth-Sutradhar
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId
)

$apis = @(
    "aiplatform.googleapis.com",
    "bigquery.googleapis.com",
    "bigqueryconnection.googleapis.com",
    "storage.googleapis.com",
    "cloudrun.googleapis.com",
    "artifactregistry.googleapis.com",
    "eventarc.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "documentai.googleapis.com",
    "speech.googleapis.com",
    "translate.googleapis.com",
    "texttospeech.googleapis.com"
)

Write-Host "Enabling APIs for project: $ProjectId" -ForegroundColor Green

foreach ($api in $apis) {
    Write-Host "  Enabling $api..." -ForegroundColor Yellow
    gcloud services enable $api --project $ProjectId
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✓ $api enabled" -ForegroundColor Green
    } else {
        Write-Host "    ✗ $api FAILED" -ForegroundColor Red
    }
}

Write-Host "`nAll APIs enabled successfully!" -ForegroundColor Green
