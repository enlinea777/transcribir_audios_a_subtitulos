#!/archivos2/transcripcion_vodeo_texto/venv/bin/python

import whisper
import os
import sys
import math

from tqdm import tqdm
import tempfile

# Ruta del archivo a transcribir
archivo = sys.argv[1] if len(sys.argv) > 1 else "audio.mp3"
salida = sys.argv[2] if len(sys.argv) > 2 else "salida"
# Cargar modelo Whisper
modelo = whisper.load_model("medium", device="cpu")

# Obtener duración del audio
import subprocess
duracion = float(subprocess.check_output([
    "ffprobe", "-v", "error", "-show_entries",
    "format=duration", "-of",
    "default=noprint_wrappers=1:nokey=1", archivo
]).decode().strip())

# Transcripción con barra de progreso simplificada
class Progreso:
    def __init__(self, total_s):
        self.total = total_s
        self.last_percent = -1

    def actualizar(self, segmento):
        start = segmento["start"]
        percent = int((start / self.total) * 100)
        if percent != self.last_percent:
            print(f"{percent}%", flush=True)
            self.last_percent = percent

progreso = Progreso(duracion)

result = modelo.transcribe(archivo, language="es", verbose=False, task="transcribe", condition_on_previous_text=False, temperature=0.0, no_speech_threshold=0.5, suppress_tokens=[])
for segmento in result["segments"]:
    progreso.actualizar(segmento)


# Guardar como .srt
import whisper.utils
writer = whisper.utils.get_writer("srt", ".")
writer(result, salida)


print("✅ Transcripción completada: salida.srt")
