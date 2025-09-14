# Microservices Project with FastAPI and Cloud Run

פרויקט מיקרו-שירותים עם FastAPI, Firebase, ו-Google Cloud Run.

## מבנה הפרויקט

```
├── backend/
│   ├── gateway/           # API Gateway (External)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── user-manager/      # User Manager (Internal)
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── devops/
│   ├── terraform/         # Infrastructure as Code
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars.example
│   └── .github/workflows/ # CI/CD Pipeline
│       └── deploy.yml
├── docker-compose.yml     # Local development
└── env.example           # Environment variables template
```

## שירותים

### 1. API Gateway (External)
- **Port**: 8000
- **תפקיד**: Gateway חיצוני שמנתב בקשות למיקרו-שירותים
- **גישה**: ציבורית
- **טכנולוגיות**: FastAPI, httpx

### 2. User Manager (Internal)
- **Port**: 8001
- **תפקיד**: ניהול משתמשים עם Firebase
- **גישה**: פנימית בלבד
- **טכנולוגיות**: FastAPI, Firebase Admin SDK

## התקנה ופיתוח מקומי

### דרישות מוקדמות
- Python 3.11+
- Docker & Docker Compose
- Firebase Project
- GCP Project

### 1. הגדרת Firebase
1. צור פרויקט ב-Firebase Console
2. הפעל Authentication ו-Firestore
3. צור Service Account וורד את ה-JSON
3. העתק את הפרטים ל-`env.example` ושנה ל-`.env`

### 2. הרצה מקומית
```bash
# Clone the repository
git clone https://github.com/gadshushan3030/test_env.git
cd test_env

# Copy environment file
cp env.example .env
# Edit .env with your Firebase credentials

# Run with Docker Compose
docker-compose up --build
```

### 3. בדיקת השירותים
- API Gateway: http://localhost:8000
- User Manager: http://localhost:8001
- API Documentation: http://localhost:8000/docs

## פריסה ל-Cloud Run

### 1. הגדרת GCP
```bash
# Install gcloud CLI
# Login to GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. הגדרת Terraform
```bash
cd devops/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and apply
terraform init
terraform plan
terraform apply
```

### 3. CI/CD עם GitHub Actions
1. הוסף את ה-Secrets הבאים ל-GitHub:
   - `GCP_PROJECT_ID`: Project ID שלך
   - `GCP_SA_KEY`: Service Account Key (JSON)
   - `FIREBASE_*`: Firebase credentials

2. Push ל-main branch יגרום לפריסה אוטומטית

## API Endpoints

### API Gateway (External)
- `GET /health` - Health check
- `POST /api/users/` - Create user
- `GET /api/users/{user_id}` - Get user
- `GET /api/users/` - List users
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user

### User Manager (Internal)
- `GET /health` - Health check
- `POST /users/` - Create user
- `GET /users/{user_id}` - Get user
- `GET /users/` - List users
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

## ארכיטקטורה

```
Internet → API Gateway (External) → User Manager (Internal) → Firebase
```

- **API Gateway**: מקבל בקשות חיצוניות ומנתב אותן
- **User Manager**: מטפל בניהול משתמשים עם Firebase
- **Firebase**: Authentication ו-Firestore Database
- **Cloud Run**: Container orchestration
- **Terraform**: Infrastructure as Code

## פיתוח

### הוספת endpoint חדש
1. הוסף את ה-endpoint ב-User Manager
2. הוסף proxy ב-API Gateway
3. עדכן את ה-Dockerfiles אם נדרש
4. בדוק עם Docker Compose מקומי

### בדיקות
```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:8001/health

# Create user
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## Troubleshooting

### בעיות נפוצות
1. **Firebase Authentication**: בדוק שה-Service Account מוגדר נכון
2. **Docker Build**: בדוק שה-requirements.txt מעודכן
3. **Cloud Run**: בדוק שה-IAM permissions נכונים
4. **Terraform**: בדוק שה-variables מוגדרים נכון

### Logs
```bash
# Local logs
docker-compose logs -f

# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision"
```