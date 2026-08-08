# meu_gemma.py
import subprocess
import time
from ollama import chat

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