import os
import re
import glob
import shutil
import time
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from utils.limiteBackup import limitar_relatorios
from config.settings import PASTA_DOWNLOADS
from utils.file_utils import limpar_nome, esperar_download_concluir, garantir_pasta
from utils.log import log
from core.jira_manager import JiraManager

class RelatorioManager:
    def __init__(self, driver):
        self.driver = driver
        self.jira = JiraManager()
        self.relatorios_baixados = []
        self.tasks_criadas = []

    # ———————— REGRAS DE VERIFICAÇÃO ———————— #
    def precisa_baixar(self, nome_relatorio: str, span_text: str, pasta_base: str) -> bool:
        """
        Com subpasta por relatório:
        pasta_base/<nome_relatorio_limpo>/*.pbix ou *.rdl
        """
        try:
            m = re.search(r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2})", span_text)
            if not m:
                log(f"Não consegui extrair data de {nome_relatorio}. Vai baixar por segurança.")
                return True
            data_site = datetime.strptime(m.group(1), "%d/%m/%Y %H:%M")

            pasta_relatorio = os.path.join(pasta_base, limpar_nome(nome_relatorio))
            if not os.path.exists(pasta_relatorio):
                return True

            arquivos = glob.glob(os.path.join(pasta_relatorio, f"{limpar_nome(nome_relatorio)}*"))
            if not arquivos:
                return True

            datas_salvas = []
            for arq in arquivos:
                # extrai "dd-mm-YYYY HH-MM"
                achou = re.search(r"(\d{2}-\d{2}-\d{4} \d{2}-\d{2})", arq)
                if achou:
                    try:
                        datas_salvas.append(datetime.strptime(achou.group(1), "%d-%m-%Y %H-%M"))
                    except Exception:
                        pass

            if not datas_salvas:
                return True

            ultima_salva = max(datas_salvas)
            log(f"{nome_relatorio}: Data site = {data_site}, Última salva = {ultima_salva}")
            return data_site > ultima_salva

        except Exception as e:
            log(f"Erro ao comparar datas para {nome_relatorio}: {e}")
            return True

    # ———————— FLUXO DE DOWNLOAD E SALVAMENTO ———————— #
    def renomear_ultimo_download(self, nome_relatorio: str, span_text: str, pasta_base: str) -> None:
        try:
            nome_relatorio_limpo = limpar_nome(nome_relatorio)
            pasta_destino = os.path.join(pasta_base, nome_relatorio_limpo)
            garantir_pasta(pasta_destino)

            m = re.search(r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2})", span_text)
            ultima_data = m.group(1).replace("/", "-").replace(":", "-") if m else time.strftime("%d-%m-%Y %H-%M")

            usuario_match = re.search(r"PARVI\\([\w\.]+)", span_text)
            usuario = usuario_match.group(1) if usuario_match else "desconhecido"

            arquivo_original = None
            timeout = 120
            inicio = time.time()
            while time.time() - inicio < timeout:
                lista = glob.glob(os.path.join(PASTA_DOWNLOADS, "*.pbix")) + \
                        glob.glob(os.path.join(PASTA_DOWNLOADS, "*.rdl"))
                if lista:
                    arquivo_original = max(lista, key=os.path.getctime)
                    if not arquivo_original.endswith(".crdownload"):
                        break
                time.sleep(2)

            if not arquivo_original or arquivo_original.endswith(".crdownload"):
                log(f"Nenhum arquivo pronto encontrado para {nome_relatorio}")
                return

            extensao = os.path.splitext(arquivo_original)[1]
            novo_nome = f"{nome_relatorio_limpo} - {usuario} {ultima_data}{extensao}"
            caminho_final = os.path.join(pasta_destino, novo_nome)

            if os.path.exists(caminho_final):
                os.remove(caminho_final)

            shutil.move(arquivo_original, caminho_final)
            log(f"[OK] {nome_relatorio} salvo em {caminho_final}")

            ##Alteração nova, apagar se necessario
            self.relatorios_baixados.append([novo_nome, f"{usuario} - {ultima_data}"])

            # Tenta criar task no Jira (evita duplicata por título)
            titulo = f"ALTERAÇÃO FEITA NO RELATORIO : {nome_relatorio} Por {usuario} - {ultima_data}"
            self.jira.criar_task(titulo, assignee_username=usuario)
            
            ##Alteração nova, apagar se necessario
            self.tasks_criadas.append([titulo])
            # limitar_relatorios(pasta_destino, limite=8)

        except Exception as e:
            log(f"[ERRO] Erro ao renomear/mover {nome_relatorio}: {e}")

    # ———————— PIPELINE DE UM RELATÓRIO ———————— #
    def processar_relatorio(self, relatorio_web_element, pasta_destino: str) -> None:
        try:
            # Verifica o tipo do tile (sobe dois níveis)
            tile_tag = relatorio_web_element.find_element(By.XPATH, "../..").tag_name

            ActionChains(self.driver).context_click(relatorio_web_element).perform()

            # título
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "#content > app-metadata > section > div.content > h3"),
                    ""
                )
            )
            nome_relatorio = self.driver.find_element(
                By.CSS_SELECTOR, "#content > app-metadata > section > div.content > h3"
            ).text.strip()

            # span com "modificado por"
            WebDriverWait(self.driver, 30).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, "#content > app-metadata > section > div.content > ul > li.modified > span"),
                    ""
                )
            )
            span_text = self.driver.find_element(
                By.CSS_SELECTOR, "#content > app-metadata > section > div.content > ul > li.modified > span"
            ).text.strip()

            tentativas = 0
            while (not nome_relatorio or not span_text) and tentativas < 5:
                time.sleep(3)
                nome_relatorio = self.driver.find_element(
                    By.CSS_SELECTOR, "#content > app-metadata > section > div.content > h3"
                ).text.strip()
                span_text = self.driver.find_element(
                    By.CSS_SELECTOR, "#content > app-metadata > section > div.content > ul > li.modified > span"
                ).text.strip()
                tentativas += 1

            if not self.precisa_baixar(nome_relatorio, span_text, pasta_destino):
                log(f"[>>] {nome_relatorio} já está atualizado. Pulando.")
                try:
                    self._fechar_popup()
                except Exception:
                    pass
                return

            if tile_tag == "app-report-tile":
                seletor_download = "#content > app-metadata > section > footer > div:nth-child(4) > span:nth-child(1) > a"
            else: 
                seletor_download = "#content > app-metadata > section > footer > div:nth-child(3) > span:nth-child(1) > a > span"

            botao_download = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, seletor_download))
            )
            botao_download.click()

            esperar_download_concluir(PASTA_DOWNLOADS)
            self.renomear_ultimo_download(nome_relatorio, span_text, pasta_destino)

            try:
                self._fechar_popup()
            except Exception:
                pass

        except Exception as e:
            log(f"[WARN] Erro ao processar relatório: {e}")

    def _fechar_popup(self):
        botao_fechar = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#content > app-metadata > section > div.content > button"))
        )
        botao_fechar.click()

    # ———————— LOTE ———————— #
    def baixar_relatorios_em_massa(self, link: str, pasta_destino: str):
        self.driver.get(link)
        time.sleep(5)

        relatorios = WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "app-report-tile > app-tile-wrapper > a, app-power-bi-tile > app-tile-wrapper > a"))
        )

        log(f"Encontrados {len(relatorios)} relatórios em {link}")

        for relatorio in relatorios:
            self.processar_relatorio(relatorio, pasta_destino)
            time.sleep(3)
