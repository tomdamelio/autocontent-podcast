import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path para poder importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

from autocontent.core.episode_processor import EpisodeProcessor

def main():
    # Obtener el número de episodio desde los argumentos de línea de comandos
    if len(sys.argv) != 2:
        print("Uso: python process_episode.py <número_episodio>")
        sys.exit(1)
    
    episode_number = sys.argv[1]
    config_path = f"episode_{episode_number}/episode_config.yaml"
    
    if not os.path.exists(config_path):
        print(f"Error: No se encontró el archivo de configuración para el episodio {episode_number}")
        sys.exit(1)
    
    # Crear y ejecutar el procesador de episodios
    processor = EpisodeProcessor(config_path)
    processor.run_pipeline()

if __name__ == "__main__":
    main() 