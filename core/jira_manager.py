import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote
from config.settings import (
    JIRA_URL, JIRA_USER, JIRA_TOKEN, JIRA_PROJECT_KEY, JIRA_USERS, DATA_HOJE
)
from utils.log import log

class JiraManager:
    def __init__(self):
        self.base_url = JIRA_URL
        self.auth = HTTPBasicAuth(JIRA_USER, JIRA_TOKEN)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def _search_issues(self, jql: str, max_results: int = 50):
        url = f"{self.base_url}/search"
        params = {"jql": jql, "maxResults": max_results}
        r = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        r.raise_for_status()
        return r.json().get("issues", [])


    def issue_exists_with_exact_summary(self, summary: str) -> bool:
        jql = f'project = "{JIRA_PROJECT_KEY}" AND summary ~ "\\"{summary}\\""'
        issues = self._search_issues(jql)
        for issue in issues:
            if issue.get("fields", {}).get("summary", "") == summary:
                return True
        return False

    def criar_task(self, titulo: str, assignee_username: str | None = None):
        """Cria task apenas se não existir com o MESMO summary."""
        if self.issue_exists_with_exact_summary(titulo):
            log(f"[WARN] Task já existe no Jira com o mesmo título. Pulando criação: {titulo}")
            return None

        assignee_id = JIRA_USERS.get(assignee_username or "", None)

        if assignee_username and not assignee_id:
            log(f"[WARN] Usuário desconhecido: {assignee_username}. Task não será criada.")
            return None

        payload = {
            "fields": {
                "project": {"key": JIRA_PROJECT_KEY},
                "summary": titulo,
                "issuetype": {"name": "Task"},
                "labels": ["BACKUP"],
                "duedate": DATA_HOJE,
                "customfield_10020": 114,
                "customfield_10037": DATA_HOJE
            }
        }
        if assignee_id:
            payload["fields"]["assignee"] = {"id": assignee_id}

        r = requests.post(
            f"{self.base_url}/issue",
            json=payload,
            headers=self.headers,
            auth=self.auth
        )
        if r.status_code == 201:
            key = r.json().get("key")
            log(f"[OK] Task criada no Jira: {key}")
            return key
        log(f"[ERROR] Erro ao criar task no Jira: {r.status_code} - {r.text}")
        return None

    # ---------------------------------------------
    # Função auxiliar para extrair texto de ADF
    # ---------------------------------------------
    def _extrair_texto_adf(self, nodo):
        textos = []

        def extrair(n):
            if isinstance(n, dict):
                if n.get("type") == "text" and "text" in n:
                    textos.append(n["text"])
                for filho in n.get("content", []):
                    extrair(filho)
            elif isinstance(n, list):
                for item in n:
                    extrair(item)

        extrair(nodo)
        return " ".join(textos).strip() if textos else None

    def descricao_task(self, summary: str) -> str | None:
        """Busca descrição + comentários da issue no Jira a partir do summary (string simples ou ADF)."""
        jql = f'project = "{JIRA_PROJECT_KEY}" AND summary ~ "\\"{summary}\\""'
        issues = self._search_issues(jql)
        if not issues:
            log(f"[WARN] Nenhuma issue encontrada para summary: {summary}")
            return None

        issue = issues[0]
        fields = issue.get("fields", {})

        textos = []

        # 1. Descrição
        desc = fields.get("description")
        if desc:
            if isinstance(desc, str):
                textos.append(desc)
            elif isinstance(desc, dict):
                texto = self._extrair_texto_adf(desc)
                if texto:
                    textos.append(texto)

        # 2. Comentários
        comentarios = fields.get("comment", {}).get("comments", [])
        for c in comentarios:
            body = c.get("body")
            if body:
                texto = self._extrair_texto_adf(body)
                if texto:
                    textos.append(f"- {texto}")

        return "\n\n".join(textos) if textos else None

    def debug_issue_fields(self, issue_key: str):
        """
        Busca todos os campos crus de uma issue do Jira (para debug).
        Assim você pode ver por que 'key' e 'description' podem estar vindo nulos.
        """
        url = f"{self.base_url}/issue/{issue_key}"
        r = requests.get(url, headers=self.headers, auth=self.auth)
        if r.status_code != 200:
            log(f"[ERROR] Erro ao buscar issue {issue_key}: {r.status_code} - {r.text}")
            return None

        data = r.json()
        log(f"[DEBUG] Dados crus da issue {issue_key}: {data}")
        return data
