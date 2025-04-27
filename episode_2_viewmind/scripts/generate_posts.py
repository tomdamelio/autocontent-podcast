import argparse
import os
import json
import requests
from dotenv import load_dotenv

def read_file(file_path):
    """Read file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_posts(dialogue_file, preprod_file, output_file, n_posts=5):
    """Generate LinkedIn posts using OpenRouter API"""
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY no encontrada en el archivo .env")
    
    # Read input files
    dialogue = read_file(dialogue_file)
    preprod = read_file(preprod_file)
    examples = read_file("episode_2_viewmind/raw/post_examples.md")
    
    # Construct the prompt
    system_prompt = """Eres un estratega de contenido para Brain Response, consultora de neurotecnologia que produce el podcast "Neurostartups".

Tu tarea es crear contenido especializado para LinkedIn a partir del podcast grabado y las notas de preproducción.
Tu objetivo es crear contenido que sea:
    - Profesional y técnicamente preciso
    - Atractivo para una audiencia profesional
    - Fácil de entender sin perder profundidad
    - Con un gancho claro en las primeras líneas
    - Con una llamada a la acción clara a escuchar el episodio del podcast"""
    
    user_prompt = f"""Aquí hay ejemplos de posts de LinkedIn de otro podcast (Startupeable), que te servirán como referencia (porque estan muy bien logrados):
    {examples}

    Aquí está el diálogo del podcast:
    {dialogue}
    
    Y aquí las notas de preproducción:
    {preprod}
    
    Crea exactamente {n_posts} posts para LinkedIn (máximo 1,300 caracteres cada uno) que capturen los puntos más importantes de la conversación.
    Cada post debe ser independiente y tener valor por sí mismo.
    Formatea cada post con un número (1-5) y una línea en blanco entre ellos.
    
    Sigue el estilo y estructura de los ejemplos proporcionados, adaptándolo al contenido de nuestro podcast y de esta entrevista en particular."""
    
    # Configure OpenRouter API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/mistral-small-3.1-24b-instruct:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }
    
    # Generate posts using OpenRouter
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    
    # Extract and format posts
    result = response.json()
    posts = result['choices'][0]['message']['content']
    
    # Write posts to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(posts)
    
    print(f"Posts generated and saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate LinkedIn posts from podcast dialogue")
    parser.add_argument("--dialogue", required=True, help="Dialogue file path")
    parser.add_argument("--preprod", required=True, help="Preproduction notes file path")
    parser.add_argument("--output", required=True, help="Output posts file path")
    parser.add_argument("--n_posts", type=int, default=5, help="Number of posts to generate")
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    generate_posts(args.dialogue, args.preprod, args.output, args.n_posts)

if __name__ == "__main__":
    main() 