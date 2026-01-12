# ⚡ YOLO Object Detector - Cloud Functions

Firebase Cloud Functions (Python) for orchestrating the object detection pipeline.

---

## 📋 Overview

This Cloud Function acts as the orchestrator between Firebase Storage and Cloud Run:

1. **Triggers** when image uploaded to `uploads/` folder
2. **Downloads** the image from Storage
3. **Calls** Cloud Run for YOLO inference
4. **Saves** annotated image to `results/` folder
5. **Updates** Firestore with detection results

---

## 🛠️ Prerequisites

- **Python 3.11+**
- **Firebase CLI** (`npm install -g firebase-tools`)
- **Firebase Project** with Blaze plan (pay-as-you-go)
- **Cloud Run** backend deployed

---

## 🚀 Quick Start

### 1. Install Firebase CLI

```bash
npm install -g firebase-tools
```

### 2. Login to Firebase

```bash
firebase login
```

### 3. Initialize Functions

```bash
# In project root
firebase init functions

# Select:
# - Python
# - Use existing project
# - Install dependencies now
```

### 4. Configure Cloud Run URL

Edit `main.py`:

```python
# Line 18 - Update with your Cloud Run URL
CLOUD_RUN_URL = "https://your-cloud-run-url.run.app/predict"
```

### 5. Deploy

```bash
firebase deploy --only functions
```

---

## 📁 Project Structure

```text
Firebase_functions
├──functions/
│  ├── main.py                  # Cloud Function code
│  └── requirements.txt         # Python dependencies
├── firebase.json               # Firebase configuration
└── README.md                   # This file
```

---

## 📄 File Descriptions

### `main.py`

Main Cloud Function with:

- **Trigger**: `@storage_fn.on_object_finalized()`
- **Validation**: File path and type checking
- **Download**: Image from Storage
- **Processing**: Call Cloud Run API
- **Upload**: Annotated image back to Storage
- **Database**: Update Firestore with results
- **Error Handling**: Retry logic and error logging

**Key Features:**

- 3 retry attempts with exponential backoff
- Comprehensive logging
- Duplicate detection prevention
- Graceful error handling

---

## 📊 Function Workflow

```text
1. Image Uploaded
   └─ uploads/img_123.jpg
      │
2. Function Triggered
   └─ process_object_detection()
      │
3. Validation
   ├─ Check folder (uploads/)
   ├─ Check file type (.jpg, .png)
   └─ Check if already processed
      │
4. Download Image
   └─ From Firebase Storage
      │
5. Call Cloud Run (with retries)
   ├─ Encode to base64
   ├─ POST /predict
   ├─ Retry on failure (3x)
   └─ Get detections
      │
6. Save Results
   ├─ Upload annotated image → results/
   └─ Update Firestore document
      │
7. Complete
   └─ Return success
```

---

## 🔥 Firebase Rules

### Firestore Rules (`firestore.rules`)

```javascript
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    
    // Detection results collection
    match /detection_results/{docId} {
      // Anyone can read (for demo)
      allow read: if true;
      
      // Only Cloud Functions can write
      allow write: if false;
    }
  }
}
```

### Storage Rules (`storage.rules`)

```javascript
rules_version = '2';

service firebase.storage {
  match /b/{bucket}/o {
    
    // Uploads folder - anyone can upload
    match /uploads/{allPaths=**} {
      allow read, write: if true;
    }
    
    // Results folder - read only
    match /results/{allPaths=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

---

## 🚀 Deployment

### Deploy Functions

```bash
# Deploy all functions
firebase deploy --only functions
```

---

## 🐛 Troubleshooting

### Issue: Function not triggering

**Check:**

```bash
# View function status
firebase functions:list

# Check logs
firebase functions:log
```

**Solutions:**

1. Verify function is deployed
2. Check Storage trigger configuration
3. Ensure file uploaded to `uploads/` folder
4. Check Firebase quota/billing

### Issue: Cloud Run unreachable

**Check:**

```bash
# Test Cloud Run directly
curl https://your-cloud-run-url.run.app/health
```

**Solutions:**

1. Verify CLOUD_RUN_URL is correct
2. Check Cloud Run allows unauthenticated access
3. Test network connectivity

### Issue: Timeout errors

**Solutions:**

```python
# Increase timeout in firebase.json
{
  "functions": [{
    "timeoutSeconds": 540  # Max 540 seconds
  }]
}
```

```bash
firebase deploy --only functions
```

### Issue: Out of memory

**Solutions:**

```python
# Increase memory in firebase.json
{
  "functions": [{
    "memory": "1GB"  # Options: 256MB, 512MB, 1GB, 2GB, 4GB
  }]
}
```

---

## 📊 Monitoring

### Firebase Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Navigate to **Functions**
4. View:
   - Invocations
   - Execution time
   - Memory usage
   - Error rate
   - Logs

### Metrics to Monitor

- **Invocations**: How many times function runs
- **Execution time**: Average processing time
- **Memory usage**: Peak memory consumption
- **Error rate**: Percentage of failed executions
- **Retry rate**: How often retries are needed

---

## 💰 Cost Optimization

### Pricing

Firebase Functions (Blaze plan):

- **Invocations**: $0.40/million
- **Compute time**: $0.0000025/GB-second
- **Networking**: $0.12/GB outbound

**Example cost** (1000 images/day):

- Invocations: ~$0.01/month
- Compute: ~$2/month
- Networking: ~$1/month
- **Total**: ~$3/month

### Optimization Tips

1. **Reduce retries**: Improve Cloud Run reliability
2. **Efficient image handling**: Don't store in memory unnecessarily
3. **Batch operations**: Process multiple images if needed
4. **Region selection**: Same region as Storage/Cloud Run
5. **Timeout**: Set appropriate timeout (not too high)

---

## 🔐 Security Best Practices

### 1. Service Account Permissions

Grant minimal required permissions:

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### 2. Firestore Rules

Prevent unauthorized writes:

```javascript
match /detection_results/{docId} {
  allow read: if request.auth != null;  // Authenticated users only
  allow write: if false;  // Only Cloud Functions
}
```

### 3. Storage Rules

Limit file sizes and types:

```javascript
match /uploads/{fileName} {
  allow write: if request.resource.size < 10 * 1024 * 1024  // 10MB limit
               && request.resource.contentType.matches('image/.*');
}
```

### 4. Environment Variables

Never commit secrets:

```bash
# Set secret
firebase functions:secrets:set CLOUD_RUN_URL

# Use in function
import os
CLOUD_RUN_URL = os.environ.get('CLOUD_RUN_URL')
```

---

## 🔗 Useful Links

- [Firebase Functions Python](https://firebase.google.com/docs/functions/python)
- [Cloud Storage Triggers](https://firebase.google.com/docs/functions/gcp-storage-events)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Pricing](https://firebase.google.com/pricing)

---

## 📧 Support

For Cloud Functions issues:

- Check function logs: `firebase functions:log`
- Test Cloud Run independently
- Verify trigger configuration
- Check Firebase quota and billing

---

Orchestrating magic with Cloud Functions ⚡

## 🤝 Contributing

If you'd like to contribute to this project, feel free to submit a pull request. Please make sure your code follows the existing style and includes appropriate comments.

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes.
4. Push to the branch.
5. Submit a pull request.

## 👤 Author

````Carlos Antonio Martinez Miranda````

GitHub: [@CarlosM1024](https://github.com/CarlosM1024)
