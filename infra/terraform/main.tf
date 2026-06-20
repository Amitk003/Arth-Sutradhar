# Enable required GCP APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "aiplatform.googleapis.com",
    "bigquery.googleapis.com",
    "bigqueryconnection.googleapis.com",
    "storage.googleapis.com",
    "artifactregistry.googleapis.com",
    "eventarc.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "documentai.googleapis.com",
    "speech.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

# Cloud Storage bucket for raw document ingestion
resource "google_storage_bucket" "raw_documents" {
  name          = "${var.project_id}-raw-documents"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90
    }
  }
}

# Cloud Storage bucket for processed/chunked data
resource "google_storage_bucket" "processed_data" {
  name          = "${var.project_id}-processed-data"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true
}

# BigQuery dataset for vector store
resource "google_bigquery_dataset" "arth_sutradhar" {
  dataset_id  = var.bq_dataset_id
  description = "Arth-Sutradhar vector store and land records data"
  location    = var.bq_region
  depends_on  = [google_project_service.apis]
}

# BigQuery connection to Vertex AI for embeddings
resource "google_bigquery_connection" "vertex_ai_embedding" {
  connection_id = "vertex-ai-embedding"
  location      = var.bq_region
  friendly_name = "Vertex AI Embedding Connection"
  description   = "Connection to Vertex AI for generating text embeddings"

  cloud_resource {}
  depends_on = [google_project_service.apis]
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "main" {
  repository_id = "arth-sutradhar"
  description   = "Docker repository for Arth-Sutradhar services"
  format        = "DOCKER"
  location      = var.region
  depends_on    = [google_project_service.apis]
}

# Cloud Run service will be created in Phase 2 when we have a Docker image
