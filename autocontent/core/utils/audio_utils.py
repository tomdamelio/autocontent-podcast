"""
Utilidades para el procesamiento de audio.
"""

import os
import logging
from datetime import datetime
import pytz
from pydub import AudioSegment
from typing import Tuple, List

def setup_logging(log_dir: str) -> logging.Logger:
    """Configura el sistema de logs con formato UTC"""
    os.makedirs(log_dir, exist_ok=True)
    
    utc_now = datetime.now(pytz.UTC)
    log_file = os.path.join(log_dir, f'audio_processing_{utc_now.strftime("%Y%m%d_%H%M%S")}.log')
    
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

def load_audio(file_path: str, sample_rate: int = 44100) -> Tuple[AudioSegment, int]:
    """
    Carga un archivo de audio y retorna el segmento de audio y la tasa de muestreo.
    
    Args:
        file_path (str): Ruta al archivo de audio
        sample_rate (int): Tasa de muestreo deseada
        
    Returns:
        Tuple[AudioSegment, int]: (segmento_audio, tasa_muestreo)
    """
    audio = AudioSegment.from_file(file_path)
    return audio, sample_rate

def save_audio(audio: AudioSegment, file_path: str, sample_rate: int = 44100):
    """
    Guarda los datos de audio en un archivo.
    
    Args:
        audio (AudioSegment): Segmento de audio a guardar
        file_path (str): Ruta donde guardar el archivo
        sample_rate (int): Tasa de muestreo
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    audio.export(file_path, format="wav")

def convert_to_wav(input_file: str, output_file: str, sample_rate: int = 44100) -> str:
    """
    Convierte un archivo de audio a formato WAV.
    
    Args:
        input_file (str): Ruta al archivo de audio de entrada
        output_file (str): Ruta donde guardar el archivo WAV
        sample_rate (int): Tasa de muestreo deseada
        
    Returns:
        str: Ruta al archivo WAV generado
    """
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_frame_rate(sample_rate)
    audio.export(output_file, format="wav")
    return output_file

def combine_audio_tracks(host_file: str, guest_file: str, output_file: str, log_dir: str) -> None:
    """
    Combina las pistas de audio del host y el invitado en una sola pista.
    
    Args:
        host_file (str): Ruta al archivo de audio del host
        guest_file (str): Ruta al archivo de audio del invitado
        output_file (str): Ruta para guardar el audio combinado
        log_dir (str): Directorio para los logs
    """
    logger = setup_logging(log_dir)
    
    try:
        # Cargar archivos de audio
        logger.info("Cargando archivos de audio...")
        host_audio = AudioSegment.from_file(host_file)
        guest_audio = AudioSegment.from_file(guest_file)
        
        # Verificar que ambos archivos tengan la misma duración
        if len(host_audio) != len(guest_audio):
            logger.warning(f"Las pistas tienen duraciones diferentes: Host={len(host_audio)/1000:.2f}s, Guest={len(guest_audio)/1000:.2f}s")
            # Ajustar a la duración más corta
            min_duration = min(len(host_audio), len(guest_audio))
            host_audio = host_audio[:min_duration]
            guest_audio = guest_audio[:min_duration]
        
        # Combinar las pistas
        logger.info("Combinando pistas de audio...")
        combined_audio = host_audio.overlay(guest_audio)
        
        # Guardar el audio combinado
        logger.info(f"Guardando audio combinado en: {output_file}")
        save_audio(combined_audio, output_file)
        
        logger.info("Proceso completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error al combinar las pistas de audio: {str(e)}")
        raise

def split_audio(input_file: str, chunk_length_ms: int = 300000) -> List[str]:
    """
    Divide el audio en chunks más pequeños.
    
    Args:
        input_file (str): Ruta al archivo de audio
        chunk_length_ms (int): Longitud de cada chunk en milisegundos
        
    Returns:
        List[str]: Lista de rutas a los chunks generados
    """
    audio = AudioSegment.from_file(input_file)
    chunks = []
    
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunk_path = f"{input_file}_chunk_{i//chunk_length_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    
    return chunks 