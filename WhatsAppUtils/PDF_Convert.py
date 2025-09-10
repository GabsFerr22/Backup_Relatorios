import os
from datetime import datetime
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
import subprocess

def pdf_para_imagens_manual(caminho_pdf, pasta_output="prints_relatorio"):
    os.makedirs(pasta_output, exist_ok=True)
    reader = PdfReader(caminho_pdf)
    num_paginas = len(reader.pages)
    caminhos = []
    
    for i in range(num_paginas):
        out_path = os.path.join(pasta_output, f"pagina_{i+1}.png")
        subprocess.run([
            r"C:\poppler-25.07.0\Library\bin\pdftoppm.exe",
            "-f", str(i+1),
            "-l", str(i+1),
            "-png",
            caminho_pdf,
            os.path.splitext(out_path)[0]
        ], check=True)
        caminhos.append(out_path)
    return caminhos


if __name__ == "__main__":
    data_hoje = datetime.today().strftime("%d-%m-%Y")
    nome_pdf = f"Relatorio_Diario {data_hoje}.pdf"

    caminho_pdf = os.path.join(
        r"C:\Users\adm.joao.mendes\Documents\LOG DIARIO", 
        nome_pdf
    )

    imagens = pdf_para_imagens(caminho_pdf)

    print("Imagens geradas:")
    for img in imagens:
        print(img)


def verificar_pdf(caminho_pdf):
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")
    if os.path.getsize(caminho_pdf) == 0:
        raise ValueError(f"O PDF está vazio: {caminho_pdf}")

    try:
        reader = PdfReader(caminho_pdf)
        num_paginas = len(reader.pages)
        print(f"[OK] PDF válido, páginas detectadas: {num_paginas}")
    except Exception as e:
        raise ValueError(f"Erro ao abrir PDF: {e}")




def verificar_pdf(caminho_pdf):
    if not os.path.exists(caminho_pdf):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_pdf}")
    if os.path.getsize(caminho_pdf) == 0:
        raise ValueError(f"O PDF está vazio: {caminho_pdf}")

    try:
        reader = PdfReader(caminho_pdf)
        num_paginas = len(reader.pages)
        print(f"[OK] PDF válido, páginas detectadas: {num_paginas}")
    except Exception as e:
        raise ValueError(f"Erro ao abrir PDF: {e}")
