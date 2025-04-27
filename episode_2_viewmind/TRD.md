# Documento de Requerimientos Técnicos (TRD)

**Proyecto:** `autocontent_podcast`

**Episodio:** `episode_2_viewmind`

**Objetivo:** Automatizar la creación de cinco posts para LinkedIn en inglés, dirigidos a una audiencia profesional interesada en neurotecnología, a partir de los archivos brutos del podcast.

---

## 1  Alcance
Este TRD cubre el flujo de trabajo completo desde los archivos de audio brutos y notas de preproducción hasta los archivos Markdown finales con posts para LinkedIn. Especifica la estructura de directorios, herramientas, scripts, variables de entorno y comandos de ejecución.

---

## 2  Prerrequisitos

- **OS**: Linux/macOS/Windows (compatible con PowerShell, CMD o bash)
- **Python**: ≥ 3.8
- **ffmpeg**: Última versión estable (preprocesamiento de audio)
- **Git**: Repositorio ya inicializado
- **Cuenta OpenRouter**: Para emparejar preguntas y respuestas

Instalar dependencias Python en un entorno virtual:
```bash
python -m venv .venv
# O si prefieres usar el nombre del repositorio:
# python -m venv autocontent
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

# Actualizar pip y wheel (funciona igual en Windows y Linux/macOS)
pip install --upgrade pip wheel
# Instalar dependencias desde requirements.txt (funciona igual en Windows y Linux/macOS)
pip install -r requirements.txt
```

Crear archivo `.env` en la raíz del repositorio con:
```dotenv
OPENROUTER_API_KEY="sk-or-..."
```

---

## 3  Estructura de Directorios
```
autocontent_podcast/
├── episode_2_viewmind/
│   ├── raw/                 # Assets brutos inmutables
│   │   ├── guest.mp3
│   │   ├── host.mp3
│   │   └── preproduction.txt
│   ├── processed/           # Archivos intermedios generados
│   ├── linkedin_posts/      # Resultados finales (Markdown)
│   └── scripts/             # Scripts de Python
└── README.md
```

> **Convención:** Todos los paths de scripts son relativos al directorio del episodio. Cada script acepta argumentos `--input` y `--output` para reutilización en futuros episodios.

---

## 4  Flujo de Trabajo Paso a Paso

### 4.1  Organizar assets brutos
1. Crear subdirectorios si no existen:
   ```bash
   mkdir -p episode_2_viewmind/{raw,processed,linkedin_posts,scripts}
   ```
2. Mover archivos:
   ```bash
   mv episode_2_viewmind/guest.mp3 episode_2_viewmind/raw/
   mv episode_2_viewmind/host.mp3 episode_2_viewmind/raw/
   mv episode_2_viewmind/preproduction.txt episode_2_viewmind/raw/
   ```

### 4.2  Combinar pistas de audio
`scripts/combine_audio_tracks.py`
```bash
# En Windows (PowerShell):
python "episode_2_viewmind/scripts/combine_audio_tracks.py" --host "episode_2_viewmind/raw/host.mp3" --guest "episode_2_viewmind/raw/guest.mp3" --output "episode_2_viewmind/processed/combined.wav"

# En Linux/macOS:
python episode_2_viewmind/scripts/combine_audio_tracks.py --host episode_2_viewmind/raw/host.mp3 --guest episode_2_viewmind/raw/guest.mp3 --output episode_2_viewmind/processed/combined.wav
```
- Combina las pistas de audio del host y el invitado en una sola pista
- Verifica y ajusta las duraciones si son diferentes
- Genera un archivo WAV combinado en la carpeta `processed/`

### 4.3  Transcribir audio
`scripts/transcribe.py`
```bash
# En Windows (PowerShell):
python "episode_2_viewmind/scripts/transcribe.py" --input "episode_2_viewmind/processed/combined.wav" --output "episode_2_viewmind/processed/transcription.txt" --model medium --language es

# En Linux/macOS:
python episode_2_viewmind/scripts/transcribe.py --input episode_2_viewmind/processed/combined.wav --output episode_2_viewmind/processed/transcription.txt --model medium --language es
```
- Transcribe el audio combinado usando Whisper
- Genera un archivo de texto con la transcripción completa
- Incluye timestamps para cada segmento


### 4.4  Generar posts para LinkedIn
`scripts/generate_posts.py`
```bash
python scripts/generate_posts.py --dialogue processed/dialogue.txt --preprod raw/preproduction.txt --output linkedin_posts/posts_en.md --n_posts 5
```
- Usa la API de Openrouter para generar exactamente cinco posts en inglés.
- Cada post cumple con las restricciones de LinkedIn (máx 1,300 caracteres).

