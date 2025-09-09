# WhatsAppUtils/WhatsApp_manager.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os

def enviar_imagens_whatsapp(grupo_id, imagens, mensagem="📊 Relatório Diário - Backup"):
    """
    Envia uma lista de imagens para um grupo do WhatsApp pelo ID.
    """

    # Configuração do Chrome para usar perfil existente (WhatsApp já logado)
    options = Options()
    options.add_argument(r"--user-data-dir=C:\Users\adm.joao.mendes\AppData\Local\Google\Chrome\User Data")  
    options.add_argument("--profile-directory=Default")  # ajuste se usar outro perfil

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://web.whatsapp.com/send?phone={grupo_id}")


    print("Aguardando carregamento do grupo...")
    time.sleep(10)  

    for img in imagens:
        # Clicar no botão de anexar
        anexar_btn = driver.find_element(By.XPATH, '//div[@title="Anexar"]')
        anexar_btn.click()
        time.sleep(1)

        # Clicar no botão de enviar imagem
        imagem_input = driver.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        imagem_input.send_keys(os.path.abspath(img))
        time.sleep(2)

        # Adicionar legenda
        legenda = driver.find_element(By.XPATH, '//div[@data-testid="caption-input"]')
        legenda.send_keys(mensagem)
        time.sleep(1)

        # Clicar no botão de enviar
        enviar_btn = driver.find_element(By.XPATH, '//span[@data-testid="send"]')
        enviar_btn.click()
        time.sleep(3)

    print("Imagens enviadas com sucesso!")
    driver.quit()
