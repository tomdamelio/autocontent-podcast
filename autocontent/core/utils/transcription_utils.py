"""
Utilidades para el procesamiento de transcripciones.
"""

import os
import logging
from datetime import datetime
import pytz
import json
import time
from typing import Dict, List
import whisper
import torch
from pydub import AudioSegment
from .audio_utils import split_audio

def setup_logging(log_dir: str) -> logging.Logger:
    """Configura el sistema de logs con formato UTC"""
    os.makedirs(log_dir, exist_ok=True)
    
    utc_now = datetime.now(pytz.UTC)
    log_file = os.path.join(log_dir, f'transcription_{utc_now.strftime("%Y%m%d_%H%M%S")}.log')
    
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

def save_transcript(transcript: Dict, output_path: str):
    """
    Guarda una transcripción en formato JSON.
    
    Args:
        transcript (Dict): Diccionario con la transcripción
        output_path (str): Ruta donde guardar el archivo
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

def load_transcript(file_path: str) -> Dict:
    """
    Carga una transcripción desde un archivo JSON.
    
    Args:
        file_path (str): Ruta al archivo de transcripción
        
    Returns:
        Dict: Transcripción cargada
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_transcript_as_text(transcript: Dict, output_path: str):
    """
    Guarda una transcripción en formato texto plano.
    
    Args:
        transcript (Dict): Diccionario con la transcripción
        output_path (str): Ruta donde guardar el archivo
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Escribir el texto completo
        f.write(transcript['text'])

def format_time(seconds: float) -> str:
    """
    Formatea un tiempo en segundos a formato HH:MM:SS.
    
    Args:
        seconds (float): Tiempo en segundos
        
    Returns:
        str: Tiempo formateado
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def transcribe_audio(input_file: str, output_file: str, model_size: str = "medium", language: str = "es", log_dir: str = None) -> Dict:
    """
    Transcribe un archivo de audio usando Whisper.
    
    Args:
        input_file (str): Ruta al archivo de audio a transcribir
        output_file (str): Ruta para guardar la transcripción
        model_size (str): Modelo de Whisper a usar (tiny, base, small, medium, large)
        language (str): Idioma a forzar (por ejemplo, "es" para español)
        log_dir (str): Directorio para los logs
        
    Returns:
        Dict: Transcripción generada
    """
    logger = setup_logging(log_dir) if log_dir else logging.getLogger(__name__)
    
    # Iniciar medición de tiempo
    start_time = time.time()
    
    # Verificar si hay GPU disponible
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Usando dispositivo: {device}")
    
    # Cargar modelo
    logger.info(f"Cargando modelo: {model_size}")
    model = whisper.load_model(model_size).to(device)
    
    # Dividir audio en chunks si es necesario
    audio_duration = AudioSegment.from_file(input_file).duration_seconds
    if audio_duration > 300:  # Si el audio es más largo que 5 minutos
        logger.info("Dividiendo audio en chunks...")
        chunks = split_audio(input_file)
        all_segments = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Transcribiendo chunk {i+1}/{len(chunks)}...")
            result = model.transcribe(chunk, language=language)
            
            # Ajustar timestamps para cada chunk
            for segment in result["segments"]:
                segment["start"] += i * 300  # Ajustar timestamps
                segment["end"] += i * 300
                all_segments.append(segment)
            
            # Limpiar archivo temporal
            os.remove(chunk)
        
        result = {"text": " ".join(seg["text"] for seg in all_segments), "segments": all_segments}
    else:
        # Transcribir audio completo
        logger.info(f"Transcribiendo archivo: {input_file} (idioma: {language})")
        result = model.transcribe(input_file, language=language)
    
    # Guardar transcripción en formato texto
    logger.info("Guardando transcripción...")
    text_output_file = output_file.replace('.json', '.txt')
    save_transcript_as_text(result, text_output_file)
    
    # Calcular y mostrar tiempo total
    end_time = time.time()
    total_minutes = (end_time - start_time) / 60
    logger.info(f"Transcripción guardada exitosamente.")
    logger.info(f"Tiempo total de transcripción: {total_minutes:.2f} minutos")
    
    return result

def segment_transcript(transcript: Dict, max_segment_length: int = 1000) -> List[Dict]:
    """
    Segmenta una transcripción en partes más pequeñas.
    
    Args:
        transcript (Dict): Transcripción completa
        max_segment_length (int): Longitud máxima de cada segmento
        
    Returns:
        List[Dict]: Lista de segmentos de la transcripción
    """
    segments = []
    current_segment = {
        "text": "",
        "start": 0,
        "end": 0,
        "words": []
    }
    
    for segment in transcript.get("segments", []):
        if len(current_segment["text"]) + len(segment["text"]) <= max_segment_length:
            # Añadir al segmento actual
            current_segment["text"] += " " + segment["text"]
            current_segment["end"] = segment["end"]
            current_segment["words"].extend(segment.get("words", []))
        else:
            # Guardar el segmento actual y crear uno nuevo
            if current_segment["text"]:
                segments.append(current_segment)
            
            current_segment = {
                "text": segment["text"],
                "start": segment["start"],
                "end": segment["end"],
                "words": segment.get("words", [])
            }
    
    # Añadir el último segmento si tiene contenido
    if current_segment["text"]:
        segments.append(current_segment)
    
    return segments 