---

## 5  Resumen de Scripts

### `combine_audio_tracks.py`
- **Propósito**: Combina pistas de audio del host y invitado
- **Flags principales**: `--host`, `--guest`, `--output`

### `transcribe.py`
- **Propósito**: Transcribe audio usando Whisper
- **Flags principales**: `--model`, `--language`, `--input`, `--output`

### `combine_dialogue.py`
- **Propósito**: Combina Preguntas y Respuestas en Markdown
- **Flags principales**: `--guest`, `--host`, `--output`

### `generate_posts.py`
- **Propósito**: Usa ChatCompletion API para crear posts
- **Flags principales**: `--n_posts`, `--output`

---

## 6  Logs y Manejo de Errores
- Cada script escribe logs en `logs/` (auto-creado) con timestamps UTC.
- Se usa la librería `logging` de Python.
- Ante errores de API, se implementa backoff exponencial y reintentos.

---

## 7  Entregables

### Archivos de entrada
- **Audio bruto y notas de preproducción**: 
  - Ubicación: `episode_2_viewmind/raw/`
  - Incluye: `host.mp3`, `guest.mp3`, `preproduction.txt`

### Archivos procesados
- **Transcripciones individuales**:
  - Ubicación: `episode_2_viewmind/processed/`
  - Archivos: `host.txt`, `guest.txt`

- **Diálogo completo**:
  - Ubicación: `episode_2_viewmind/processed/`
  - Archivo: `dialogue.txt`

### Resultado final
- **Posts para LinkedIn (en inglés)**:
  - Ubicación: `episode_2_viewmind/linkedin_posts/`
  - Archivo: `posts_en.md` (contiene 5 posts)

---

## 8  Extensiones Futuras

- **Variantes de idioma:** añadir generación de posts en español.
- **Automatización de publicación:** integrar APIs de Buffer/Hootsuite para publicar directamente en LinkedIn.

---

## 9  Notas de Implementación y Ajustes Recientes

### 9.1  Preprocesamiento de Audio
- Se reemplazó el preprocesamiento automático con ffmpeg por una conversión manual previa
- El script `transcribe.py` ahora acepta directamente archivos `.wav` convertidos
- Conversión manual recomendada:
  ```powershell
  # En Windows (PowerShell):
  ffmpeg -i "episode_2_viewmind/raw/guest.mp3" -ac 1 -ar 16000 "episode_2_viewmind/raw/guest.wav"
  ffmpeg -i "episode_2_viewmind/raw/host.mp3" -ac 1 -ar 16000 "episode_2_viewmind/raw/host.wav"

  # En Linux/macOS:
  ffmpeg -i episode_2_viewmind/raw/guest.mp3 -ac 1 -ar 16000 episode_2_viewmind/raw/guest.wav
  ffmpeg -i episode_2_viewmind/raw/host.mp3 -ac 1 -ar 16000 episode_2_viewmind/raw/host.wav
  ```

### 9.2  Transcripción en Español
- Se agregó soporte para forzar el idioma español mediante el parámetro `--language es`
- Ejemplo de uso:
  ```powershell
  python scripts/transcribe.py --input guest_test.wav --output processed/guest.txt --model large-v3 --language es
  ```

### 9.3  Medición de Tiempo
- El script ahora mide y reporta el tiempo total de transcripción en minutos
- Los tiempos se registran tanto en consola como en los logs
- Formato: `Tiempo total de transcripción: XX.XX minutos`

### 9.4  Sistema de Logs
- Directorio: `logs/` (auto-creado)
- Formato: `YYYY-MM-DD HH:MM:SS UTC - LEVEL - Mensaje`
- Niveles implementados: INFO, WARNING, ERROR
- Información registrada:
  - Dispositivo usado (CPU/GPU)
  - Modelo cargado
  - Idioma seleccionado
  - Tiempo total de proceso
  - Errores y advertencias

### 9.5  Compatibilidad CUDA y PyTorch
- Se verificó e instaló PyTorch con soporte CUDA
- Versión de CUDA: 12.8
- Versión de PyTorch: 2.7.0+cu128
- GPU detectada y utilizada automáticamente

### 9.6  Advertencias Conocidas
- **TF32 Warning**: Advertencia sobre TensorFloat-32 puede ser ignorada
  ```