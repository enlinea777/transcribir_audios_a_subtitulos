from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import whisper
import os
import shutil
import uuid
import re


app = FastAPI()

# Cargar modelo al inicio   small turbo medium large
modelo = whisper.load_model("medium", device="cpu")


def generar_srt_controlado_con_puntuacion(resultado, nombre_base, palabras_por_subtitulo=3):
    """Genera un archivo SRT controlando palabras y separando por comas y puntos."""
    segmentos_srt = []
    contador_subtitulo = 1

    for segmento in resultado["segments"]:
        buffer_palabras = []
        tiempo_inicio_subtitulo = None

        for palabra_info in segmento["words"]:
            palabra_original = palabra_info["word"]
            palabra_limpia = re.sub(r'[.,]', '', palabra_original)  # Eliminar comas y puntos temporalmente
            tiempo_inicio_palabra = palabra_info["start"]
            tiempo_fin_palabra = palabra_info["end"]

            if not buffer_palabras:
                tiempo_inicio_subtitulo = tiempo_inicio_palabra

            buffer_palabras.append((palabra_original, tiempo_inicio_palabra, tiempo_fin_palabra))

            # Verificar límite de palabras o presencia de coma o punto en la palabra original
            if len(buffer_palabras) >= palabras_por_subtitulo or "," in palabra_original or "." in palabra_original:
                tiempo_fin_subtitulo = buffer_palabras[-1][2]
                texto_subtitulo = " ".join([p[0] for p in buffer_palabras]).strip()
                texto_subtitulo_limpio = re.sub(r'[.,]', '', texto_subtitulo) # Eliminar al final
                segmentos_srt.append(f"{contador_subtitulo}\n{formatear_tiempo(tiempo_inicio_subtitulo)} --> {formatear_tiempo(tiempo_fin_subtitulo)}\n{texto_subtitulo_limpio}\n")
                contador_subtitulo += 1
                buffer_palabras = []
                tiempo_inicio_subtitulo = None

        # Manejar palabras restantes al final del segmento
        if buffer_palabras:
            tiempo_fin_subtitulo = buffer_palabras[-1][2]
            texto_subtitulo = " ".join([p[0] for p in buffer_palabras]).strip()
            texto_subtitulo_limpio = re.sub(r'[.,]', '', texto_subtitulo)
            segmentos_srt.append(f"{contador_subtitulo}\n{formatear_tiempo(tiempo_inicio_subtitulo)} --> {formatear_tiempo(tiempo_fin_subtitulo)}\n{texto_subtitulo_limpio}\n")
            contador_subtitulo += 1

    nombre_srt = f"{nombre_base}_puntuacion.srt"
    with open(nombre_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(segmentos_srt))
    return nombre_srt

def generar_srt_controlado(resultado, nombre_base, palabras_por_subtitulo=3):
    """Genera un archivo SRT con un número controlado de palabras por subtítulo."""
    segmentos_srt = []
    contador_subtitulo = 1
    tiempo_inicio_subtitulo = None
    palabras_subtitulo = []

    for segmento in resultado["segments"]:
        for palabra_info in segmento["words"]:
            palabra = palabra_info["word"]
            tiempo_inicio = palabra_info["start"]
            tiempo_fin = palabra_info["end"]

            if not palabras_subtitulo:
                tiempo_inicio_subtitulo = tiempo_inicio

            palabras_subtitulo.append((palabra, tiempo_inicio, tiempo_fin))

            if len(palabras_subtitulo) >= palabras_por_subtitulo:
                tiempo_fin_subtitulo = palabras_subtitulo[-1][2]
                texto_subtitulo = " ".join([p[0] for p in palabras_subtitulo])
                segmentos_srt.append(f"{contador_subtitulo}\n{formatear_tiempo(tiempo_inicio_subtitulo)} --> {formatear_tiempo(tiempo_fin_subtitulo)}\n{texto_subtitulo}\n")
                contador_subtitulo += 1
                palabras_subtitulo = []
                tiempo_inicio_subtitulo = None

    # Manejar las palabras restantes si no forman un grupo completo
    if palabras_subtitulo:
        tiempo_fin_subtitulo = palabras_subtitulo[-1][2]
        texto_subtitulo = " ".join([p[0] for p in palabras_subtitulo])
        segmentos_srt.append(f"{contador_subtitulo}\n{formatear_tiempo(tiempo_inicio_subtitulo)} --> {formatear_tiempo(tiempo_fin_subtitulo)}\n{texto_subtitulo}\n")

    nombre_srt = f"{nombre_base}_controlado.srt"
    with open(nombre_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(segmentos_srt))
    return nombre_srt


