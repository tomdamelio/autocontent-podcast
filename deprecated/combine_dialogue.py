import argparse
import os
import json
import logging
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv

def setup_logging():
    """Configura el sistema de logs con formato UTC"""
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato y archivo de log con timestamp UTC
    utc_now = datetime.now(pytz.UTC)
    log_file = os.path.join(log_dir, f'combine_dialogue_{utc_now.strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s UTC - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def read_transcription(file_path):
    """Lee el archivo de transcripción y retorna su contenido"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def combine_dialogue_with_openrouter(host_text, guest_text, api_key):
    """Combina el diálogo usando OpenRouter para emparejar preguntas y respuestas"""
    logger = logging.getLogger(__name__)
    
    # Preparar el prompt para OpenRouter
    prompt = f"""Dado el siguiente texto del host y del invitado, empareja las preguntas con sus respuestas correspondientes.
    Formatea la salida en bloques de diálogo usando Markdown.

    Texto del host:
    {host_text}

    Texto del invitado:
    {guest_text}

    Por favor, empareja las preguntas con sus respuestas y formatea la salida así:
    **Host:** [pregunta]
    **Guest:** [respuesta]

    Asegúrate de mantener el contexto y el flujo de la conversación."""

    # Configurar la llamada a OpenRouter
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-3-opus-20240229",
        "messages": [
            {"role": "system", "content": "Eres un asistente experto en analizar y emparejar diálogos de entrevistas."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }

    try:
        logger.info("Enviando solicitud a OpenRouter...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        dialogue = result['choices'][0]['message']['content']
        
        logger.info("Diálogo combinado exitosamente")
        return dialogue
        
    except Exception as e:
        logger.error(f"Error al combinar el diálogo: {str(e)}")
        raise

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Combina transcripciones de host e invitado usando OpenRouter")
    parser.add_argument("--guest", required=True, help="Ruta al archivo de transcripción del invitado")
    parser.add_argument("--host", required=True, help="Ruta al archivo de transcripción del host")
    parser.add_argument("--output", required=True, help="Ruta para guardar el diálogo combinado")
    
    args = parser.parse_args()
    
    # Configurar logging
    logger = setup_logging()
    
    # Cargar variables de entorno
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY no encontrada en el archivo .env")
    
    # Leer transcripciones
    logger.info("Leyendo archivos de transcripción...")
    host_text = read_transcription(args.host)
    guest_text = read_transcription(args.guest)
    
    # Combinar diálogo
    logger.info("Combinando diálogo...")
    dialogue = combine_dialogue_with_openrouter(host_text, guest_text, api_key)
    
    # Asegurar que el directorio de salida existe
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Guardar diálogo
    logger.info(f"Guardando diálogo en: {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(dialogue)
    
    logger.info("Proceso completado exitosamente")

if __name__ == "__main__":
    main() 