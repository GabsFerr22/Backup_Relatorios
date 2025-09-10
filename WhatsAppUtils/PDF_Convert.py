import os
from datetime import datetime
import fitz 
from PyPDF2 import PdfReader


def pdf_para_imagens_manual(caminho_pdf, pasta_output=r"C:\Users\adm.joao.mendes\Documents\prints_relatorio"):
    os.makedirs(pasta_output, exist_ok=True)
    reader = PdfReader(caminho_pdf)
    num_paginas = len(reader.pages)
    caminhos = []


    doc = fitz.open(caminho_pdf)

    for i in range(num_paginas):
        pagina = doc[i]
        pix = pagina.get_pixmap(dpi=200)  
        out_path = os.path.join(pasta_output, f"pagina_{i+1}.png")
        pix.save(out_path)
        caminhos.append(out_path)

    doc.close()
    return caminhos


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


if __name__ == "__main__":
    data_hoje = datetime.today().strftime("%d-%m-%Y")
    nome_pdf = f"Relatorio_Diario {data_hoje}.pdf"

    caminho_pdf = os.path.join(
        r"C:\Users\adm.joao.mendes\Documents\LOG DIARIO", 
        nome_pdf
    )

    verificar_pdf(caminho_pdf)

    imagens = pdf_para_imagens_manual(caminho_pdf)

    print("Imagens geradas:")
    for img in imagens:
        print(img)
