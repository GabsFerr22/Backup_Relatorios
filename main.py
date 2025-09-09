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


        if datetime.now().hour >= 18:
            data = self.storage.load()
            ReportManager().gerar_relatorio(
                data["relatorios"],
                data["commits"],
                data["tasks"]
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
            main.browser.quit()
        except:
            pass
