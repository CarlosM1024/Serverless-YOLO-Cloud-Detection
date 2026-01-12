# 🔍 YOLO Object Detector

> Real-time object detection using YOLO11n with Flutter mobile app, Cloud Run backend, and Firebase integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flutter](https://img.shields.io/badge/Flutter-3.0+-blue.svg)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)
[![YOLO](https://img.shields.io/badge/YOLO-11n-red.svg)](https://github.com/ultralytics/ultralytics)

---

## 📖 About

This project is a simplified version of my Master's thesis on coffee cherry maturity detection, adapted for general object detection using the pre-trained YOLO11n model (COCO dataset).

The system demonstrates a complete serverless architecture for real-time AI inference, combining:

- **Flutter** mobile app for image capture
- **Firebase** for storage and real-time updates
- **Cloud Run** for scalable YOLO inference
- **Cloud Functions** for orchestration

---

## 📸 Demo

<div align="center">
  <img src="video/test_video.gif" alt="Complete Demo" width="350"/>
  <p><i>From image selection to detection results</i></p>
</div>

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Flutter App    │
│  📱 Mobile      │
└────────┬────────┘
         │ 1. Upload image
         ↓
┌─────────────────────────┐
│  Firebase Storage       │
│  📦 uploads/           │
└────────┬────────────────┘
         │ 2. Trigger
         ↓
┌─────────────────────────┐
│  Cloud Function         │
│  ⚡ Python             │
│  - Download image       │
│  - Call Cloud Run       │
│  - Save results         │
└────────┬────────────────┘
         │ 3. POST /predict
         ↓
┌─────────────────────────┐
│  Cloud Run              │
│  🐳 Docker + FastAPI   │
│  - YOLO11n inference    │
│  - Object detection     │
│  - Return annotations   │
└────────┬────────────────┘
         │ 4. Results
         ↓
┌─────────────────────────┐
│  Firebase Storage       │
│  💾 results/           │
│  Firestore (metadata)   │
└────────┬────────────────┘
         │ 5. Real-time listener
         ↓
┌─────────────────┐
│  Flutter App    │
│  📱 Show result │
└─────────────────┘
```

---

## ✨ Features

- 📸 **Camera & Gallery** - Capture or select images
- 🤖 **YOLO11n Detection** - State-of-the-art object detection (80 COCO classes)
- ⚡ **Real-time Processing** - Serverless architecture with Cloud Run
- 🔥 **Firebase Integration** - Storage, Firestore, and Cloud Functions
- 📱 **Cross-platform** - Flutter app works on iOS and Android
- 🐳 **Containerized** - Docker deployment for consistency
- 📊 **Detailed Results** - Bounding boxes, confidence scores, and class labels

### Detected Object Classes

The YOLO11n model can detect 80 different objects including:

- **People**: person
- **Vehicles**: car, truck, bus, motorcycle, bicycle
- **Animals**: dog, cat, horse, bird, etc.
- **Objects**: chair, table, laptop, phone, book, etc.
- [Full COCO dataset classes](https://tech.amikelive.com/node-718/what-object-categories-labels-are-in-coco-dataset/)

---

## 🚀 Quick Start

### Prerequisites

- **Flutter SDK** (3.0+)
- **Python** (3.11+)
- **Docker**
- **Google Cloud SDK** (`gcloud`)
- **Firebase CLI** (`firebase-tools`)
- **Firebase Project** with Firestore, Storage, and Functions enabled

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/CarlosM1024/Object_Detection_Flutter_YOLO.git
   cd Object_Detection_Flutter_YOLO
   ```

2. **Deploy Backend (Cloud Run).**

   See [cloud_run/README.md](https://github.com/CarlosM1024/Object_Detection_Flutter_YOLO/tree/main/cloud_run) for detailed instructions and run ``main.py``.

3. **Deploy Cloud Functions.**

   Update CLOUD_RUN_URL and run ``main.py``, located in [Firebase_functions/](https://github.com/CarlosM1024/Object_Detection_Flutter_YOLO/tree/main/Firebase_functions)

4. **Setup Mobile App**

   Add your Firebase config files in [mobile_app/](hhttps://github.com/CarlosM1024/Object_Detection_Flutter_YOLO/tree/main/mobile_app)

   ```bash
   cd mobile_app
   flutter pub get
   flutter run
   ```

For detailed setup instructions, see the README in each folder.

---

## 📁 Project Structure

```text
Object_Detection_Flutter_YOLO/
│
├── README.md                 # This file
├── LICENSE                   # MIT License
│
├── mobile/                   # 📱 Flutter Mobile App
│   ├── README.md
│   ├── lib/
│   │   ├── main.dart
│   │   ├── detector_screen.dart
│   │   └── firebase_service.dart
│   └── pubspec.yaml
│
├── cloud_run/                # 🐳 Cloud Run Backend
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   ├── main.py           # FastAPI server
│   │   └── app.py            # YOLO inference logic
│   └── models/
│
└── Firebase_functions/       # ⚡ Cloud Functions
    ├── README.md
    ├── main.py
    ├── requirements.txt
    └── firebase.json
```

---

## 🛠️ Technology Stack

### Mobile

- **Flutter** - Cross-platform mobile framework
- **Firebase SDK** - Storage, Firestore, Auth

### Backend

- **Python 3.12** - Programming language
- **FastAPI** - Modern web framework
- **Ultralytics YOLO11n** - Object detection model
- **Docker** - Containerization

### Infrastructure

- **Google Cloud Run** - Serverless container platform
- **Firebase Cloud Functions** - Event-driven functions
- **Firebase Storage** - Image storage
- **Firebase Firestore** - Real-time database

---

## 📊 Performance

- **Inference Time**: ~200-500ms per image (depends on image size)
- **Model Size**: 6.2 MB (YOLO11n)
- **Supported Image Formats**: JPG, JPEG, PNG
- **Max Image Size**: 10 MB
- **Detection Classes**: 80 (COCO dataset)
- **Default Confidence Threshold**: 0.25

---

## 🔐 Security & Privacy

- Anonymous authentication enabled by default
- Storage and Firestore security rules configured
- Images stored in user-specific paths
- No personal data collection
- All processing done server-side

---

## 🧪 Testing

```bash
# Test Cloud Run health
curl https://your-cloud-run-url.run.app/health

# Test with an image
python test_cloudrun.py path/to/image.jpg

# Monitor logs
firebase functions:log --only process_object_detection
gcloud run services logs read yolo-detector --limit 50
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎓 Academic Context

This project is a simplified, open-source version of my [article](https://doi.org/10.32854/rxr1f675) and master's thesis on detecting coffee cherry maturity using computer vision. The original thesis work involved:

- Custom YOLO model training for coffee cherry classification
- Field deployment in coffee plantations
- Agricultural data analysis and yield prediction

This public version uses the pre-trained YOLO11n model for general object detection to make it accessible and useful for the broader community.

---

## 🙏 Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - Object detection framework
- [Flutter Team](https://flutter.dev/) - Mobile framework
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Firebase](https://firebase.google.com/) - Backend services

---

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
