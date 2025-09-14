# 🚀 הוראות התקנה מהירה

## שלב 1: הגדרת Firebase

### 1.1 צור פרויקט Firebase
1. לך ל-[Firebase Console](https://console.firebase.google.com/)
2. לחץ "Create a project"
3. תן שם לפרויקט (למשל: `test-env-project`)
4. הפעל Google Analytics (אופציונלי)

### 1.2 הפעל Authentication
1. בפרויקט שלך → "Authentication" → "Sign-in method"
2. הפעל "Email/Password"
3. שמור

### 1.3 הפעל Firestore
1. "Firestore Database" → "Create database"
2. בחר "Start in test mode"
3. בחר location (us-central1)

### 1.4 הורד Service Account Key
1. "Project Settings" (⚙️) → "Service accounts"
2. לחץ "Generate new private key"
3. הורד את ה-JSON file
4. **שנה את השם ל-`firebase-key.json`**
5. **העבר את הקובץ לתיקיית הפרויקט**

## שלב 2: הרצה מקומית

### 2.1 העתק קובץ סביבה
```bash
cp env.example .env
```

### 2.2 ערוך את .env
```bash
# פתח את הקובץ
nano .env
```

**החלף רק את השורה הזו:**
```
FIREBASE_PROJECT_ID=your-actual-project-id
```

**השאר הכל כמו שהוא!** (הקוד יקרא מה-JSON file)

### 2.3 הרץ את השירותים
```bash
# עצור שירותים קיימים
docker-compose down

# הרץ מחדש
docker-compose up --build
```

## שלב 3: בדיקה

### 3.1 בדוק שהשירותים רצים
```bash
# בדוק status
docker-compose ps

# בדוק logs
docker-compose logs
```

### 3.2 בדוק את ה-APIs
- **API Gateway**: http://localhost:8000/docs
- **User Manager**: http://localhost:8001/docs
- **Health Check**: http://localhost:8000/health

## שלב 4: יצירת משתמש (אופציונלי)

אם Firebase מוגדר נכון, תוכל ליצור משתמש:

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## 🔧 פתרון בעיות

### בעיה: User Manager לא רץ
**פתרון**: בדוק שה-`firebase-key.json` קיים בתיקיית הפרויקט

### בעיה: Firebase credentials error
**פתרון**: 
1. הורד מחדש את ה-JSON מ-Firebase Console
2. שנה שם ל-`firebase-key.json`
3. העבר לתיקיית הפרויקט

### בעיה: Port כבר בשימוש
**פתרון**:
```bash
# עצור שירותים אחרים
docker-compose down

# או שנה ports ב-docker-compose.yml
```

## ✅ סיכום

אחרי ההתקנה תהיה לך:
- ✅ API Gateway רץ על port 8000
- ✅ User Manager רץ על port 8001  
- ✅ Firebase מחובר (אם ה-JSON קיים)
- ✅ APIs זמינים ב-http://localhost:8000/docs

**הפרויקט מוכן לפיתוח!** 🎉
