import fitz  # PyMuPDF
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Configuração do tkinter para escolher o arquivo PDF
Tk().withdraw()  # Oculta a janela principal do tkinter
file_path = askopenfilename(filetypes=[("Arquivos PDF", "*.pdf")], title="Selecione o arquivo PDF")

if not file_path:
    print("Nenhum arquivo selecionado.")
else:
    try:
        # Abre o PDF usando o caminho do arquivo
        with fitz.open(file_path) as pdf:
            # Itera pelas páginas do PDF
            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)  # Carrega a página usando load_page
                text = page.get_text("text")  # Extrai o texto da página
                print(f"\n--- Texto da página {page_num + 1} ---\n")
                print(text)

    except Exception as e:
        print(f"Erro ao abrir o arquivo: {e}")
