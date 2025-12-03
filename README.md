# Documentação da RPA de Backup e Versionamento de Dashboards Power BI

## Visão Geral

Esta RPA foi desenvolvida para **automatizar o backup, versionamento e rastreamento de alterações** em relatórios da nossa plataforma: PBIReports 

O robô executa de forma autônoma os seguintes processos:

1. **Download dos relatórios do Power BI** passando por todas as pastas definidas.
2. **Backup local** em repositório organizado.
3. **Versionamento automático no GitHub**, garantindo histórico das alterações.
4. **Criação automática de tasks no Jira** sempre que houver alterações, associando ao usuário responsável.
5. **Execução orquestrada via Jenkins**, com agendamento em CRON.

---

## Relatórios Incluídos no Backup

A RPA percorre e realiza backup dos seguintes diretórios no Power BI:

- Adm Fin Cont
- Comercial
- DOC
- DOC Área Homologação
- Pneus
- Pós Vendas
- BI Empilhadeira
- BI Mardisa Veículos
- BI Mardisa CRM - Rac
- BI Mardisa Pós Vendas
- Contabilidade
- Fiscal
- RH - DP

---

## Orquestração e Agendamento

- **Ferramenta:** Jenkins
- **Agendamento:** CRON executado a cada **10 minutos** entre **07:00 e 19:00**.
- **Pipeline:** configurado via `Jenkinsfile`, garantindo controle de execução, logs e falhas.

---

## Arquitetura da Solução

O projeto foi desenvolvido em **Python**, utilizando **Selenium + ChromeDriver** para navegação automatizada no Power BI.

Foi aplicada **orientação a objetos (OOP)** para melhor organização, reuso de código e aplicação de **Clean Code**.

### Estrutura de Pastas

![image.png](/Document/image.png)

A estrutura é organizada da seguinte forma:

```
RPA_BACKUP_PBI/
│── config/
│   ├── __init__.py
│   ├── settings.py          # Configurações do projeto
│
│── core/
│   ├── __init__.py
│   ├── browser.py           # Controle do navegador (Selenium + ChromeDriver)
│   ├── github_manager.py    # Controle de versionamento no GitHub
│   ├── jira_manager.py      # Integração e criação de tasks no Jira
│   ├── relatorio.py         # Download e manipulação dos relatórios
│
│── utils/
│   ├── __init__.py
│   ├── file_utils.py        # Funções utilitárias para manipulação de arquivos
│   ├── log.py               # Módulo de logging e rastreabilidade
│
│── .env                     # Variáveis de ambiente (tokens, senhas, etc.)
│── .gitignore
│── Jenkinsfile              # Pipeline configurado no Jenkins
│── main.py                  # Ponto de entrada da aplicação
│── README.md
│── requirements.txt         # Dependências do projeto

```

---

## Fluxo de Execução

1. **Inicialização**
    - O `main.py` inicia a execução da RPA.
    - O `browser.py` abre o navegador via Selenium/ChromeDriver.
2. **Download de Relatórios**
    - O módulo `relatorio.py` percorre todas as pastas e baixa os dashboards se necessarios e os configura renomeando e movendo para pasta desejada localmente.
    - Os arquivos são salvos no repositório de backup.
3. **Versionamento no GitHub**
    - O módulo `github_manager.py` verifica novos arquivos.
    - Caso haja alterações, realiza o **commit e push** automaticamente para o repositório remoto.
    - Repositorio abaixo:
    
    ![image.png](/Document/image%201.png)
    
4. **Criação de Task no Jira**
    - O módulo `jira_manager.py` cria automaticamente uma task no Jira.
    - A task é associada ao usuário responsável pela modificação.
    
    📌 Exemplo de Task criada na automação.
    
    ![image.png](/Document/image%202.png)
    
5. **Logs e Monitoramento**
    - Todos os passos são registrados no `log.py` para auditoria e análises futuras.

---

## Dependências

As dependências estão listadas no arquivo `requirements.txt`. Principais libs utilizadas:

- `selenium` → automação de navegador
- `python-dotenv` → gerenciamento de variáveis de ambiente
- `requests` → integração com API do Jira
- `logging` → registro e auditoria de execuções

---

## Conclusão

Esta RPA garante:

✅ **Automatização completa** do processo de backup de dashboards Power BI.

✅ **Versionamento contínuo** dos relatórios no GitHub.

✅ **Rastreabilidade via Jira**, com tasks criadas automaticamente.

✅ **Execução confiável e agendada** via Jenkins.

✅ **Código limpo e sustentável**, orientado a objetos.

## Fluxo do Projeto

Abaixo verifique o fluxo do Projeto de forma Clara:

![image.png](/Document/image%203.png)