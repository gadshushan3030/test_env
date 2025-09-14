terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
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

# Enable required APIs
resource "google_project_service" "run_api" {
  service = "run.googleapis.com"
}

resource "google_project_service" "cloudbuild_api" {
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "container_registry_api" {
  service = "containerregistry.googleapis.com"
}

# Container Registry
resource "google_container_registry" "registry" {
  depends_on = [google_project_service.container_registry_api]
}

# IAM for Cloud Build
resource "google_project_iam_member" "cloudbuild_sa" {
  role   = "roles/run.admin"
  member = "serviceAccount:${var.project_id}@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_storage" {
  role   = "roles/storage.admin"
  member = "serviceAccount:${var.project_id}@cloudbuild.gserviceaccount.com"
}

# User Manager Service (Internal)
resource "google_cloud_run_v2_service" "user_manager" {
  name     = "user-manager-${var.environment}"
  location = var.region
  depends_on = [google_project_service.run_api]

  template {
    service_account = google_service_account.user_manager.email
    
    containers {
      image = "gcr.io/${var.project_id}/user-manager:latest"
      
      ports {
        container_port = 8001
      }
      
      env {
        name  = "FIREBASE_PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "FIREBASE_PRIVATE_KEY_ID"
        value = var.firebase_private_key_id
      }
      
      env {
        name  = "FIREBASE_PRIVATE_KEY"
        value = var.firebase_private_key
      }
      
      env {
        name  = "FIREBASE_CLIENT_EMAIL"
        value = var.firebase_client_email
      }
      
      env {
        name  = "FIREBASE_CLIENT_ID"
        value = var.firebase_client_id
      }
      
      env {
        name  = "FIREBASE_CLIENT_X509_CERT_URL"
        value = var.firebase_client_x509_cert_url
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# API Gateway Service (External)
resource "google_cloud_run_v2_service" "api_gateway" {
  name     = "api-gateway-${var.environment}"
  location = var.region
  depends_on = [google_project_service.run_api]

  template {
    service_account = google_service_account.api_gateway.email
    
    containers {
      image = "gcr.io/${var.project_id}/api-gateway:latest"
      
      ports {
        container_port = 8000
      }
      
      env {
        name  = "USER_MANAGER_URL"
        value = "https://${google_cloud_run_v2_service.user_manager.uri}"
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 20
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# Service Accounts
resource "google_service_account" "user_manager" {
  account_id   = "user-manager-${var.environment}"
  display_name = "User Manager Service Account"
}

resource "google_service_account" "api_gateway" {
  account_id   = "api-gateway-${var.environment}"
  display_name = "API Gateway Service Account"
}

# IAM for User Manager (Internal - no public access)
resource "google_cloud_run_v2_service_iam_member" "user_manager_internal" {
  location = google_cloud_run_v2_service.user_manager.location
  name     = google_cloud_run_v2_service.user_manager.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.api_gateway.email}"
}

# IAM for API Gateway (External - public access)
resource "google_cloud_run_v2_service_iam_member" "api_gateway_public" {
  location = google_cloud_run_v2_service.api_gateway.location
  name     = google_cloud_run_v2_service.api_gateway.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "api_gateway_url" {
  description = "API Gateway URL"
  value       = google_cloud_run_v2_service.api_gateway.uri
}

output "user_manager_url" {
  description = "User Manager URL (Internal)"
  value       = google_cloud_run_v2_service.user_manager.uri
}
