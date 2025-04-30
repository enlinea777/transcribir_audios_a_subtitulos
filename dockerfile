FROM python:3.12-slim

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y ffmpeg python3-venv && rm -rf /var/lib/apt/lists/*

# Crea directorio de trabajo
WORKDIR /app

RUN python -m venv venv

# Establece el entorno para usar el Python del virtualenv
ENV PATH="/app/venv/bin:$PATH"

# Expone puerto
EXPOSE 8000

# Comando de arranque
#CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]

