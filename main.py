from config.settings import RELATORIOS, PASTA_REPOSITORIO, REPOSITORIO, MENSAGEM_COMMIT
from core.browser import Browser
from core.relatorio import RelatorioManager
from core.github_manager import GitHubManager
from core.relatorio_PDF import ReportManager
from utils.limiteBackup import limitar_relatorios
from utils.log import log
from core.relatorioJSON import StorageManager
from datetime import datetime, time
from core.jira_manager import JiraManager
from WhatsAppUtils.WhatsApp_manager import enviar_imagens_whatsapp
from WhatsAppUtils.PDF_Convert import pdf_para_imagens
import os
 
class Main:
    def __init__(self):
        self.browser = Browser()
        self.storage = StorageManager()
        self.jira = JiraManager()

    def run(self):
        driver = self.browser.start()
        rel_manager = RelatorioManager(driver)

        for nome_pasta, dados in RELATORIOS.items():
            log(f"\nIniciando backup de {nome_pasta}...")
            rel_manager.baixar_relatorios_em_massa(dados["link"], dados["pasta"])
            limitar_relatorios(dados["pasta"], limite=8)

        log("\n[OK] Backup Realizado com Sucesso!")

        git_manager = GitHubManager(PASTA_REPOSITORIO, REPOSITORIO, MENSAGEM_COMMIT)
        git_manager.atualizar()

        self.storage.add_data(
            rel_manager.relatorios_baixados,
            git_manager.commits,
            rel_manager.tasks_criadas
        )

        data = self.storage.load()

        for i, task in enumerate(data["tasks"]):
            if isinstance(task, dict):
                if "descricao" not in task or not task["descricao"]:
                    desc = self.jira.descricao_task(task.get("titulo", ""))
                    if desc:
                        data["tasks"][i]["descricao"] = desc
            else:
                data["tasks"][i] = {
                    "titulo": str(task),
                    "key": None,
                    "descricao": None
                }

        self.storage.save(data)


        # --- ENVIO DE RELATÓRIO PARA WHATSAPP ---
        if datetime.now().hour >= 18:
            data = self.storage.load()
            ReportManager().gerar_relatorio(
                data["relatorios"],
                data["commits"],
                data["tasks"]
            )

            # Define o caminho do PDF do dia
            data_hoje = datetime.today().strftime("%d-%m-%Y")
            nome_pdf = f"Relatorio_Diario {data_hoje}.pdf"
            caminho_pdf = os.path.join(
                r"C:\Users\adm.joao.mendes\Documents\LOG DIARIO",
                nome_pdf
            )

            # Converte PDF em imagens
            imagens = pdf_para_imagens(caminho_pdf)

            # ID do grupo WhatsApp
            GRUPO_ID = "@g.us_3EB02010A86B6E87DA2C"
            enviar_imagens_whatsapp(GRUPO_ID, imagens)

            self.storage.reset()



if __name__ == "__main__":
    main = Main()   
    try:
        main.run()
    except Exception as e:
        log(f"[ERRO] {e}")
    finally:
        try:
            log("[QUIT] Fechando navegador...")
            main.browser.quit()
            log("[QUIT] Fechado com Sucesso!!")
        except:
            pass
