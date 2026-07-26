# EchoBot Telegram — Raspberry Pi
**[@hissapinto_pi3_bot](https://t.me/hissapinto_pi3_bot)**

Bot de Telegram em Python, rodando 24/7 como serviço em um Raspberry Pi 3 Model B.

Com meu novo interesse em hardware, comprei um Raspberry Pi 3 na OLX e comecei a realizar
projetos populares que vi pela internet, para aprender um pouco enquanto me divirto.
Depois de configurar um Pi-hole na minha rede doméstica, decidi fazer um echo bot, pelo desafio
de manter meu dispositivo rodando 24/7 como um servidor pessoal e aprender mais sobre Linux,
Python e APIs no processo.

## Funcionalidades

- **Echo** — repete qualquer mensagem de texto recebida
- `/start` — mensagem de boas-vindas
- `/help` — descrição dos comandos
- `/facts` — busca um fato aleatório numa API externa e retorna

## Stack

- **Hardware:** Raspberry Pi 3 Model B (1 GB RAM)
- **SO:** Raspberry Pi OS Lite (64-bit), headless via SSH
- **Linguagem:** Python 3
- **Biblioteca:** [python-telegram-bot](https://python-telegram-bot.org/)
- **Execução contínua:** systemd (inicia no boot, reinicia em caso de falha)
- **API externa:** [uselessfacts](https://uselessfacts.jsph.pl/)

## Como rodar

Requer Python 3 e um token de bot do [@BotFather](https://t.me/BotFather).

```bash
git clone git@github.com:hissapinto/EchoBotTelegram_Pi3.git
cd EchoBotTelegram_Pi3

python3 -m venv venv
source venv/bin/activate
pip install python-telegram-bot python-dotenv requests

echo "TELEGRAM_BOT_TOKEN=seu_token_aqui" > .env

python echo_bot.py
```

O token fica num `.env` local, protegido pelo `.gitignore` — nunca vai pro repositório.

## Rodando como serviço (systemd)

Para manter o bot ativo 24/7 e reiniciar sozinho no boot, uso um serviço systemd
(`/etc/systemd/system/echobot.service`) apontando para o Python do venv:

```ini
[Service]
Type=simple
User=hissapinto
WorkingDirectory=/home/hissapinto/projects/TelegramPi3Bot
ExecStart=/home/hissapinto/projects/TelegramPi3Bot/venv/bin/python echo_bot.py
Restart=on-failure
```

```bash
sudo systemctl enable --now echobot
sudo systemctl status echobot
```

## Notas

Rodar num Pi 3 impõe restrições boas de RAM e CPU — o mesmo aparelho serve também
um Pi-hole em paralelo, sem gargalo. Escolhi hospedar em hardware próprio em vez de
uma VM na nuvem: mesmo papel de um servidor sempre ligado, sem custo recorrente.
