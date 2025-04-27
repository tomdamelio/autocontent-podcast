import os
import yaml
from pathlib import Path
from typing import Dict, Any

class EpisodeProcessor:
    def __init__(self, config_path: str):
        """
        Inicializa el procesador de episodios con la configuración especificada.
        
        Args:
            config_path (str): Ruta al archivo de configuración del episodio
        """
        self.config = self._load_config(config_path)
        self._setup_directories()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carga la configuración desde el archivo YAML."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_directories(self):
        """Crea los directorios necesarios si no existen."""
        paths = self.config['paths']
        for path in paths.values():
            if isinstance(path, str) and not path.endswith('.wav'):
                os.makedirs(path, exist_ok=True)
    
    def process_audio(self):
        """Procesa el audio del episodio."""
        raise NotImplementedError("Este método debe ser implementado por las clases hijas")
    
    def generate_transcript(self):
        """Genera la transcripción del episodio."""
        raise NotImplementedError("Este método debe ser implementado por las clases hijas")
    
    def create_linkedin_posts(self):
        """Crea los posts de LinkedIn basados en el contenido del episodio."""
        raise NotImplementedError("Este método debe ser implementado por las clases hijas")
    
    def run_pipeline(self):
        """Ejecuta el pipeline completo de procesamiento."""
        self.process_audio()
        self.generate_transcript()
        self.create_linkedin_posts() 