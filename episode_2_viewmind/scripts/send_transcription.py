import argparse
import os
import logging
from datetime import datetime
import pytz
from dotenv import load_dotenv
import yagmail

def setup_logging():
    """Configura el sistema de logs con formato UTC"""
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato y archivo de log con timestamp UTC
    utc_now = datetime.now(pytz.UTC)
    log_file = os.path.join(log_dir, f'send_transcription_{utc_now.strftime("%Y%m%d_%H%M%S")}.log')
    
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

def send_transcription_email(transcription_file, subject="Transcripción del Podcast"):
    """Envía la transcripción por correo electrónico usando yagmail"""
    logger = setup_logging()
    
    # Cargar variables de entorno
    load_dotenv()
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("EMAIL_RECIPIENT")
    
    if not all([sender_email, sender_password, recipient_email]):
        raise ValueError("Faltan credenciales de correo en el archivo .env")
    
    try:
        # Leer el contenido del archivo
        with open(transcription_file, 'r', encoding='utf-8') as f:
            transcription_content = f.read()
        
        # Inicializar yagmail
        logger.info("Inicializando yagmail...")
        yag = yagmail.SMTP(sender_email, sender_password)
        
        # Enviar el correo
        logger.info("Enviando correo...")
        yag.send(
            to=recipient_email,
            subject=subject,
            contents=transcription_content,
            attachments=transcription_file
        )
        
        logger.info(f"Correo enviado exitosamente a {recipient_email}")
        
    except Exception as e:
        logger.error(f"Error al enviar el correo: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Envía la transcripción por correo electrónico")
    parser.add_argument("--transcription", required=True, help="Ruta al archivo de transcripción")
    parser.add_argument("--subject", default="Transcripción del Podcast", help="Asunto del correo")
    
    args = parser.parse_args()
    
    send_transcription_email(args.transcription, args.subject)

if __name__ == "__main__":
    main() 