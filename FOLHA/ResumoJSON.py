import fitz  # PyMuPDF
import json
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from datetime import datetime

# Configuração do debug
debug = False

def mm_to_points(mm):
    return mm / 25.4 * 72

def obter_arquivo_pdf():
    Tk().withdraw()  # Oculta a janela principal do tkinter
    return askopenfilename(
        filetypes=[("Arquivos PDF", "*.pdf")],
        title="Arquivo do RESUMO",
        initialdir="C:/A"
    )

def inicializar_dados_empresa(empresa_id, nome_empresa, cnpjcpf):
    return {
        'empresa_id': empresa_id,
        'identificação': cnpjcpf,
        'fgts_total': 0.0,
        'inss_total': 0.0
    }

def processar_linha_para_fgts(linha_atual, linha_posterior, total_fgts):
    if "Valor do FGTS:" in linha_atual:
        fgts_match = re.search(r'([\d,.]+)', linha_posterior)
        if fgts_match:
            try:
                total_fgts += float(fgts_match.group(1).replace('.', '').replace(',', '.'))
            except ValueError:
                if debug:
                    print(f"Erro ao converter valor do FGTS: {fgts_match.group(1)}")
    return total_fgts

def processar_linha_para_inss(linha_atual, linha_anterior, total_inss):
    if "Saldo à recolher:" in linha_atual:
        inss_match = re.search(r'([\d,.]+)', linha_anterior)
        if inss_match:
            try:
                total_inss += float(inss_match.group(1).replace('.', '').replace(',', '.'))
            except ValueError:
                if debug:
                    print(f"Erro ao converter valor do INSS: {inss_match.group(1)}")
    return total_inss

def capturar_data_apos_texto(linhas, chave, debug):
    for i in range(len(linhas)):
        if chave in linhas[i] and i < len(linhas) - 1:
            data_match = re.search(r'\b(\d{2})[-/](\d{2})[-/](\d{4})\b', linhas[i + 1])
            if data_match:
                data = data_match.group(0).strip()
                if debug:
                    print(f"{chave} encontrada: {data}")
                return data
    return None

def capturar_competencia_apos_texto(linhas, chave, debug):
    for i in range(len(linhas)):
        if chave in linhas[i] and i < len(linhas) - 1:
            competencia_match = re.search(r'([\d]+)', linhas[i + 1])
            if competencia_match:
                competencia = competencia_match.group(0).strip()
                if debug:
                    print(f"{chave} encontrada: {competencia}")
                return competencia
    return None

def extrair_dados_empresa(pagina, dados_gerais):
    nome_empresa_rect = fitz.Rect(mm_to_points(30), mm_to_points(0), mm_to_points(150), mm_to_points(4.2))
    ident_rect = fitz.Rect(mm_to_points(30), mm_to_points(4.4), mm_to_points(85), mm_to_points(8.7))

    nome_empresa = pagina.get_text("text", clip=nome_empresa_rect).strip()
    ident_text = pagina.get_text("text", clip=ident_rect).strip()

    empresa_match = re.search(r'(\d+)\s*-\s*(.*)', nome_empresa)
    cnpj_match = re.search(r'([\d.\-/]+)', ident_text)

    if empresa_match and cnpj_match:
        empresa_id = empresa_match.group(1).strip()
        nome_empresa = empresa_match.group(2).strip()
        cnpjcpf = cnpj_match.group(1).strip()

        if nome_empresa not in dados_gerais:
            dados_gerais[nome_empresa] = inicializar_dados_empresa(empresa_id, nome_empresa, cnpjcpf)
    return nome_empresa

def processar_pdf(arquivo_pdf):
    with fitz.open(arquivo_pdf) as pdf:
        dados_gerais = {}

        for pagina_num in range(len(pdf)):
            pagina = pdf.load_page(pagina_num)
            nome_empresa = extrair_dados_empresa(pagina, dados_gerais)

            if nome_empresa:
                texto = pagina.get_text("text")
                print(texto)
                linhas = texto.splitlines()

                if debug:
                    print(f"\n--- Texto extraído da página {pagina_num + 1} ---\n")
                    print(texto)

                total_fgts = 0.0
                total_inss = 0.0
                competencia = capturar_competencia_apos_texto(linhas, "Competência:", debug)
                emissao = capturar_data_apos_texto(linhas, "Emissão:", debug)

                for i in range(len(linhas)):
                    linha_atual = linhas[i]
                    linha_posterior = linhas[i + 1] if i < len(linhas) - 1 else ""
                    linha_anterior = linhas[i - 1] if i > 0 else ""

                    total_fgts = processar_linha_para_fgts(linha_atual, linha_posterior, total_fgts)
                    total_inss = processar_linha_para_inss(linha_atual, linha_anterior, total_inss)

                if competencia:
                    dados_gerais[nome_empresa]['competencia'] = competencia
                if emissao:
                    dados_gerais[nome_empresa]['emissao'] = emissao

                if total_inss == 0.0:
                    for i in range(1, len(linhas)):
                        if "Total INSS:" in linhas[i] and i > 0:
                            linha_anterior = linhas[i - 1]

                            inss_total_match = re.search(r'([\d,.]+)', linha_anterior)
                            if inss_total_match:
                                try:
                                    total_inss = float(inss_total_match.group(1).replace('.', '').replace(',', '.'))
                                except ValueError:
                                    if debug:
                                        print(f"Erro ao converter valor do Total INSS: {inss_total_match.group(1)}")
                            break

                dados_gerais[nome_empresa]['fgts_total'] += total_fgts
                dados_gerais[nome_empresa]['inss_total'] += total_inss

        for empresa in dados_gerais:
            if re.search(r'\b\d{11}\b', empresa):
                dados_gerais[empresa]['total_geral'] = dados_gerais[empresa]['fgts_total'] + dados_gerais[empresa]['inss_total']

        return dados_gerais

def salvar_dados_json(dados, nome_arquivo=f"JSON/{datetime.now().strftime('%d%m%Y_H%M%S')}.json"):
    json_dados = json.dumps(dados, indent=4, ensure_ascii=False)
    print(json_dados)
    with open(nome_arquivo, "w", encoding="utf-8") as json_file:
        json_file.write(json_dados)

def execJSON():
    arquivo_pdf = obter_arquivo_pdf()
    if arquivo_pdf:
        dados_gerais = processar_pdf(arquivo_pdf)
        salvar_dados_json(dados_gerais)
    else:
        print("Nenhum arquivo selecionado.")
    return dados_gerais

# Executa o script principal
if __name__ ==  "__main__":
    execJSON()