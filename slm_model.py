# meu_gemma.py
# O Ollama é uma camada por cima do llama.cpp que simplifica bastante, mas em troca esconde e renomeia alguns parâmetros.

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
            options={
                'temperature': 0.3, # aleatoriedade: maior = mais "criativas"/imprevisíveis as respostas
                'top_p': 0.95, # (0.95): nucleus sampling: considera só os tokens cuja probabilidade acumulada chega a 95%
                'top_k': 50, # (50): limita a escolha aos 50 tokens mais prováveis a cada passo
                #'num_predict': 100,  # equivalente a max_tokens, quantidade máxima de tokens a gerar na resposta
                'repeat_penalty': 1.06, # penaliza tokens que já apareceram recentemente, reduzindo repetição (1.0 = desligado, >1.2 arriscado)
            },
            keep_alive= "30m" # para manter a IA na RAM por 30 min (se não ela é desalocada da RAM depois de 5 min). -1 para ficar sempre ligada
        )
        return response['message']['content']
    except Exception as e:
        return f"Erro ao conectar com o Ollama: {e}"