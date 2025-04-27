"""
Utilidades para el procesamiento de contenido y generación de posts.
"""

import os
import logging
from datetime import datetime
import pytz
import json
from typing import Dict, List
import yagmail
from dotenv import load_dotenv

def setup_logging(log_dir: str) -> logging.Logger:
    """Configura el sistema de logs con formato UTC"""
    os.makedirs(log_dir, exist_ok=True)
    
    utc_now = datetime.now(pytz.UTC)
    log_file = os.path.join(log_dir, f'content_processing_{utc_now.strftime("%Y%m%d_%H%M%S")}.log')
    
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

def save_post(post: Dict, output_path: str):
    """
    Guarda un post en formato JSON.
    
    Args:
        post (Dict): Diccionario con el contenido del post
        output_path (str): Ruta donde guardar el archivo
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(post, f, ensure_ascii=False, indent=2)

def load_post(file_path: str) -> Dict:
    """
    Carga un post desde un archivo JSON.
    
    Args:
        file_path (str): Ruta al archivo del post
        
    Returns:
        Dict: Post cargado
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_post_from_segment(segment: Dict, episode_info: Dict) -> Dict:
    """
    Genera un post de LinkedIn a partir de un segmento de transcripción.
    
    Args:
        segment (Dict): Segmento de transcripción
        episode_info (Dict): Información del episodio
        
    Returns:
        Dict: Post generado
    """
    # Extraer el texto del segmento
    text = segment.get("text", "").strip()
    
    # Generar título basado en el contenido
    title = generate_title(text)
    
    # Generar contenido del post
    content = generate_post_content(text, episode_info)
    
    # Generar hashtags
    hashtags = generate_hashtags(episode_info)
    
    return {
        "title": title,
        "content": content,
        "hashtags": hashtags,
        "metadata": {
            "episode": episode_info["number"],
            "timestamp": f"{segment.get('start', 0):.2f}-{segment.get('end', 0):.2f}"
        }
    }

def generate_title(text: str) -> str:
    """
    Genera un título atractivo para el post.
    
    Args:
        text (str): Texto del segmento
        
    Returns:
        str: Título generado
    """
    # Tomar las primeras palabras que formen una frase completa
    words = text.split()
    if len(words) > 10:
        title = " ".join(words[:10]) + "..."
    else:
        title = text
    
    return title

def generate_post_content(text: str, episode_info: Dict) -> str:
    """
    Genera el contenido del post de LinkedIn.
    
    Args:
        text (str): Texto del segmento
        episode_info (Dict): Información del episodio
        
    Returns:
        str: Contenido del post
    """
    # Crear el contenido del post
    content = f"🎙️ En el episodio {episode_info['number']} de nuestro podcast, {episode_info['title']}, "
    
    # Añadir información del invitado
    guest = episode_info['guests'][0]
    content += f"{guest['name']}, {guest['role']} de {guest['company']}, comparte:\n\n"
    
    # Añadir el texto del segmento
    content += f"{text}\n\n"
    
    # Añadir call to action
    content += "¿Qué opinas sobre esto? ¡Comparte tus pensamientos en los comentarios! 👇"
    
    return content

def generate_hashtags(episode_info: Dict) -> List[str]:
    """
    Genera hashtags relevantes para el post.
    
    Args:
        episode_info (Dict): Información del episodio
        
    Returns:
        List[str]: Lista de hashtags
    """
    hashtags = [
        f"#Podcast{episode_info['title']}",
        "#TechPodcast",
        "#Innovación",
        "#Tecnología"
    ]
    
    # Añadir hashtags específicos del episodio
    for guest in episode_info.get("guests", []):
        if guest.get("company"):
            hashtags.append(f"#{guest['company'].replace(' ', '')}")
        if guest.get("role"):
            hashtags.append(f"#{guest['role'].replace(' ', '')}")
    
    return hashtags

def create_posts_summary(posts: List[Dict], output_path: str):
    """
    Crea un archivo de texto con el resumen de todos los posts.
    
    Args:
        posts (List[Dict]): Lista de posts
        output_path (str): Ruta donde guardar el resumen
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, post in enumerate(posts, 1):
            f.write(f"Post {i}:\n")
            f.write(f"Título: {post['title']}\n")
            f.write(f"Contenido:\n{post['content']}\n")
            f.write(f"Hashtags: {' '.join(post['hashtags'])}\n")
            f.write(f"Timestamp: {post['metadata']['timestamp']}\n")
            f.write("\n" + "="*80 + "\n\n")

def send_transcription_email(transcription_file: str, subject: str = "Transcripción del Podcast", log_dir: str = None) -> None:
    """
    Envía la transcripción por correo electrónico usando yagmail.
    
    Args:
        transcription_file (str): Ruta al archivo de transcripción
        subject (str): Asunto del correo
        log_dir (str): Directorio para los logs
    """
    logger = setup_logging(log_dir) if log_dir else logging.getLogger(__name__)
    
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