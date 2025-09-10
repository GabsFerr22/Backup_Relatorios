# WhatsAppUtils/WhatsApp_manager.py
from selenium.webdriver.common.by import By
import time
import os

def enviar_imagens_whatsapp(driver, grupo_id, imagens, mensagem="📊 Relatório Diário - Backup"):
    """
    Envia uma lista de imagens para um grupo do WhatsApp pelo ID.
    Usa o driver já iniciado pelo Browser().
    """

    # Se for ID de grupo (termina com @g.us), precisa usar link especial
    if grupo_id.endswith("@g.us"):
        url = f"https://web.whatsapp.com/accept?code={grupo_id}"
    else:  # fallback para número de telefone
        url = f"https://web.whatsapp.com/send?phone={grupo_id}"

    driver.get(url)

    print("Aguardando carregamento do grupo...")
    time.sleep(10)

    for img in imagens:
        anexar_btn = driver.find_element(By.XPATH, '//div[@title="Anexar"]')
        anexar_btn.click()
        time.sleep(1)

        imagem_input = driver.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        imagem_input.send_keys(os.path.abspath(img))
        time.sleep(2)

        legenda = driver.find_element(By.XPATH, '//div[@data-testid="caption-input"]')
        legenda.send_keys(mensagem)
        time.sleep(1)

        enviar_btn = driver.find_element(By.XPATH, '//span[@data-testid="send"]')
        enviar_btn.click()
        time.sleep(3)

    print("Imagens enviadas com sucesso!")
