import subprocess
from telegram import Update

async def status(update: Update, context):
    """Envia a temperatura e o espaço em disco do Raspberry Pi."""

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

    temp_message = "Temperatura do Raspberry: " + str(temp) + "°C"
    message = temp_message + "\n\n" + disk
    await update.message.reply_text(message)