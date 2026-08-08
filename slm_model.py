# meu_gemma.py

from ollama import chat

def model_response(input, cabecalho):

    try:
        response = chat(
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
            ],
            keep_alive= "30m" # para manter a IA na RAM por 30 min (se não ela é desalocada da RAM depois de 5 min). -1 para ficar sempre ligada
        )
        return response['message']['content']
    except Exception as e:
        return f"Erro ao conectar com o Ollama: {e}"