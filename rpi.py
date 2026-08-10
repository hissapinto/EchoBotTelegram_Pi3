# Antigo
"""
async def status(update: Update, context):
    Envia a temperatura e o espaço em disco do Raspberry Pi.

    # Temperatura do Pi:
    # subprocess.check_output roda um comando do terminal pelo Python e captura a saída.
    # O comando vai como lista (["vcgencmd", "measure_temp"]).
    # 'vcgencmd measure_temp' retorna algo como b"temp=42.8'C\n" (em bytes).
    #  decode converte de bytes pra string
    saida = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
    temp = float(saida.replace("temp=", "").replace("'C", "").strip())
    # strip tira espaços em branco do começo e do final

    # Espaço em disco:
    # 'df -h .' mostra o disco da pasta atual (.) como lista.
    result = subprocess.check_output(["df", "-h", "."])

    output = result.split() # divide e transforma em lista
    disk = ("Espaço em disco:\nTotal: " + output[9].decode("utf-8") +
            "\nUsado: " + output[10].decode("utf-8") +
            " (" + output[12].decode("utf-8") + ")" +
            "\nLivre: " + output[11].decode("utf-8")) #pega índices especificos

    temp_message = "Temperatura do Raspberry PI3: " + str(temp) + "°C"
    message = temp_message + "\n\n" + disk
    await update.message.reply_text(message)
    """

import psutil
import subprocess
from datetime import datetime
from telegram import Update


async def status(update: Update, context):
    """Envia informações de hardware do Raspberry Pi."""

    # Modelo do Pi
    # subprocess -> faz o python rodar comandos no terminal.
    # Tem mandar as especificações do comando em formato de lista
    # .strip() tira espaços e o caractere nulo do fim (\0).
    modelo = subprocess.check_output(["cat", "/proc/device-tree/model"]).decode("utf-8").strip()

    # Temperatura
    # ex de retorno: "temp=44.0'C". O comando seria: vcgencmd measure_temp
    saida = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
    temp = float(saida.replace("temp=", "").replace("'C", "").strip())

    # CPU
    #  mede o uso em %. interval=1 mede por 1 seg.
    cpu = psutil.cpu_percent(interval=1)

    # RAM
    # virtual_memory() devolve em struct/class?
    # dividir por 1024**2 pra ser em MB (vem em bytes)
    mem = psutil.virtual_memory()
    mem_usada = mem.used / (1024**2)
    mem_total = mem.total / (1024**2)

    # Swap
    # swap_memory() dá o swap (memória em disco).
    swap = psutil.swap_memory()
    swap_usado = swap.used / (1024**2)
    swap_total = swap.total / (1024**2)

    # Disco
    # disk_usage('/') -> disco da raiz. já em %
    disco = psutil.disk_usage('/')
    disco_usado = disco.used / (1024**3)   # em GB
    disco_total = disco.total / (1024**3)  # em GB

    # Uptime
    # boot_time -> momento em que o Pi ligou - now
    boot = datetime.fromtimestamp(psutil.boot_time())
    agora = datetime.now()
    uptime = agora - boot
    # tira os microssegundos
    uptime_str = str(uptime).split(".")[0]

    # mensagem
    message = (
        f"Informações do {modelo}:\n\n"
        f"Temperatura: {temp}°C\n"
        f"CPU: {cpu}%\n"
        f"RAM: {mem_usada:.0f} / {mem_total:.0f} MB ({mem.percent}%)\n"
        f"Swap: {swap_usado:.0f} / {swap_total:.0f} MB\n"
        f"Disco: {disco_usado:.1f} / {disco_total:.1f} GB ({disco.percent}%)\n"
        f"Ligado há: {uptime_str}"
    )

    await update.message.reply_text(message)