def generar_srt_controlado_con_comas(resultado, nombre_base, palabras_por_subtitulo=3):
    """Genera un archivo SRT controlando palabras y separando por comas."""
    segmentos_srt = []
    contador_subtitulo = 1

    for segmento in resultado["segments"]:
        buffer_palabras = []
        tiempo_inicio_subtitulo = None

        for palabra_info in segmento["words"]:
            palabra = palabra_info["word"]
            tiempo_inicio_palabra = palabra_info["start"]
            tiempo_fin_palabra = palabra_info["end"]

            if not buffer_palabras:
                tiempo_inicio_subtitulo = tiempo_inicio_palabra

            buffer_palabras.append((palabra, tiempo_inicio_palabra, tiempo_fin_palabra))

            # Verificar si se alcanza el límite de palabras o si la palabra actual contiene una coma
            if len(buffer_palabras) >= palabras_por_subtitulo or "," in palabra:
                tiempo_fin_subtitulo = buffer_palabras[-1][2]
                texto_subtitulo = " ".join([p[0] for p in buffer_palabras])
                segmentos_srt.append(f"{contador_subtitulo}\n{formatear_tiempo(tiempo_inicio_subtitulo)} --> {formatear_tiempo(tiempo_fin_subtitulo)}\n{texto_subtitulo.strip()}\n")
                contador_subtitulo += 1
                buffer_palabras = []
                tiempo_inicio_subtitulo = None

        # Manejar las palabras restantes al final del segmento
        if buffer_palabras:
            tiempo_fin_subtitulo = buffer_palabras[-1][2]
            texto_subtitulo = " ".join([p[0] for p in buffer_palabras])
            segmentos_srt.append(f"{contador_subtitulo}\n{formatear_tiempo(tiempo_inicio_subtitulo)} --> {formatear_tiempo(tiempo_fin_subtitulo)}\n{texto_subtitulo.strip()}\n")
            contador_subtitulo += 1

    nombre_srt = f"{nombre_base}_comas.srt"
    with open(nombre_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(segmentos_srt))
    return nombre_srt


def formatear_tiempo(tiempo_segundos):
    """Formatea segundos a formato SRT (HH:MM:SS,ms)."""
    horas = int(tiempo_segundos // 3600)
    minutos = int((tiempo_segundos % 3600) // 60)
    segundos = int(tiempo_segundos % 60)
    milisegundos = int((tiempo_segundos - int(tiempo_segundos)) * 1000)
    return f"{horas:02d}:{minutos:02d}:{segundos:02d},{milisegundos:03d}"



@app.post("/transcribir/")
async def transcribir(audio: UploadFile, nombre_salida: str = Form(default="salida"),palabras_por_linea: int = Form(default=4)):
    temp_id = str(uuid.uuid4())
    archivo_temp = f"temp_{temp_id}.mp3"
    salida_srt = f"{nombre_salida}.srt"

    # Guardar archivo subido
    with open(archivo_temp, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    # Transcribir
    resultado = modelo.transcribe(archivo_temp, language="es",task="transcribe", 
                        word_timestamps=True,
                        condition_on_previous_text=True,
                        initial_prompt="",
                        no_speech_threshold=0.6,
                        logprob_threshold=-1.0,
                        compression_ratio_threshold=2.4,
                        temperature=0.0,
                        verbose=True,
                        fp16=False)
    
    
    #nombre_srt_controlado = generar_srt_controlado(resultado, nombre_salida, palabras_por_linea)
    #nombre_srt_controlado = generar_srt_controlado_con_comas(resultado, nombre_salida, palabras_por_linea)
    nombre_srt_controlado = generar_srt_controlado_con_puntuacion(resultado, nombre_salida, palabras_por_linea)
    

    # Limpiar temporal
    os.remove(archivo_temp)

    # Retornar archivo SRT controlado como descarga
    return FileResponse(nombre_srt_controlado, filename=f"{nombre_salida}_controlado.srt", media_type="text/plain")

    '''

    # Guardar como .srt
    writer = whisper.utils.get_writer("srt", ".")
    writer(resultado, nombre_salida)

    # Limpiar temporal
    os.remove(archivo_temp)

    # Retornar archivo SRT como descarga
    return FileResponse(salida_srt, filename=salida_srt, media_type="text/plain")
    '''




    


