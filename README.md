API usando docker para poder hacer transcripciones de mp3 a SRT subtitulos usando IA
modelo whisper por ahora solo ocupo la CPU y ocupa 3G de ram.


-Primero hacer probas locales

crear entorno local
```bash
python -m venv venv
```

activar el entorno
```bash
source venv/bin/activate
```

ejecutar las instalaciones
```bash
pip install -r requirements.txt
```


probar
```bash
uvicorn whisper_server:app --host 0.0.0.0 --port 8000
```

Prueba con curl una ves que anda ok
```bash
curl -F "audio=@salida.mp3" -F "nombre_salida=salida" http://xeon:8000/transcribir/ -o mi_subtitulo.srt
```

con esto se optiene el resultado  de la transcripcion 


ffmpeg -i video.mp4 -i subtitulos.srt -c copy -c:s mov_text video_con_subs.mp4


ffmpeg -i video.mp4 -vf subtitles=subtitulos.srt video_subtitulado.mp4
