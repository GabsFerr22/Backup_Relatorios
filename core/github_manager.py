import os
import subprocess
from utils.log import log

class GitHubManager:
    def __init__(self, repo_path: str, repo_url: str, commit_message: str):
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.commit_message = commit_message
        self.commits = [] 


    def _run(self, args, cwd=None, check=True, capture=False):
        return subprocess.run(
            args,
            cwd=cwd,
            check=check,
            capture_output=capture,
            text=True
        )

    def _is_git_repo(self) -> bool:
        return os.path.exists(os.path.join(self.repo_path, ".git"))

    def atualizar(self):
        os.makedirs(self.repo_path, exist_ok=True)

        if not self._is_git_repo():
            if not os.listdir(self.repo_path):
                log("Clonando repositório...")
                self._run(["git", "clone", self.repo_url, self.repo_path], cwd=None)
            else:
                log("Inicializando repositório git local...")
                self._run(["git", "init"], cwd=self.repo_path)

                remotes = self._run(["git", "remote"], cwd=self.repo_path, check=False, capture=True)
                if "origin" not in remotes.stdout.split():
                    self._run(["git", "remote", "add", "origin", self.repo_url], cwd=self.repo_path)
                    
        self._run(["git", "lfs", "install"], cwd=self.repo_path)
        self._run(["git", "add", "."], cwd=self.repo_path)

        diff = self._run(["git", "diff", "--cached", "--quiet"], cwd=self.repo_path, check=False)
        if diff.returncode != 0:
            self._run(["git", "config", "user.name", "BI-PARVI"], cwd=self.repo_path)
            self._run(["git", "config", "user.email", "bi@parvi.com.br"], cwd=self.repo_path)

            self._run(["git", "commit", "-m", self.commit_message], cwd=self.repo_path)
            log("[OK] Commit realizado!")
            
            ##alteração nova, apagar se necessario.
            self.commits.append(["*", self.commit_message])

        else:
            log("[WARN] Nenhuma alteração para commitar.")

        self._run(["git", "branch", "-M", "main"], cwd=self.repo_path, check=False)

        try:
            self._run(["git", "push", "-u", "origin", "main"], cwd=self.repo_path)
            log("[OK] Alterações enviadas para GitHub com sucesso!")
        except subprocess.CalledProcessError as e:
            log(f"[ERROR] Erro ao enviar para o GitHub: {e}")
