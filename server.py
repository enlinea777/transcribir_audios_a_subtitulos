from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import whisper
import os
import shutil
import uuid

app = FastAPI()

# Cargar modelo al inicio
modelo = whisper.load_model("medium", device="cpu")

@app.post("/transcribir/")
async def transcribir(audio: UploadFile, nombre_salida: str = Form(default="salida")):
    temp_id = str(uuid.uuid4())
    archivo_temp = f"temp_{temp_id}.mp3"
    salida_srt = f"{nombre_salida}.srt"

    # Guardar archivo subido
    with open(archivo_temp, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Transcribir
    resultado = modelo.transcribe(archivo_temp, language="es", verbose=False)
    
    # Guardar como .srt
    writer = whisper.utils.get_writer("srt", ".")
    writer(resultado, nombre_salida)

    # Limpiar temporal
    os.remove(archivo_temp)

    # Retornar archivo SRT como descarga
    return FileResponse(salida_srt, filename=salida_srt, media_type="text/plain")
