"""
Firebase Cloud Function (Python) para YOLO Object Detection
"""

from firebase_functions import storage_fn
from firebase_admin import initialize_app, storage, firestore
import requests
import io
import logging
import base64
import time

# Initialize Firebase Admin
app = initialize_app()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('yolo_detector')

# IMPORTANTE: Actualiza con tu URL de Cloud Run
CLOUD_RUN_URL = "URL_DE_TU_CLOUD_RUN"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


@storage_fn.on_object_finalized()
def process_object_detection(event: storage_fn.CloudEvent[storage_fn.StorageObjectData]):
    """
    Triggered when a file is uploaded to Firebase Storage.
    Processes images in 'uploads/' folder with YOLO object detection.
    """
    file_path = event.data.name
    bucket_name = event.data.bucket
    
    logger.info(f"📁 File detected: {file_path}")
    
    # === VALIDATION ===
    
    # Only process files in 'uploads/' folder
    if not file_path.startswith('uploads/'):
        logger.info(f"Skipping file (not in uploads/): {file_path}")
        return
    
    # Only process image files
    if not file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        logger.info(f"Skipping file (not an image): {file_path}")
        return
    
    # Extract document ID from filename
    doc_id = file_path.replace('uploads/', '').rsplit('.', 1)[0]
    
    # Check if already processed (avoid duplicates)
    db = firestore.client()
    doc_ref = db.collection('detection_results').document(doc_id)
    doc = doc_ref.get()
    
    if doc.exists and doc.to_dict().get('status') == 'completed':
        logger.info(f"Already processed: {doc_id}")
        return
    
    logger.info(f"Processing: {file_path} (ID: {doc_id})")
    
    # === DOWNLOAD IMAGE ===
    
    bucket = storage.bucket(bucket_name)
    blob = bucket.blob(file_path)
    
    try:
        # Download image to memory
        image_bytes = io.BytesIO()
        blob.download_to_file(image_bytes)
        image_bytes.seek(0)
        image_data = image_bytes.getvalue()
        
        image_size_kb = len(image_data) / 1024
        logger.info(f"Downloaded image: {image_size_kb:.2f} KB")
        
        if len(image_data) == 0:
            raise Exception("Downloaded image is empty")
        
        # === CALL CLOUD RUN WITH RETRIES ===
        
        detections_list = []
        detection_count = 0
        annotated_image_base64 = None
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES} - Calling Cloud Run...")
                
                # Encode image to base64
                image_base64 = base64.b64encode(image_data).decode('utf-8')
                
                # Make request to Cloud Run
                response = requests.post(
                    CLOUD_RUN_URL,
                    json={
                        'instances': [{'image': image_base64}],
                        'parameters': {
                            'confidence': 0.25,
                            'return_annotated_image': True
                        }
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=120
                )
                
                logger.info(f"Response status: {response.status_code}")
                
                # Check if successful
                if response.status_code == 200:
                    json_data = response.json()
                    predictions = json_data.get('predictions', [])
                    
                    if predictions:
                        prediction = predictions[0]
                        detections = prediction.get('detections', [])
                        detection_count = prediction.get('detection_count', 0)
                        annotated_image_base64 = prediction.get('annotated_image')
                        
                        logger.info(f"Found {detection_count} objects")
                        
                        # Count objects by class
                        class_counts = {}
                        detections_list = []
                        
                        for detection in detections:
                            class_name = detection.get('class_name', 'unknown')
                            confidence = detection.get('confidence', 0.0)
                            bbox = detection.get('bbox', {})
                            
                            # Count by class
                            class_counts[class_name] = class_counts.get(class_name, 0) + 1
                            
                            # Store detection 
                            detections_list.append({
                                'class_name': class_name,  
                                'confidence': confidence,
                                'bbox': bbox
                            })
                        
                        logger.info(f"Objects by class: {class_counts}")
                    else:
                        logger.warning("No predictions returned")
                    
                    # Success - break retry loop
                    break
                
                else:
                    error_msg = f"Cloud Run error: {response.status_code} - {response.text[:500]}"
                    logger.error(f"{error_msg}")
                    
                    if attempt == MAX_RETRIES - 1:
                        raise Exception(f"Failed after {MAX_RETRIES} attempts. {error_msg}")
            
            except requests.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt == MAX_RETRIES - 1:
                    raise Exception(f"Timeout after {MAX_RETRIES} attempts")
            
            except requests.exceptions.RequestException as e:
                logger.warning(f"Connection error: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
            
            # Wait before retry (exponential backoff)
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_DELAY * (2 ** attempt)
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        # === SAVE ANNOTATED IMAGE ===
        
        processed_path = ''
        
        if annotated_image_base64 and detection_count > 0:
            # Save to results/ folder
            file_extension = file_path.split('.')[-1]
            processed_path = f"results/{doc_id}.{file_extension}"
            result_blob = bucket.blob(processed_path)
            
            # Decode base64 and upload
            annotated_image_bytes = base64.b64decode(annotated_image_base64)
            result_blob.upload_from_string(
                annotated_image_bytes,
                content_type='image/jpeg'
            )
            
            logger.info(f"Saved annotated image to: {processed_path}")
        else:
            logger.info(" No detections - skipping annotated image")
        
        # === UPDATE FIRESTORE ===
        
        update_data = {
            'original': file_path,
            'processed': processed_path,
            'detections': detections_list,
            'detection_count': detection_count,
            'status': 'completed',
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(update_data)
        
        logger.info(f"Success! Document updated: {doc_id}")
        logger.info(f"Total detections: {detection_count}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing {file_path}: {error_msg}")
        
        # Update Firestore with error
        doc_ref.set({
            'original': file_path,
            'processed': '',
            'detections': [],
            'detection_count': 0,
            'status': 'error',
            'error': error_msg,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # Re-raise to mark function as failed
        raise
