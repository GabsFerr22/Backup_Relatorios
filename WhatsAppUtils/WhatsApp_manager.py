from selenium.webdriver.common.by import By
import time
import os


def enviar_imagens_whatsapp(driver, nome_grupo, imagens, mensagem="📊 Relatório Diário - Backup"):
    """
    Envia uma lista de imagens para um grupo do WhatsApp pelo nome.
    Usa o driver já iniciado pelo Browser().
    """

    # Abre a home do WhatsApp
    driver.get("https://web.whatsapp.com/")
    print("Aguardando carregamento do WhatsApp Web...")
    time.sleep(10)

    # --- PESQUISAR PELO GRUPO ---
    print(f"Abrindo grupo: {nome_grupo}")
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.click()
    time.sleep(1)
    search_box.send_keys(nome_grupo)
    time.sleep(3)

    # Clica no resultado da busca
    grupo = driver.find_element(By.XPATH, f'//span[@title="{nome_grupo}"]')
    grupo.click()
    time.sleep(3)

    # --- ENVIAR IMAGENS ---
    for img in imagens:
        print(f"Enviando imagem: {img}")

        # Botão de clipe (anexar)
        anexar_btn = driver.find_element(By.XPATH, '//div[@aria-label="Anexar"]')
        anexar_btn.click()
        time.sleep(1)

        # Input de upload de imagem
        imagem_input = driver.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        imagem_input.send_keys(os.path.abspath(img))
        time.sleep(2)

        # Campo de legenda
        legenda = driver.find_element(By.XPATH, '//div[@data-testid="caption-input"]')
        legenda.send_keys(mensagem)
        time.sleep(1)

        # Botão de enviar
        enviar_btn = driver.find_element(By.XPATH, '//span[@data-testid="send"]')
        enviar_btn.click()
        time.sleep(3)

    print("[OK] Imagens enviadas com sucesso!")
