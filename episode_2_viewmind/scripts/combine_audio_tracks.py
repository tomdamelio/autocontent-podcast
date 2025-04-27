import argparse
import os
import logging
from datetime import datetime
import pytz
from pydub import AudioSegment
from dotenv import load_dotenv

def setup_logging():
    """Configura el sistema de logs con formato UTC"""
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato y archivo de log con timestamp UTC
    utc_now = datetime.now(pytz.UTC)
    log_file = os.path.join(log_dir, f'combine_audio_{utc_now.strftime("%Y%m%d_%H%M%S")}.log')
    
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

def combine_audio_tracks(host_file, guest_file, output_file):
    """
    Combina las pistas de audio del host y el invitado en una sola pista
    
    Parameters:
    - host_file: Ruta al archivo de audio del host
    - guest_file: Ruta al archivo de audio del invitado
    - output_file: Ruta para guardar el audio combinado
    """
    logger = setup_logging()
    
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
        
        # Asegurar que el directorio de salida existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Exportar el audio combinado
        logger.info(f"Guardando audio combinado en: {output_file}")
        combined_audio.export(output_file, format="wav")
        
        logger.info("Proceso completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error al combinar las pistas de audio: {str(e)}")
        raise

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Combina las pistas de audio del host y el invitado")
    parser.add_argument("--host", required=True, help="Ruta al archivo de audio del host")
    parser.add_argument("--guest", required=True, help="Ruta al archivo de audio del invitado")
    parser.add_argument("--output", required=True, help="Ruta para guardar el audio combinado")
    
    args = parser.parse_args()
    
    # Ejecutar combinación de audio
    combine_audio_tracks(args.host, args.guest, args.output)

if __name__ == "__main__":
    main() 