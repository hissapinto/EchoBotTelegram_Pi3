from transformers import AutoTokenizer, AutoModelForCausalLM

checkpoint = "gpt2" # modelo que só completa as frases que você inputa
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint)

# tokenizer = AutoTokenizer.from_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model")
# model = AutoModelForCausalLM.from_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model")


def model_response(input):

    inputs = tokenizer(input, return_tensors="pt")

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
model.save_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model2")
tokenizer.save_pretrained("/home/hissapinto/projects/TelegramPi3Bot/Model")