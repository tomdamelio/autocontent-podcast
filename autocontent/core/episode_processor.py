"""
Procesador base para episodios del podcast.
"""

import os
import logging
from datetime import datetime
import pytz
from typing import Dict, Any
import yaml
import whisper
import shutil
from pydub import AudioSegment

from .utils import audio_utils, transcription_utils, content_utils

class EpisodeProcessor:
    def __init__(self, config_path: str):
        """
        Inicializa el procesador de episodios con la configuración especificada.
        
        Args:
            config_path (str): Ruta al archivo de configuración del episodio
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self._setup_directories()
        self.logger = self._setup_logging()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga la configuración desde el archivo YAML."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_directories(self):
        """Crea la estructura completa de directorios y mueve los archivos MP3 a la carpeta raw."""
        episode_dir = os.path.dirname(self.config_path)
        
        # Crear estructura de directorios
        directories = [
            'raw',
            'processed',
            'processed/transcripts',
            'linkedin_posts',
            'logs'
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(episode_dir, directory), exist_ok=True)
        
        # Mover archivos MP3 a la carpeta raw si están en la raíz
        for file in os.listdir(episode_dir):
            if file.endswith('.mp3'):
                source = os.path.join(episode_dir, file)
                if 'host' in file.lower():
                    destination = os.path.join(episode_dir, 'raw', 'host.mp3')
                elif 'guest' in file.lower():
                    destination = os.path.join(episode_dir, 'raw', 'guest.mp3')
                else:
                    continue
                
                # Mover el archivo si no existe en el destino
                if not os.path.exists(destination):
                    shutil.move(source, destination)
    
    def _setup_logging(self) -> logging.Logger:
        """Configura el sistema de logs."""
        log_dir = os.path.join(os.path.dirname(self.config_path), self.config['paths']['logs'])
        return logging.getLogger(__name__)
    
    def process_audio(self):
        """Procesa el audio del episodio."""
        episode_dir = os.path.dirname(self.config_path)
        raw_audio = self.config['paths']['raw_audio']
        processed_audio = self.config['paths']['processed_audio']
        combined_audio = self.config['paths']['combined_audio']
        
        # Rutas completas
        host_audio_path = os.path.join(episode_dir, raw_audio['host'])
        guest_audio_path = os.path.join(episode_dir, raw_audio['guest'])
        combined_audio_path = os.path.join(episode_dir, combined_audio)
        
        # Cargar archivos MP3
        self.logger.info("Cargando archivos de audio...")
        host_audio = AudioSegment.from_file(host_audio_path)
        guest_audio = AudioSegment.from_file(guest_audio_path)
        
        # Verificar que ambos archivos tengan la misma duración
        if len(host_audio) != len(guest_audio):
            self.logger.warning(f"Las pistas tienen duraciones diferentes: Host={len(host_audio)/1000:.2f}s, Guest={len(guest_audio)/1000:.2f}s")
            # Ajustar a la duración más corta
            min_duration = min(len(host_audio), len(guest_audio))
            host_audio = host_audio[:min_duration]
            guest_audio = guest_audio[:min_duration]
        
        # Combinar las pistas
        self.logger.info("Combinando pistas de audio...")
        combined_audio = host_audio.overlay(guest_audio)
        
        # Guardar el audio combinado en WAV
        self.logger.info(f"Guardando audio combinado en: {combined_audio_path}")
        combined_audio.export(combined_audio_path, format="wav")
        
        self.logger.info("Proceso de audio completado exitosamente")
    
    def generate_transcript(self):
        """Genera la transcripción del episodio."""
        episode_dir = os.path.dirname(self.config_path)
        combined_audio = self.config['paths']['combined_audio']
        transcripts_path = os.path.join(episode_dir, self.config['paths']['transcripts'])
        
        # Ruta completa al audio combinado
        audio_path = os.path.join(episode_dir, combined_audio)
        
        # Transcribir el audio
        self.logger.info("Transcribiendo audio...")
        result = transcription_utils.transcribe_audio(
            audio_path,
            os.path.join(transcripts_path, 'transcript.json'),
            model_size=self.config['processing']['transcription']['model'],
            language=self.config['processing']['transcription']['language'],
            log_dir=os.path.join(episode_dir, self.config['paths']['logs'])
        )
    
    def create_linkedin_posts(self):
        """Crea los posts de LinkedIn basados en el contenido del episodio."""
        if not self.config.get('create_linkedin_posts', True):
            self.logger.info("Generación de posts de LinkedIn desactivada en la configuración")
            return
            
        episode_dir = os.path.dirname(self.config_path)
        transcripts_path = os.path.join(episode_dir, self.config['paths']['transcripts'])
        linkedin_posts_path = os.path.join(episode_dir, self.config['paths']['linkedin_posts'])
        
        # Cargar la transcripción
        transcript_file = os.path.join(transcripts_path, 'transcript.json')
        if not os.path.exists(transcript_file):
            self.logger.error(f"No se encontró el archivo de transcripción: {transcript_file}")
            return
            
        transcript = transcription_utils.load_transcript(transcript_file)
        
        # Generar posts para cada segmento
        posts = []
        for segment in transcript.get('segments', []):
            post = content_utils.generate_post_from_segment(segment, self.config['episode'])
            posts.append(post)
            
            # Guardar post individual
            post_path = os.path.join(linkedin_posts_path, f'post_{len(posts)}.json')
            content_utils.save_post(post, post_path)
        
        # Crear resumen de posts
        content_utils.create_posts_summary(
            posts,
            os.path.join(linkedin_posts_path, 'posts_summary.txt')
        )
    
    def send_email_notifications(self):
        """Envía las notificaciones por correo electrónico."""
        episode_dir = os.path.dirname(self.config_path)
        transcripts_path = os.path.join(episode_dir, self.config['paths']['transcripts'])
        linkedin_posts_path = os.path.join(episode_dir, self.config['paths']['linkedin_posts'])
        
        # Enviar transcripción
        transcript_file = os.path.join(transcripts_path, 'transcript.txt')
        if os.path.exists(transcript_file):
            self.logger.info("Enviando transcripción por correo...")
            subject = f"Transcripción del Podcast - Episodio {self.config['episode']['number']}"
            content_utils.send_transcription_email(
                transcript_file,
                subject,
                os.path.join(episode_dir, self.config['paths']['logs'])
            )
        
        # Enviar posts de LinkedIn si se generaron
        if self.config.get('create_linkedin_posts', True):
            post_files = [f for f in os.listdir(linkedin_posts_path) if f.startswith('post_')]
            if post_files:
                self.logger.info("Enviando posts de LinkedIn por correo...")
                subject = f"Posts de LinkedIn - Episodio {self.config['episode']['number']}"
                
                # Crear contenido del correo con todos los posts
                email_content = "Posts de LinkedIn generados:\n\n"
                for post_file in sorted(post_files):
                    post_path = os.path.join(linkedin_posts_path, post_file)
                    post = content_utils.load_post(post_path)
                    email_content += f"Post {post_file.replace('post_', '').replace('.json', '')}:\n"
                    email_content += f"Título: {post['title']}\n"
                    email_content += f"Contenido:\n{post['content']}\n"
                    email_content += f"Hashtags: {' '.join(post['hashtags'])}\n"
                    email_content += "\n" + "="*80 + "\n\n"
                
                # Enviar el correo
                content_utils.send_transcription_email(
                    email_content,
                    subject,
                    os.path.join(episode_dir, self.config['paths']['logs'])
                )
    
    def run_pipeline(self):
        """Ejecuta el pipeline completo de procesamiento."""
        try:
            self.logger.info("Iniciando procesamiento del episodio...")
            
            # Procesar audio
            self.logger.info("Procesando audio...")
            self.process_audio()
            
            # Generar transcripción
            self.logger.info("Generando transcripción...")
            self.generate_transcript()
            
            # Crear posts de LinkedIn (opcional)
            self.logger.info("Procesando posts de LinkedIn...")
            self.create_linkedin_posts()
            
            # Enviar notificaciones por correo
            self.logger.info("Enviando notificaciones por correo...")
            self.send_email_notifications()
            
            self.logger.info("Procesamiento completado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error durante el procesamiento: {str(e)}")
            raise 