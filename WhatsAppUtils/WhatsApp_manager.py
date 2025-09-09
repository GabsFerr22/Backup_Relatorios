import pywhatkit as kit
import time

def enviar_imagens_whatsapp(numeros_grupo, imagens, mensagem="📊 Relatório Diário - Backup"):
    for img in imagens:
        kit.sendwhats_image(
            receiver=numeros_grupo,  
            img_path=img,
            caption=mensagem,
            wait_time=15
        )
        time.sleep(10) 
