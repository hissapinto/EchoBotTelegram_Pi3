"""
DistilGPT-2 rodando com onnxruntime PURO (sem torch, sem optimum).

A ideia: em vez de usar model.generate() (que exigia torch/optimum),
carregamos o arquivo .onnx direto com onnxruntime e escrevemos o loop
de geracao "na mao" — prever o proximo token, adicionar, repetir.

Precisa instalado no venv:
    onnxruntime      -> roda o .onnx
    transformers     -> so pelo AutoTokenizer (leve, nao precisa do torch)
    huggingface_hub  -> baixar o .onnx pronto do repositorio
    numpy            -> os dados entram/saem como arrays numpy
"""

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer
from huggingface_hub import hf_hub_download

# 1. TOKENIZER — traduz texto <-> numeros (tokens). Funciona sem torch.
checkpoint = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

# 2. BAIXAR O .onnx PRONTO do repositorio oficial (subpasta onnx/).
#    Assim NAO precisamos do torch pra converter (era o export=True).
onnx_path = hf_hub_download(
    repo_id="distilbert/distilgpt2",
    filename="onnx/model.onnx",
)

# 3. CARREGAR no onnxruntime. CPUExecutionProvider = roda na CPU (sem CUDA).
session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])


def model_response(prompt, max_new_tokens=40, temperature=0.7):
    """Gera texto um token de cada vez (o loop que o generate fazia sozinho)."""

    # texto -> tokens numpy ("np", nao "pt"/torch)
    enc = tokenizer(prompt, return_tensors="np")
    input_ids = enc["input_ids"]
    attention_mask = enc["attention_mask"]

    for _ in range(max_new_tokens):
        onnx_inputs = {
            "input_ids": input_ids.astype(np.int64),
            "attention_mask": attention_mask.astype(np.int64),
        }
        # roda o modelo -> logits: pontuacao de cada token possivel como proximo
        logits = session.run(None, onnx_inputs)[0]
        # so interessa a previsao da ULTIMA posicao (o proximo token)
        next_token_logits = logits[0, -1, :] / temperature

        # softmax: logits -> probabilidades
        exp = np.exp(next_token_logits - np.max(next_token_logits))
        probs = exp / np.sum(exp)

        # amostra um token pelas probabilidades (do_sample=True)
        next_token_id = np.random.choice(len(probs), p=probs)

        if next_token_id == tokenizer.eos_token_id:
            break

        # adiciona o token novo e continua o loop
        input_ids = np.concatenate([input_ids, [[next_token_id]]], axis=1)
        attention_mask = np.concatenate([attention_mask, [[1]]], axis=1)

    return tokenizer.decode(input_ids[0], skip_special_tokens=True)




"""
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForCausalLM # para hardware limitado - ONNX Runtime

checkpoint = "distilgpt2" # modelo que só completa as frases que você inputa
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = ORTModelForCausalLM.from_pretrained(checkpoint, subfolder="onnx") # ORTModelForCausalLM tranforma de pytorch pra ONNX

# tokenizer = AutoTokenizer.from_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model")
# model = AutoModelForCausalLM.from_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model")


def model_response(input):

    inputs = tokenizer(input, return_tensors="np") # np para o onnix, pt para o

    output_ids = model.generate(
        **inputs,
        max_length=60,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,      # adiciona variação nas respostas
        temperature=0.5,     # 0 = mais previsível, 1+ = mais "criativo"/aleatório
    )

    texto_gerado = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return texto_gerado

# salva o modelo
model.save_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model")
tokenizer.save_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model")
"""