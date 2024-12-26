import fitz
from ResumoJSON import execJSON
import re
import difflib
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilenames


def searchText(file, search):
    search = search.casefold()
    with fitz.open(file) as pdf:
        for page in range(0, len(pdf)):
            pagina = pdf.load_page(page)
            texto = pagina.get_text("text")
            texto = texto.casefold()

            # Verifica se o texto está presente na página
            if search in texto:
                return True

    # Se não encontrar o texto em nenhuma página
    return False


def locate(coord, page):
    clip_rect = fitz.Rect(coord)
    texto_encontrado = page.get_text("text", clip=clip_rect)
    if texto_encontrado:
        return texto_encontrado
    else:
        return None


def getINSS(file):
    with fitz.open(file) as pdf:
        page = pdf.load_page(0)

        coord_valor = (450.0, 201.0, 556.0, 217.0)
        coord_nome = (150, 132.53, 502.14, 144.82)

        return locate(coord_nome, page).strip(), float(
            locate(coord_valor, page).replace('.', '').replace(',', '.').strip())


def getFGTS(file):
    with fitz.open(file) as pdf:
        page = pdf.load_page(0)

        coord_valor = (425.18, 147.42, 570.01, 169.57)
        coord_nome = (155.0, 108.0, 590.00, 132.92)

        nome = locate(coord_nome, page)
        nome = nome[nome.find('\n') + 1:]
        nome = nome[:nome.find('\n')]
        print(nome)

        return nome, float(
            locate(coord_valor, page).replace('.', '').replace(',', '.').strip())


def find_best_match(input_text, possible_texts):
    input_text = input_text.casefold()
    possible_texts_normalized = [text.casefold() for text in possible_texts]
    matches = difflib.get_close_matches(input_text, possible_texts_normalized, n=1)
    if matches:
        # Retorna o nome original correspondente ao match
        return possible_texts[possible_texts_normalized.index(matches[0])]
    return None


def execCheck():
    def initResponse(nomeEmpresa, inss_dominio, fgts_dominio):
        # tipo = None
        # guiaCorretaInss = False
        # guiaCorretaFgts = False
        #
        # if valorGuiaInss:
        #     diffGuiaInss = abs(valorGuiaInss - inss_total)
        #     if diffGuiaInss <= 0.1:
        #         guiaCorretaInss = True
        # elif valorGuiaFgts:
        #     diffGuiaFgts = abs(valorGuiaFgts - fgts_total)
        #     if diffGuiaFgts <= 0.1:
        #         guiaCorretaFgts = True

        return {
            "correto": False,
            "inss": {
                "guiaCorreta": False,
                "valorGuia": 0.0,
                "valorDominio": inss_dominio,
                "valorDiff": 0.0
            },
            "fgts": {
                "guiaCorreta": False,
                "valorGuia": 0.0,
                "valorDominio": fgts_dominio,
                "valorDiff": 0.0
            }
        }

    Tk().withdraw()  # Oculta a janela principal do tkinter
    files = askopenfilenames(
        filetypes=[("Arquivos PDF", "*.pdf")],
        title="Guias Para Conferência",
        initialdir="C:/Users/nelso/Downloads"
    )

    JSON = execJSON()
    CheckJSON = {}

    for i in files:
        inss = False
        fgts = False
        if searchText(i, "FGTS DIGITAL"):
            nomeGuia, valorGuia = getFGTS(i)
            fgts = True
        elif searchText(i, "CP SEGURADOS"):
            nomeGuia, valorGuia = getINSS(i)
            inss = True

        listaEmpresas = list(JSON.keys())
        empresa = find_best_match(nomeGuia, listaEmpresas)

        if empresa:
            guiaCorreta = False

            # print(f'nome: {nomeGuia}, \nmatch: {empresa}\n')
            inss_dominio = JSON[empresa]['inss_total']
            fgts_dominio = JSON[empresa]['fgts_total']

            if empresa not in CheckJSON:
                CheckJSON[empresa] = initResponse(empresa, inss_dominio, fgts_dominio)

            if inss:
                valorDiff = round(abs(inss_dominio - valorGuia), 2)
                if abs(inss_dominio - valorGuia) <= 0.1:
                    guiaCorreta = True
                CheckJSON[empresa]['inss']['guiaCorreta'] = guiaCorreta
                CheckJSON[empresa]['inss']['valorGuia'] += valorGuia
                CheckJSON[empresa]['inss']['valorDiff'] += valorDiff
            elif fgts:
                valorDiff = round(abs(fgts_dominio - valorGuia), 2)
                if abs(fgts_dominio - valorGuia) <= 0.1:
                    guiaCorreta = True
                CheckJSON[empresa]['fgts']['guiaCorreta'] = guiaCorreta
                CheckJSON[empresa]['fgts']['valorGuia'] += valorGuia
                CheckJSON[empresa]['fgts']['valorDiff'] += valorDiff

    for empresa in CheckJSON:
        inss_dominio = JSON[empresa]['inss_total']
        fgts_dominio = JSON[empresa]['fgts_total']

        diffInss = abs(inss_dominio - CheckJSON[empresa]['inss']['valorGuia'])
        diffFgts = abs(fgts_dominio - CheckJSON[empresa]['fgts']['valorGuia'])
        if diffInss <= 0.1:
            CheckJSON[empresa]['inss']['guiaCorreta'] = True
        if diffFgts <= 0.1:
            CheckJSON[empresa]['fgts']['guiaCorreta'] = True

        if re.match(r'([a-zA-Z ]+\d{11})', empresa):
            MEI = fgts_dominio + inss_dominio
            diffMEI = abs(CheckJSON[empresa]['inss']['valorGuia'] - MEI)
            # print(empresa)
            # print(f"total dominio = {MEI}"
            #       f"\nvalorGuia = {CheckJSON[empresa]['inss']['valorGuia']}")
            # print(f"diffMEI = {diffMEI}")

            if diffMEI <= 0.1:
                CheckJSON[empresa]['inss']['guiaCorreta'] = True
                CheckJSON[empresa]['fgts']['guiaCorreta'] = True

        if CheckJSON[empresa]['inss']['guiaCorreta'] and CheckJSON[empresa]['fgts']['guiaCorreta']:
            CheckJSON[empresa]['correto'] = True

    print(f"\n---------------------------------------\n")
    # print(f"\n{CheckJSON}")

    for idx, empresa in enumerate(CheckJSON):
        if CheckJSON[empresa]['correto'] == False:
            print(empresa)
            print(json.dumps(CheckJSON[empresa], indent=4, ensure_ascii=False))
        else:
            print(f"CORRETO - {list(CheckJSON.keys())[idx]}")

    # CheckJSON = json.dumps(CheckJSON, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    execCheck()