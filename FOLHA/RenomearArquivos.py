import fitz  # PyMuPDF
import os
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilenames

# Função para converter milímetros para pontos (PyMuPDF usa pontos)
def mm_pontos(milimetros):
    return milimetros * 72 / 25.4

# Função para extrair texto de uma região específica (em milímetros)
def extrair_texto_regiao(pagina, x0_mm, y0_mm, x1_mm, y1_mm):
    x0, y0, x1, y1 = mm_pontos(x0_mm), mm_pontos(y0_mm), mm_pontos(x1_mm), mm_pontos(y1_mm)
    texto = pagina.get_textbox(fitz.Rect(x0, y0, x1, y1)).strip()
    return texto

# Função para extrair texto de um bloco específico (usado em "Guia de Pagamento")
def extrair_texto_bloco(pagina, linha_inicial):
    texto_blocos = pagina.get_text("blocks")
    if len(texto_blocos) > linha_inicial:
        bloco = texto_blocos[linha_inicial]
        return bloco[4].strip()
    return ""

# Função para renomear o arquivo
def renomear_arquivo(caminho_arquivo, nome_empresa, sufixo=""):
    nome_empresa = nome_empresa.replace("/", "_").replace("_", " ")  # Formata o nome para evitar problemas
    novo_nome_arquivo = os.path.join(os.path.dirname(caminho_arquivo), f'{nome_empresa} {sufixo}.pdf')
    try:
        os.rename(caminho_arquivo, novo_nome_arquivo)
        print(f'Arquivo renomeado para: {novo_nome_arquivo}')
    except Exception as e:
        print(f"Erro ao renomear o arquivo {caminho_arquivo}: {e}")

# Função principal para processar o arquivo PDF
def processar_pdf(arquivo_pdf):
    nome_arquivo = os.path.basename(arquivo_pdf)

    with fitz.open(arquivo_pdf) as pdf:
        pagina = pdf.load_page(0)  # Considera que o nome da empresa está na primeira página

        # Verifica o padrão do nome do arquivo e aplica a extração apropriada
        sufixo = ""
        if re.match(r'^\d+-Recibo de Pagamento.*\.pdf$', nome_arquivo):
            # Para "*-Recibo de Pagamento", buscar o nome na região especificada
            nome_empresa = extrair_texto_regiao(pagina, 0, 0, 100, 4.5)
            sufixo = "(RECIBO)"
        elif re.match(r'^GuiaPagamento_\d+_\d+\.pdf$', nome_arquivo):
            # Para "GuiaPagamento_*", buscar na linha 2
            nome_empresa = extrair_texto_bloco(pagina, 2)
            if nome_empresa:
                nome_empresa = nome_empresa.split("\n")[-1]  # Manter apenas o texto após a "/n"
            sufixo = "(GUIA)"
        else:
            print(f"Nome do arquivo '{nome_arquivo}' não corresponde aos padrões especificados.")
            return

    # Renomear o arquivo se um nome foi encontrado
    if nome_empresa:
        renomear_arquivo(arquivo_pdf, nome_empresa, sufixo)
    else:
        print(f"Nenhum texto encontrado para renomear o arquivo {nome_arquivo}.")

if __name__ == "__main__":
    # Configuração do tkinter para escolher arquivos PDF
    Tk().withdraw()  # Oculta a janela principal do tkinter
    arquivos_pdf = askopenfilenames(filetypes=[("Arquivos PDF", "*.pdf")], title="Selecione os arquivos PDF")

    # Verifica se algum arquivo foi selecionado
    total_arquivos = len(arquivos_pdf)
    if total_arquivos == 0:
        print("Nenhum arquivo selecionado.")
    else:
        print(f"{total_arquivos} arquivo(s) selecionado(s). Processando...")
        # Loop através de todos os arquivos selecionados
        for arquivo_pdf in arquivos_pdf:
            processar_pdf(arquivo_pdf)