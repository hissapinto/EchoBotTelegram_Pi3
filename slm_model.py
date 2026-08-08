# meu_gemma.py
import subprocess
import time
from ollama import chat

def start_ollama():
    """Inicia o Ollama em segundo plano se ele não estiver rodando."""
    try:
        chat(model='gemma3:270m', messages=[{'role': 'user', 'content': 'ping'}])
    except Exception:
        print("Ollama não está rodando. Iniciando servidor local...")
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)

def model_response(input, cabecalho):

    try:
        resposta = chat(
            model='gemma3:270m',
            messages=[
                {
                    'role': 'system',
                    'content': cabecalho,
                },
                {
                    'role': 'user',
                    'content': input,
                },
            ]
        )
        return resposta['message']['content']
    except Exception as e:
        return f"Erro ao conectar com o Ollama: {e}"