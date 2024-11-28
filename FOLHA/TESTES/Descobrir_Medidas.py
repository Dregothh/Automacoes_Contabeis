import fitz  # PyMuPDF
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Configuração do tkinter para escolher o arquivo PDF
Tk().withdraw()  # Oculta a janela principal do tkinter
arquivo_pdf = askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")], title="Selecione o arquivo PDF")

# Verifica se algum arquivo foi selecionado
if not arquivo_pdf:
    print("Nenhum arquivo selecionado.")
else:
    # Abre o PDF
    with fitz.open(arquivo_pdf) as pdf:
        # Pega a primeira página (ou pode adaptar para percorrer todas)
        pagina = pdf.load_page(0)
        texto_blocos = pagina.get_text("blocks")  # Obtém o texto dividido em blocos

        texto_procurado = "1.092,28"  # Substituir pelo texto que você está procurando

        print(f'texto_blocos: {texto_blocos}')
        # Itera sobre todos os blocos de texto
        for indice, bloco in enumerate(texto_blocos):
            # Cada bloco é uma tupla (x0, y0, x1, y1, "conteúdo do texto", bloco_num, linha_num)
            print(f'bloco: {bloco}')
            x0, y0, x1, y1, conteudo, bloco_num, linha_num = bloco

            # Procura pelo texto dentro do bloco
            if re.search(texto_procurado, conteudo):
                print(f"Texto encontrado no bloco {indice}:")
                print(f"Conteúdo: {conteudo}")
                print(f"Coordenadas: ({round(x0, 2)}, {round(y0, 2)}, {round(x1, 2)}, {round(y1, 2)})")
                break
        else:
            print("Texto não encontrado no documento.")
