import argparse
import os
import whisper
from dotenv import load_dotenv
import json
import logging
from datetime import datetime
import pytz
import time
from tqdm import tqdm
import torch
import numpy as np
from pydub import AudioSegment

def setup_logging():
    """Configura el sistema de logs con formato UTC"""
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato y archivo de log con timestamp UTC
    utc_now = datetime.now(pytz.UTC)
    log_file = os.path.join(log_dir, f'transcribe_{utc_now.strftime("%Y%m%d_%H%M%S")}.log')
    
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

def split_audio(input_file, chunk_length_ms=300000):  # 5 minutos por chunk
    """Divide el audio en chunks más pequeños"""
    audio = AudioSegment.from_file(input_file)
    chunks = []
    
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_path = f"{input_file}_chunk_{i//chunk_length_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    
    return chunks

def transcribe_audio(input_file, output_file, model_size="medium", language="es"):
    """
    Transcribe un archivo de audio usando Whisper
    
    Parameters:
    - input_file: Ruta al archivo de audio a transcribir
    - output_file: Ruta para guardar la transcripción
    - model_size: Modelo de Whisper a usar (tiny, base, small, medium, large)
    - language: Idioma a forzar (por ejemplo, "es" para español)
    """
    # Configurar logging y variables de entorno
    logger = setup_logging()
    load_dotenv()
    
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
    
    # Guardar transcripción
    logger.info("Guardando transcripción...")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    
    # Guardar timestamps en JSON
    logger.info("Guardando timestamps...")
    segments = result.get("segments", [])
    with open(output_file.replace(".txt", "_timestamps.json"), "w", encoding="utf-8") as f:
        json.dump([
            {"start": s["start"], "end": s["end"], "text": s["text"]} for s in segments
        ], f, indent=2)
    
    # Calcular y mostrar tiempo total
    end_time = time.time()
    total_minutes = (end_time - start_time) / 60
    logger.info(f"Transcripción y segmentos guardados exitosamente.")
    logger.info(f"Tiempo total de transcripción: {total_minutes:.2f} minutos")

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI Whisper")
    parser.add_argument("--input", required=True, help="Input audio file path")
    parser.add_argument("--output", required=True, help="Output text file path")
    parser.add_argument("--model", default="medium", help="Whisper model to use (tiny, base, small, medium, large)")
    parser.add_argument("--language", default="es", help="Language code (e.g., 'es' for Spanish)")
    
    args = parser.parse_args()
    
    # Asegurar que el directorio de salida existe
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Ejecutar transcripción
    transcribe_audio(args.input, args.output, args.model, args.language)

if __name__ == "__main__":
    main() 