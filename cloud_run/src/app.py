# Core YOLO11 inference logic
from ultralytics import YOLO
from PIL import Image
import io
import os
from typing import Dict, Any
import cv2
import numpy as np

# Inicialización del modelo
model_yolo = None # Variable global que almacenará el modelo YOLO
_model_ready = False # Bandera que indica si el modelo está listo para usar


def _initialize_model():
    """Inicializar el modelo YOLO."""
    global model_yolo, _model_ready  # Permite modificar las variables globales

    try:
        # Obtener la ruta del modelo desde variables de entorno, o usar ruta por defecto
        model_path = os.getenv("MODEL_PATH", "models/best.onnx")

        # Verificar si existe un modelo personalizado en la ruta especificada
        if os.path.exists(model_path):
            print(f"ONNX model loaded from {model_path}")
            # Cargar modelo YOLO para detección
            model_yolo = YOLO(model_path, task="detect")
            
        else:
           # Cargar modelo pre-entrenado YOLO11n
            print("Pre-trained YOLO11n model loaded")
            model_yolo = YOLO("yolo11n.pt")
        
        # Marcar el modelo como listo si se cargó correctamente
        _model_ready = True
        print("Modelo iniciado correctamente.")

    except Exception as e:
        # Manejar cualquier error durante la inicialización
        print(f"Error al inicializar modelo YOLO: {e}")
        _model_ready = False # Marcar como no listo
        model_yolo = None # Limpiar referencia al modelo

# Ejecutar la inicialización al importar el módulo
_initialize_model()

def is_model_ready() -> bool:
    # Verificar que ambas condiciones sean verdaderas:
    # - La bandera _model_ready está en True
    # - La variable model_yolo no es None
    return _model_ready and model_yolo is not None

def get_image_from_bytes(binary_image: bytes) -> Image.Image:
    """Convertir imagen de bytes a formato PIL RGB."""
    # Abrir la imagen y convertir a formato RGB
    input_image = Image.open(io.BytesIO(binary_image)).convert("RGB")
    return input_image

def get_bytes_from_image(image: Image.Image) -> bytes:
    """Convertir formato imagen PIL a bytes."""
    # Crear un buffer en memoria para almacenar la imagen
    return_image = io.BytesIO()
    # Guardar la imagen en el buffer en formato JPEG con calidad 85%
    image.save(return_image, format="JPEG", quality=85)
    # Mover el puntero al inicio del buffer para lectura
    return_image.seek(0)
    # Obtener los bytes del buffer
    return return_image.getvalue()

def run_inference(input_image: Image.Image, confidence_threshold: float = 0.5) -> Dict[str, Any]:
    """Ejecutar inferencia en una imagen usando el modelo YOLO11."""
    global model_yolo # Referencia a la variable global del modelo

    # Verificar si el modelo esta listo
    if not is_model_ready():
        print("Model not ready for inference")
        # Retornar estructura vacía si el modelo no está listo
        return {"detections": [], "results": None}

    try:
        # Ejecutar predicción con parámetros específicos:
        results = model_yolo.predict(
            imgsz=640,           # Tamaño de imagen
            source=input_image,  # Imagen de entrada
            conf=confidence_threshold,  # Umbral de confianza
            save=False,          # No guardar imágenes automáticamente
            augment=False,       # No usar aumentación de datos
            verbose=False        # No mostrar output verbose en consola
        )

        # Extract detections (bounding boxes, class names, and confidences)
        detections = [] # Lista para almacenar todas las detecciones
        if results and len(results) > 0: # Verificar que hay resultados
            result = results[0] # Tomar el primer resultado (solo una imagen)
            if result.boxes is not None and len(result.boxes.xyxy) > 0:
                boxes = result.boxes # Acceder a las cajas delimitadoras

                # Convertir tensores de PyTorch a arrays de numpy para procesamiento
                xyxy = boxes.xyxy.cpu().numpy()  # Coordenadas [xmin, ymin, xmax, ymax]
                conf = boxes.conf.cpu().numpy()  # Niveles de confianza
                cls = boxes.cls.cpu().numpy().astype(int)  # Clases (convertidas a enteros)

                # Crear diccionarios con la información de cada detección
                for i in range(len(xyxy)):
                    detection = {
                        "xmin": float(xyxy[i][0]),  # Coordenada x mínima
                        "ymin": float(xyxy[i][1]),  # Coordenada y mínima
                        "xmax": float(xyxy[i][2]),  # Coordenada x máxima
                        "ymax": float(xyxy[i][3]),  # Coordenada y máxima
                        "confidence": float(conf[i]),  # Confianza de la detección
                        "class": int(cls[i]),  # ID de la clase
                        # Obtener nombre de la clase del diccionario de nombres del modelo
                        "name": model_yolo.names.get(int(cls[i]), f"class_{int(cls[i])}"),
                    }
                    detections.append(detection)  # Agregar detección a la lista
        # Retornar resultados estructurados
        return {
            "detections": detections,  # Lista de detecciones formateadas
            "results": results,        # Resultados brutos para anotaciones posteriores
        }
    except Exception as e:
        # Retornar estructura vacía en caso de error
        print(f"Error in YOLO detection: {e}")
        return {"detections": [], "results": None}

def get_annotated_image ( results : list ) -> Image . Image :
    " Obtener imagen anotada usando metodo plot de Ultralytics . "
    if not results or len ( results ) == 0:
        raise ValueError ( " Sin resultados para la anotacion " )
    result = results [0] # Tomar el primer resultado
    # Siempre obtener como numpy array y convertir BGR to RGB
    # Usar el metodo plot () de Ultralytics que devuelve imagen anotada en formato BGR
    annotated_img_bgr = result . plot () # Esto devuelve BGR (formato OpenCV )
    # Convertir de BGR a RGB ( formato PIL )
    annotated_img_rgb = cv2 . cvtColor ( annotated_img_bgr , cv2.COLOR_BGR2RGB )
    # Convertir array de numpy a imagen PIL
    return Image . fromarray ( annotated_img_rgb )