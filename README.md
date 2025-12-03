# Backup Relatórios (RPA)

Automação para baixar relatórios do Power BI On-Prem, organizar por categorias e subpastas de cada relatório, versionar em GitHub e abrir tarefas no Jira quando houver alterações.

## Como rodar?
1. Python 3.10+
2. `pip install -r requirements.txt`
3. Configure `config/settings.py` (caminhos, repo, Jira).
4. `python main.py`

## Jenkins
Use o `Jenkinsfile` ou configure "Build periodically" (`H/15 7-18 * * *`).

## Estrutura
- `core/` classes OOP (Browser, RelatorioManager, GitHubManager, JiraManager).
- `utils/` utilidades (arquivos e logs).
- `config/` settings centralizados.
- `WhatsAppUtils/` converte e envia para o WhatsApp a imagem
