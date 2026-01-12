# Definir la imagen base
FROM ultralytics/ultralytics:8.3.189-cpu
#Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/app/models/best.onnx
#Instalar dependencias del sistema
RUN pip install --no-cache-dir fastapi[all] uvicorn[standard] loguru onnxruntime
#Definir el carpeta de trabajo
WORKDIR /app
# Crear carpeta para logs
RUN mkdir -p /app/models /app/logs
# Copiar archivos de configuración y codigos
COPY src/ ./src/
COPY pyproject.toml ./
# Copiar modelos
COPY models/ /app/models/
# Instalar dependencias desde pyproject.toml
RUN pip install --no-cache-dir -e .
# Crear usuario no-root y carpeta para almacenar archivos de log
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser
# Establecer PYTHONPATH
ENV PYTHONPATH=/app/src
#Definir el puerto expuesto
EXPOSE 8000
#Especifica el comando predeterminado al ejecutar
CMD ["python", "src/main.py"]