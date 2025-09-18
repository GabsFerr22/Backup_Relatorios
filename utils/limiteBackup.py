import os
from utils.log import log
from typing import Iterable, Optional

def limitar_relatorios(pasta: str, limite: int = 8, extensoes: Optional[Iterable[str]] = None, dry_run: bool = False):
    """
    Mantém no máximo 'limite' arquivos em 'pasta'.
    Remove os mais antigos caso ultrapasse.
    - extensoes: lista opcional de extensões (ex: ['.pdf']) para considerar apenas esses arquivos.
    - dry_run: se True, apenas loga quais arquivos seriam removidos sem apagar nada.
    """

    if not os.path.isdir(pasta):
        log(f"[WARN] Pasta não encontrada: {pasta}")
        return

    # Normaliza as extensões (se fornecidas)
    exts = None
    if extensoes:
        exts = {e.lower() if e.startswith('.') else f".{e.lower()}" for e in extensoes}

    arquivos = []
    with os.scandir(pasta) as it:
        for entry in it:
            if not entry.is_file():
                continue
            if exts and os.path.splitext(entry.name)[1].lower() not in exts:
                continue
            try:
                # No Windows, stat().st_ctime normalmente representa tempo de criação.
                # Em Unix, st_ctime é metadata-change; para cross-platform mais previsível usamos:
                timestamp = entry.stat().st_ctime if os.name == "nt" else entry.stat().st_mtime
            except Exception as e:
                log(f"[WARN] Não consegui ler metadata de {entry.path}: {e}")
                continue
            arquivos.append((entry.path, timestamp))

    total = len(arquivos)
    log(f"[INFO] {total} arquivo(s) encontrado(s) em '{pasta}' (limite={limite}).")

    if total <= limite:
        log("[OK] Não há arquivos para remover.")
        return

    # Ordena do mais antigo para o mais novo
    arquivos.sort(key=lambda x: x[1])

    # Arquivos a remover (todos exceto os últimos `limite`)
    remover = arquivos[:-limite]
    log(f"[INFO] Serão removidos {len(remover)} arquivo(s).")

    for path, ts in remover:
        if dry_run:
            log(f"[DRY-RUN] Removeria: {path}")
            continue
        try:
            os.remove(path)
            log(f"[OK] Arquivo removido: {path}")
        except Exception as e:
            log(f"[ERRO] Não consegui remover {path}: {e}")

# exemplo rápido de uso para testar:
if __name__ == "__main__":
    pasta_teste = r"C:\Users\adm.joao.mendes\Documents\LOG DIARIO"
    limitar_relatorios(pasta_teste, limite=8, extensoes=['.pdf'], dry_run=True)
