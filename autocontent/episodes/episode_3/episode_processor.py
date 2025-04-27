"""
Implementación específica del procesador para el episodio 3.
"""

import os
from pathlib import Path
from typing import Dict, Any
import whisper

from autocontent.core.episode_processor import EpisodeProcessor
from autocontent.core.utils import audio_utils, transcription_utils, content_utils

class Episode3Processor(EpisodeProcessor):
    def process_audio(self):
        """Procesa el audio del episodio 3."""
        raw_audio_path = os.path.join(os.path.dirname(self.config_path), self.config['paths']['raw_audio'])
        processed_audio_path = os.path.join(os.path.dirname(self.config_path), self.config['paths']['processed_audio'])
        
        # Cargar y procesar el audio
        audio_data, sr = audio_utils.load_audio(raw_audio_path)
        
        # Guardar el audio procesado
        output_path = os.path.join(processed_audio_path, 'processed_audio.wav')
        audio_utils.save_audio(audio_data, output_path, sr)
    
    def generate_transcript(self):
        """Genera la transcripción del episodio 3."""
        processed_audio_path = os.path.join(os.path.dirname(self.config_path), self.config['paths']['processed_audio'])
        transcripts_path = os.path.join(os.path.dirname(self.config_path), self.config['paths']['transcripts'])
        
        # Cargar el modelo de Whisper
        model = whisper.load_model("base")
        
        # Transcribir el audio
        audio_path = os.path.join(processed_audio_path, 'processed_audio.wav')
        result = model.transcribe(audio_path, language="es")
        
        # Guardar la transcripción
        transcript_path = os.path.join(transcripts_path, 'transcript.json')
        transcription_utils.save_transcript(result, transcript_path)
        
        # Segmentar la transcripción
        segments = transcription_utils.segment_transcript(result)
        
        # Guardar los segmentos
        for i, segment in enumerate(segments):
            segment_path = os.path.join(transcripts_path, f'segment_{i+1}.json')
            transcription_utils.save_transcript(segment, segment_path)
    
    def create_linkedin_posts(self):
        """Crea los posts de LinkedIn para el episodio 3."""
        transcripts_path = os.path.join(os.path.dirname(self.config_path), self.config['paths']['transcripts'])
        linkedin_posts_path = os.path.join(os.path.dirname(self.config_path), self.config['paths']['linkedin_posts'])
        
        # Cargar los segmentos
        segment_files = [f for f in os.listdir(transcripts_path) if f.startswith('segment_')]
        
        for segment_file in segment_files:
            segment_path = os.path.join(transcripts_path, segment_file)
            segment = transcription_utils.load_transcript(segment_path)
            
            # Generar post
            post = content_utils.generate_post_from_segment(segment, self.config['episode'])
            
            # Guardar post
            post_path = os.path.join(linkedin_posts_path, f'post_{segment_file.replace("segment_", "").replace(".json", "")}.json')
            content_utils.save_post(post, post_path) 