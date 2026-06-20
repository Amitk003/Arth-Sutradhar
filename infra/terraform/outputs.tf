output "project_id" {
  value = var.project_id
}

output "raw_documents_bucket" {
  value = google_storage_bucket.raw_documents.name
}

output "processed_data_bucket" {
  value = google_storage_bucket.processed_data.name
}

output "bq_dataset_id" {
  value = google_bigquery_dataset.arth_sutradhar.dataset_id
}

output "bq_embedding_connection" {
  value = google_bigquery_connection.vertex_ai_embedding.name
}

output "artifact_registry" {
  value = google_artifact_registry_repository.main.repository_id
}
