# 🐳 YOLO Object Detector - Backend (Cloud Run)

[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![YOLOv8](https://img.shields.io/badge/Model-YOLO11-00ff00)](https://docs.ultralytics.com/)
[![License: AGPL 3.0](https://img.shields.io/badge/License-AGPL_v3.0-blue.svg)](https://opensource.org/licenses/AGPL-3.0)

FastAPI backend for YOLO11n object detection, containerized with Docker and deployed on Google Cloud Run.

---

## 📋 Features

- ⚡ **FastAPI** - Modern, high-performance web framework
- 🤖 **YOLO11n** - Ultralytics latest model (COCO 80 classes)
- 🐳 **Docker** - Containerized for consistent deployment
- ☁️ **Cloud Run** - Serverless, auto-scaling deployment
- 📊 **Automatic Docs** - Interactive API documentation
- 🔍 **Logging** - Structured logging with Loguru
- 🎯 **Optimized** - Fast inference (~200-500ms per image)

---

## 🛠️ Prerequisites

- **Python 3.11+**
- **Docker** (for containerization)
- **Google Cloud SDK** (`gcloud`)
- **Google Cloud Project** with billing enabled

---

## 🚀 Quick Start

### Local Development (without Docker)

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run server
python src/main.py

# 4. Test
curl http://localhost:8080/health
```

Server runs at `http://localhost:8080`

### Local Development (with Docker)

```bash
# 1. Build image
docker build -t yolo-detector .

# 2. Run container
docker run -p 8080:8080 yolo-detector

# 3. Test
curl http://localhost:8080/health
```

---

## 📦 Project Structure

```text
backend/
├── src/
│   ├── main.py              # FastAPI application
│   └── app.py               # YOLO inference logic
│
├── models/                  # Model files (gitignored)
│   └── .gitkeep
│
├── Dockerfile               # Multi-stage build
├── requirements.txt         # Python dependencies
├── .dockerignore           # Files to exclude from Docker
└── README.md               # This file
```

---

## 📄 File Descriptions

### `src/main.py`

FastAPI server with endpoints:

- `GET /` - API information
- `GET /health` - Health check
- `POST /predict` - Object detection endpoint

**Key features:**

- Request validation with Pydantic
- Base64 image encoding/decoding
- Configurable confidence threshold
- Optional annotated image return
- Comprehensive error handling

### `src/app.py`

YOLO inference logic:

- Model initialization
- Image preprocessing
- Detection execution
- Result formatting
- Annotated image generation

**Functions:**

- `is_model_ready()` - Check model status
- `run_inference()` - Run YOLO detection
- `get_annotated_image()` - Generate annotated image
- `get_image_from_bytes()` - Convert bytes to PIL Image
- `get_bytes_from_image()` - Convert PIL Image to bytes

---

## 🔌 API Endpoints

### 1. Health Check

```bash
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "model": "YOLO11n"
}
```

### 2. Root

```bash
GET /
```

**Response:**

```json
{
  "message": "YOLO Object Detector API",
  "version": "2.0.0",
  "model": "YOLO11n (COCO dataset - 80 classes)",
  "endpoints": {
    "health": "/health",
    "predict": "/predict",
    "docs": "/docs"
  }
}
```

### 3. Predict

```bash
POST /predict
Content-Type: application/json

{
  "instances": [
    {"image": "base64_encoded_image_string"}
  ],
  "parameters": {
    "confidence": 0.25,
    "return_annotated_image": true
  }
}
```

**Response:**

```json
{
  "predictions": [
    {
      "detections": [
        {
          "class_name": "person",
          "confidence": 0.92,
          "bbox": {
            "xmin": 100.5,
            "ymin": 50.2,
            "xmax": 300.8,
            "ymax": 450.6
          }
        }
      ],
      "detection_count": 1,
      "annotated_image": "base64_encoded_annotated_image"
    }
  ]
}
```

---

## ☁️ Cloud Run Deployment

### Using gcloud

```bash
# 1. Set variables
export PROJECT_ID=your-project-id
export REGION=us-central1

# 2. Build and push
gcloud builds submit --tag gcr.io/$PROJECT_ID/yolo-detector

# 3. Deploy
gcloud run deploy yolo-detector \
  --image gcr.io/$PROJECT_ID/yolo-detector \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --allow-unauthenticated \
  --set-env-vars MODEL_PATH=yolo11n.pt

# 4. Get URL
gcloud run services describe yolo-detector \
  --region $REGION \
  --format 'value(status.url)'
```

---

## ⚙️ Configuration

### Resource Requirements

**Recommended for Cloud Run:**

- **Memory**: 2Gi (minimum 1Gi)
- **CPU**: 2 cores
- **Timeout**: 300 seconds
- **Concurrency**: 80 (default)

**For custom models:**

- Increase memory to 4Gi or 8Gi
- May need more CPU cores

---

## 📊 Performance

### Optimization Tips

1. **Image Size**: Resize images before upload
2. **Confidence**: Higher threshold = faster
3. **Concurrency**: Adjust for traffic patterns
4. **Cold Start**: ~10-15 seconds (minimized with min instances)

---

## 🔐 Security

### Best Practices

1. **Authentication**: Add Cloud IAM for production
2. **Rate Limiting**: Use Cloud Armor or API Gateway
3. **Input Validation**: Already implemented with Pydantic
4. **CORS**: Configure if needed for web apps

---

## 💰 Cost Optimization

### Tips

1. **Min/Max Instances**: Set min=0 for low traffic
2. **Concurrency**: Increase to 80-100
3. **CPU Allocation**: Use "CPU always allocated" only if needed
4. **Region**: Choose closest to users
5. **Memory**: Start small, increase if needed

### Estimated Costs

``Example: 1000 requests/day, 500ms avg``

- Requests: ~$0.40/month
- CPU: ~$2.40/month
- Memory (2Gi): ~$2.40/month
- **Total**: ~$5/month

[Google Cloud Pricing Calculator](https://cloud.google.com/products/calculator)

---

## 🔗 Useful Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## 📧 Support

For backend issues:

- Check logs: ``gcloud run services logs read yolo-detector``
- Test locally with Docker first
- Verify model is loading correctly
- Check resource allocation (memory/CPU)

---

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0. See the LICENSE file for details.

## 🙏 Credits and Acknowledgments

### Technical Foundation

This deployment architecture is built upon the robust standards provided by **Ultralytics** for enterprise-grade computer vision. Specifically, the containerization strategy was informed by their official guide:

- **Source:** [Vertex AI Deployment with Docker](https://docs.ultralytics.com/guides/vertex-ai-deployment-with-docker/)
- **Organization:** [Ultralytics](https://ultralytics.com/)

### Educational Resources & Ecosystem

The successful implementation of this pipeline was made possible through the documentation and community insights from:

- **Core Libraries:** Official documentation of [YOLO](https://www.ultralytics.com/) and [FastApi](https://fastapi.tiangolo.com/).
- **Containerization:** Docker official best practices for Python-based Microservices.
- **Community:** Technical discussions and optimization tips from the GitHub community.

### Technical Statement

While this project follows the architectural patterns established by Ultralytics, **all code within this repository has been independently implemented, tested, and optimized by me.**

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
