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

