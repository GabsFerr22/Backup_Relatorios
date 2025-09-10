import os
from datetime import datetime
from pdf2image import convert_from_path
from PyPDF2 import PdfReader


def pdf_para_imagens(caminho_pdf, pasta_output="prints_relatorio"):
    os.makedirs(pasta_output, exist_ok=True)
    imagens = convert_from_path(caminho_pdf, dpi=200, poppler_path = r"C:\poppler-25.07.0\Library\bin" )  
    caminhos = []
    for i, img in enumerate(imagens):
        caminho_img = os.path.join(pasta_output, f"pagina_{i+1}.png")
        img.save(caminho_img, "PNG")
        caminhos.append(caminho_img)
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
