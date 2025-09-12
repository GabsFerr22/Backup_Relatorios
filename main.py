from config.settings import RELATORIOS, PASTA_REPOSITORIO, REPOSITORIO, MENSAGEM_COMMIT
from core.browser import Browser
from core.relatorio import RelatorioManager
from core.github_manager import GitHubManager
from core.relatorio_PDF import ReportManager
from utils.limiteBackup import limitar_relatorios
from utils.log import log
from core.relatorioJSON import StorageManager
from core.jira_manager import JiraManager
from datetime import datetime
import os
import time

class Main:
    def __init__(self):
        self.browser = Browser()
        self.storage = StorageManager()
        self.jira = JiraManager()

    def run(self):
        driver = self.browser.start()
        rel_manager = RelatorioManager(driver)

        # --- BACKUP DE RELATÓRIOS ---
        for nome_pasta, dados in RELATORIOS.items():
            log(f"\nIniciando backup de {nome_pasta}...")
            rel_manager.baixar_relatorios_em_massa(dados["link"], dados["pasta"])
            limitar_relatorios(dados["pasta"], limite=8)
        log("\n[OK] Backup Realizado com Sucesso!")

        # --- ATUALIZAÇÃO GITHUB ---
        git_manager = GitHubManager(PASTA_REPOSITORIO, REPOSITORIO, MENSAGEM_COMMIT)
        git_manager.atualizar()

        # --- SALVA DADOS NO STORAGE ---
        self.storage.add_data(
            rel_manager.relatorios_baixados,
            git_manager.commits,
            rel_manager.tasks_criadas
        )

        data = self.storage.load()

        # --- ATUALIZA DESCRIÇÃO DAS TASKS ---
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

        # --- CRIÇÃO DE RELATORIO ---
        agora = datetime.now()
        if agora >= 18:
            data = self.storage.load()


            ReportManager().gerar_relatorio(
                data["relatorios"],
                data["commits"],
                data["tasks"]
            )

            data_hoje = datetime.today().strftime("%d-%m-%Y")
            nome_pdf = f"Relatorio_Diario {data_hoje}.pdf"
            caminho_pdf = os.path.join(
                r"C:\Users\adm.joao.mendes\Documents\LOG DIARIO",
                nome_pdf
            )

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
