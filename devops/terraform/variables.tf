variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Firebase credentials
variable "firebase_private_key_id" {
  description = "Firebase Private Key ID"
  type        = string
  sensitive   = true
}

variable "firebase_private_key" {
  description = "Firebase Private Key"
  type        = string
  sensitive   = true
}

variable "firebase_client_email" {
  description = "Firebase Client Email"
  type        = string
  sensitive   = true
}

variable "firebase_client_id" {
  description = "Firebase Client ID"
  type        = string
  sensitive   = true
}

variable "firebase_client_x509_cert_url" {
  description = "Firebase Client X509 Cert URL"
  type        = string
  sensitive   = true
}
