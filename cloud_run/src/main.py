# FastAPI inference server
import sys
import os
from fastapi import FastAPI, HTTPException, status, Response, UploadFile, File
from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from app import is_model_ready, run_inference, get_image_from_bytes, get_bytes_from_image, get_annotated_image
import uvicorn
import base64
from loguru import logger

# Configurar logger
# Eliminar logger por defecto
logger.remove()
# Configurar el logger para output en consola (necesario para Cloud Run)
# - colorize: colorea la salida
# - format: formato personalizado del log
# - level: nivel mínimo de log (INFO)
# - serialize: no serializar a JSON
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>",
    level="INFO",
    serialize=False,
)
# Agrega logger a archivo local para debugging
# - rotation: rota el archivo cuando alcanza 1MB
# - level: DEBUG (más detallado que INFO)
# - compression: comprime los logs rotados en ZIP
logger.add("log.log", rotation="1 MB", level="DEBUG", compression="zip")

# Crea la instancia principal de FastAPI con metadatos:
# - título, versión y descripción de la API
# - URLs para documentación automática
app = FastAPI(
    title="YOLO11 Inference Server", 
    version="1.0.0",
    description="**Detección de cereza de café usando YOLO11**",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Lee variables de entorno para configuración en Cloud Run
# Valores por defecto si no están definidas las variables
PORT = int(os.getenv("PORT", "8000"))
AIP_HEALTH_ROUTE = os.getenv("AIP_HEALTH_ROUTE", "/health")
AIP_PREDICT_ROUTE = os.getenv("AIP_PREDICT_ROUTE", "/predict")

# Define límite máximo de tamaño para requests (10MB)
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB in bytes

# Modelos pydantic para request/response
class Detection(BaseModel):   #Define una deteccion individual
    class_name: str           # Ej: "cereza_madura"
    confidence: float         # Ej: 0.95 (95% de confianza)
    bbox: Dict[str, float]    # Ej: {"xmin": 10, "ymin": 20, "xmax": 50, "ymax": 60}

class PredictionResult(BaseModel):    #Define el resultado completo de una prediccion
    detections: List[Detection]       # Lista de detecciones
    detection_count: int              # Cantidad total de detecciones
    annotated_image: Optional[str] = None  # Imagen anotada en base64 (opcional)

class PredictionRequest(BaseModel):             #Lo que el cliente envia
    instances: List[Dict[str, Any]]           # Lista de imágenes/instancias
    parameters: Optional[Dict[str, Any]] = None  # Parámetros opcionales

class PredictionResponse(BaseModel):    #Lo que la API devuelve
    predictions: List[PredictionResult]  # Lista de resultados por cada instancia

# Endpoint de health check que:
# - Verifica si el modelo está listo
# - Retorna 503 si no está listo
# - Retorna 200 con status "healthy" si está listo
@app.get(AIP_HEALTH_ROUTE, status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint."""
    if not is_model_ready():
        raise HTTPException(status_code=503, detail="Model not ready")
    return {"status": "healthy"}

# Endpoint raíz que muestra información básica de la API y los endpoints disponibles
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "YOLO11 Inference Server",
        "version": "1.0.0",
        "endpoints": {
            "health": AIP_HEALTH_ROUTE,
            "predict": AIP_PREDICT_ROUTE,
            "predict_image": "/predict-image",
            "docs": "/docs"
        }
    }


@app.post(AIP_PREDICT_ROUTE, response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Prediction endpoint."""
    try:
        predictions = [] # Lista para almacenar resultados de todas las instancias

        # Procesa cada instancia en la request
        for instance in request.instances:
            if isinstance(instance, dict):
                if "image" in instance:
                    # Decodifica la imagen de base64
                    image_data = base64.b64decode(instance["image"])
                    # Convierte bytes a imagen PIL/OpenCV
                    input_image = get_image_from_bytes(image_data)
                else:
                    raise HTTPException(status_code=400, detail="Instance must contain 'image' field")
            else:
                raise HTTPException(status_code=400, detail="Invalid instance format")

            # Extrae parámetros opcionales o usa valores por defecto
            parameters = request.parameters or {}
            confidence_threshold = parameters.get("confidence", 0.5)
            return_annotated_image = parameters.get("return_annotated_image", True)

            # Ejecuta inferencia con el modelo YOLO11
            result = run_inference(input_image, confidence_threshold=confidence_threshold)
            detections_list = result["detections"]

            # Formatea las detecciones para la respuesta
            detections = []
            for detection in detections_list:
                formatted_detection = {
                    "class_name": detection["name"],
                    "confidence": detection["confidence"],
                    "bbox": {
                        "xmin": detection["xmin"],
                        "ymin": detection["ymin"],
                        "xmax": detection["xmax"],
                        "ymax": detection["ymax"],
                    },
                }
                detections.append(formatted_detection)

            # Construye el resultado de predicción
            prediction = {
                "detections": detections, 
                "detection_count": len(detections),
                "annotated_image": None
                }

            # Genera imagen anotada si se solicita y hay detecciones
            if return_annotated_image and result["results"]:
                annotated_image = get_annotated_image(result["results"])
                img_bytes = get_bytes_from_image(annotated_image)
                # Codifica la imagen anotada en base64 para la respuesta
                prediction["annotated_image"] = base64.b64encode(img_bytes).decode("utf-8")

            predictions.append(prediction)
        # Log del procesamiento
        logger.info(
            f"Processed {len(request.instances)} instances, found {sum(len(p['detections']) for p in predictions)} total detections"
        )

        return PredictionResponse(predictions=predictions)

    except HTTPException:
        # Re-lanza HTTPExceptions sin modificar
        raise
    except Exception as e:
        # Maneja errores inesperados con log y response 500
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


if __name__ == "__main__":
    # Inicialización del servidor
    logger.info(f"Starting server on port {PORT}")
    logger.info(f"Health check route: {AIP_HEALTH_ROUTE}")
    logger.info(f"Predict route: {AIP_PREDICT_ROUTE}")
    # Inicia el servidor uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)