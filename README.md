# AutoContent Podcast

Sistema automatizado para procesar episodios de podcast, generar transcripciones y crear posts de LinkedIn.

## Estado Actual

El sistema actualmente:
- ✅ Procesa archivos de audio MP3
- ✅ Combina las pistas de host e invitado
- ✅ Genera transcripción usando Whisper
- ✅ Envía la transcripción por correo
- ❌ Generación de posts de LinkedIn (en desarrollo)
- ❌ Envío de posts por correo (en desarrollo)

## Próximas Características

1. **Generación de Posts de LinkedIn**:
   - Implementar la generación de posts a partir de la transcripción
   - Formatear los posts según las mejores prácticas de LinkedIn
   - Añadir emojis y hashtags relevantes

2. **Envío de Posts**:
   - Enviar los posts generados por correo
   - Incluir formato adecuado para fácil copia y pega en LinkedIn

## Estructura del Repositorio

```
autocontent/
├── core/                    # Código principal del sistema
│   ├── episode_processor.py # Procesador principal de episodios
│   └── utils/              # Utilidades
│       ├── audio_utils.py  # Procesamiento de audio
│       ├── transcription_utils.py # Transcripción y procesamiento de texto
│       └── content_utils.py # Generación de contenido y envío de correos
├── scripts/
│   └── process_episode.py  # Script para procesar un episodio
└── episodes/               # Carpeta para cada episodio
    └── episode_X/         # Carpeta específica para cada episodio
        ├── raw/          # Archivos de audio originales
        │   ├── host.mp3
        │   └── guest.mp3
        ├── processed/    # Archivos procesados
        │   ├── combined.wav
        │   └── transcripts/
        ├── linkedin_posts/ # Posts generados
        └── episode_config.yaml # Configuración del episodio
```

## Requisitos

1. Python 3.8 o superior
2. Dependencias (instalar con `pip install -r requirements.txt`):
   - numpy
   - soundfile
   - PyYAML
   - whisper
   - torch
   - transformers
   - python-dotenv
   - yagmail
   - pydub

## Configuración

1. Crear un archivo `.env` en la raíz del proyecto con las credenciales de correo:
```
EMAIL_SENDER=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña
EMAIL_RECIPIENT=destinatario@email.com
```

2. Para cada episodio, crear una carpeta `episode_X` con su archivo de configuración `episode_config.yaml`:
```yaml
# Configuración base para episodios del podcast
episode:
  number: X  # Número del episodio
  title: "Título del Episodio"
  date: "YYYY-MM-DD"
  guests:
    - name: "Nombre del Invitado"
      role: "Rol del Invitado"
      company: "Empresa del Invitado"

# Configuración de rutas
paths:
  raw_audio:
    host: "raw/host.mp3"
    guest: "raw/guest.mp3"
  processed_audio: "processed/"
  combined_audio: "processed/combined.wav"
  transcripts: "processed/transcripts/"
  linkedin_posts: "linkedin_posts/"
  logs: "logs/"

# Configuración de procesamiento
processing:
  audio:
    sample_rate: 44100
    channels: 2
    input_format: "mp3"
    output_format: "wav"
  transcription:
    language: "es"
    model: "medium"  # Opciones: tiny, base, small, medium, large
  content:
    max_post_length: 1300
    min_post_length: 1000

# Opciones de generación de contenido
create_linkedin_posts: true  # Activar/desactivar generación de posts
```

## Uso

1. **Preparar los archivos de audio**:
   - Colocar los archivos MP3 en la carpeta `episode_X`
   - Los archivos deben contener las palabras "host" y "guest" en sus nombres
   - El sistema los moverá automáticamente a la carpeta `raw`

2. **Procesar el episodio**:
```bash
python autocontent/scripts/process_episode.py X
```
Donde X es el número del episodio.

3. **Resultados**:
   - En `processed/transcripts/transcript.txt`: Transcripción completa
   - Por correo: Transcripción
   - Posts de LinkedIn: En desarrollo

## Modelos de Transcripción

El sistema usa Whisper para la transcripción. Los modelos disponibles son:
- `tiny`: Más rápido, menos preciso
- `base`: Rápido, precisión básica
- `small`: Más preciso que base
- `medium`: Aún más preciso, más lento
- `large`: El más preciso, más lento y requiere más memoria

Para cambiar el modelo, modifica `model: "medium"` en el archivo de configuración.

## Notas

- Los archivos de audio deben ser MP3
- El sistema combina automáticamente las pistas de host e invitado
- La transcripción se guarda en formato texto plano
- Los posts de LinkedIn están en desarrollo
- Todo el proceso se registra en la carpeta `logs` 