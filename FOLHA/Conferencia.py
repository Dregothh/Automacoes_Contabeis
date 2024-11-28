import fitz
from ResumoJSON import exec
from RenomearArquivos import mm_pontos, extrair_texto_regiao
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilenames


def searchText(file, search):
    with fitz.open(file) as pdf:
        for idx in range(len(pdf)):
            pagina = pdf.load_page(idx)
            texto = pagina.get_text("text")

            # Verifica se o texto está presente na página
            if search in texto:
                return True

    # Se não encontrar o texto em nenhuma página
    return False

def locate(coord, page):
    clip_rect = fitz.Rect(coord)
    texto_encontrado = page.get_text("text", clip=clip_rect)
    if texto_encontrado:
        print(f"Texto encontrado nas coordenadas: {coord}")
        print(texto_encontrado)
    else:
        print(f"Nenhum texto encontrado nas coordenadas {coord}.")

def getINSS(file):
    with fitz.open(file) as pdf:
        pagina = pdf.load_page(0)

        coord_valor = (450.0, 201.0, 556.0, 217.0)
        coord_nome = (150, 132.53, 502.14, 144.82)

        locate(coord_nome, pagina)
        locate(coord_valor, pagina)


if __name__ == "__main__":

    # Configuração do tkinter para escolher os arquivos PDF
    Tk().withdraw()  # Oculta a janela principal do tkinter
    arquivos = askopenfilenames(filetypes=[("Arquivos PDF", "*.pdf")], title="Selecione o arquivo PDF")

    getINSS(arquivos[0])
