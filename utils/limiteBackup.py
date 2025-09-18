import os
from utils.log import log
from typing import Iterable, Optional

def limitar_relatorios(pasta: str, limite: int = 8, extensoes: Optional[Iterable[str]] = None, dry_run: bool = False):
    if not os.path.isdir(pasta):
        log(f"[WARN] Pasta não encontrada: {pasta}")
        return

    # Itera sobre subpastas
    for root, dirs, files in os.walk(pasta):
        arquivos = []
        for f in files:
            if extensoes and os.path.splitext(f)[1].lower() not in {e.lower() if e.startswith('.') else f".{e.lower()}" for e in extensoes}:
                continue
            caminho = os.path.join(root, f)
            try:
                ts = os.stat(caminho).st_ctime if os.name == "nt" else os.stat(caminho).st_mtime
                arquivos.append((caminho, ts))
            except Exception as e:
                log(f"[WARN] Não consegui ler metadata de {caminho}: {e}")

        total = len(arquivos)
        if total <= limite:
            continue  # essa pasta está ok

        arquivos.sort(key=lambda x: x[1])  # mais antigo primeiro
        remover = arquivos[:-limite]

        log(f"[INFO] {root}: {total} arquivos, removendo {len(remover)} (limite={limite})")
        for path, _ in remover:
            try:
                if dry_run:
                    log(f"[DRY-RUN] Removeria: {path}")
                else:
                    os.remove(path)
                    log(f"[OK] Removido: {path}")
            except Exception as e:
                log(f"[ERRO] Não consegui remover {path}: {e}")

# exemplo rápido de uso para testar:
if __name__ == "__main__":
    pasta_teste = r"C:\Users\adm.joao.mendes\Documents\LOG DIARIO"
    limitar_relatorios(pasta_teste, limite=8, extensoes=['.pdf'], dry_run=True)
