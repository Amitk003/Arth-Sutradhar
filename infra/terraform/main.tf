# Enable required GCP APIs
resource "google_project_service" "apis" {
  for_each = toset([
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

# Cloud Storage bucket for Terraform state
resource "google_storage_bucket" "tfstate" {
  name          = "${var.project_id}-tfstate"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
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

# Grant Vertex AI User role to the BigQuery connection service account
resource "google_project_iam_member" "bq_connection_vertex_ai_user" {
  project = var.project_id
  role    = "roles/vertexai.user"
  member  = "serviceAccount:${google_bigquery_connection.vertex_ai_embedding.cloud_resource[0].service_account_id}"
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "main" {
  repository_id = "arth-sutradhar"
  description   = "Docker repository for Arth-Sutradhar services"
  format        = "DOCKER"
  location      = var.region
  depends_on    = [google_project_service.apis]
}

# Cloud Run service placeholder (will be populated in later phases)
resource "google_cloud_run_v2_service" "agent_api" {
  name     = "arth-sutradhar-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}/agent-api:latest"
      ports {
        container_port = 8080
      }
    }
  }

  depends_on = [google_project_service.apis]
}

# Allow unauthenticated access for the API (will lock down in production)
resource "google_cloud_run_v2_service_iam_member" "public_access" {
  name     = google_cloud_run_v2_service.agent_api.name
  location = google_cloud_run_v2_service.agent_api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}
