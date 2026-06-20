variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "asia-south1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID for vector store"
  type        = string
  default     = "arth_sutradhar"
}

variable "bq_region" {
  description = "BigQuery dataset location"
  type        = string
  default     = "asia-south1"
}
