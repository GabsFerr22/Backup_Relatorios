import os
from datetime import datetime
from pdf2image import convert_from_path

def pdf_para_imagens(caminho_pdf, pasta_output="prints_relatorio"):
    os.makedirs(pasta_output, exist_ok=True)
    imagens = convert_from_path(caminho_pdf, dpi=200)  
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
