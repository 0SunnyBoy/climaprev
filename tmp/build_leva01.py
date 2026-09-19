from copy import copy
from pathlib import Path
import shutil
import zipfile

import openpyxl


INPUT = Path(r"C:\Users\sammt\OneDrive\Área de Trabalho\modelo_importacao_apoiadores.xlsx")
OUTPUT = Path(r"C:\Users\sammt\OneDrive\Documentos\ClimaPrevV3\climaprev-atualiza-ao-geral\importacao_apoiadores_Leva01.xlsx")


def rec(nome, sexo, titulo="", secao="", zona="", endereco="", n_casa="", cep="", bairro="", telefone="", complemento=""):
    return {
        "NOME": nome,
        "SEXO": sexo,
        "N TÍTULO": titulo,
        "SEÇÃO": secao,
        "ZONA": zona,
        "ENDEREÇO": endereco,
        "N CASA": n_casa,
        "CEP": cep,
        "COMPLEMENTO": complemento,
        "BAIRRO": bairro,
        "TELEFONE": telefone,
    }


rows = [
    rec("KATIA CILENE BARROSO DOS SANTOS", "FEMININO", "050158441392", "0093", "095", "PSS. ALVARO ADOLFO", "212", "66085030", "PEDREIRA", "(91) 98033-6503"),
    rec("GISLA HELICIA DA SILVA NOGUEIRA", "FEMININO", "091675441389", "0049", "095", "PSS. ALVARO ADOLFO", "212", "66085030", "PEDREIRA", "(91) 98600-3761"),
    rec("SILMA NOGUEIRA DA SILVA", "FEMININO", "050025431373", "0107", "095", "PSS. ALVARO ADOLFO", "212", "66085030", "PEDREIRA", "(91) 98968-8134"),
    rec("ERICA KAREN DA SILVA", "FEMININO", "057583001350", "0093", "095", "PSS. ALVARO ADOLFO", "212", "66085030", "PEDREIRA", "(91) 98312-7022"),
    rec("ANDREA RAMON NASCIMENTO GALIZA", "FEMININO", "062696161350", "0132", "095", "PSS. ALVARO ADOLFO", "212", "66085030", "PEDREIRA", "982539603"),

    rec("MESSIAS PEREIRA SILVA", "MASCULINO", "057584091350", "0172", "095", "PASS. ALVARO ADOLFO", "67", "66085030", "PEDREIRA", "980731370"),
    rec("RUAN MIKAEL DA COSTA BEZERRA", "MASCULINO", "091674891317", "0065", "095", "PASS. ALVARO ADOLFO", "67", "66085030", "PEDREIRA"),
    rec("MISSILENE CORREA DA COSTA", "FEMININO", "", "0321", "072", "PASS. ALVARO ADOLFO", "67", "66085030", "PEDREIRA", "982064249"),
    rec("PATRICIA DE ALMEIDA FERREIRA", "FEMININO", "057604781392", "0046", "096", "RUA DIOGO MOIA", "2769", "66060740", "PEDREIRA", "983289010"),
    rec("MARCELA SAMARA DE ALMEIDA", "FEMININO", "", "0216", "095", "RUA DIOGO MOIA", "1769", "66060740", "PEDREIRA", "983195727"),

    rec("HELO COELHO MACIEL JUNIOR", "OUTROS", "067414871376", "0136", "095", "PASS. JOSE MARIA DA COSTA", "73", "66085230", "PEDREIRA", "983067923", "ALTOS"),
    rec("JOCELIA DOS SANTOS", "FEMININO", "", "0079", "095", "PASS. JOSE MARIA DA COSTA", "73", "66085230", "PEDREIRA", "98960973", "ALTOS"),
    rec("CELIA LUIZIN CAMPOS DOS SANTOS", "FEMININO", "079094121390", "0091", "095", "PASS. JOSE MARIA DA COSTA", "73", "66085230", "PEDREIRA", "987062482", "ALTOS"),
    rec("MARIA CRISTINA CAMPOS DOS SANTOS", "FEMININO", "", "0091", "095", "PASS. JOSE MARIA DA COSTA", "73", "66085230", "PEDREIRA", "980682346"),
    rec("ALEX ARIEL SIQUEIRA DOS SANTOS", "OUTROS", "085104111368", "0304", "095", "PASS. JOSE MARIA DA COSTA", "73", "66085230", "PEDREIRA", "986157603"),

    rec("ALEX CAMPOS DA SILVA", "OUTROS", "", "0103", "095", "PASS. JOSE MARIA DA COSTA", "73", "66085230", "PEDREIRA", "980699761"),
    rec("CRISTIANE SANTOS DAS CHAGAS", "FEMININO", "032300441325", "0105", "095", "TV. ANTONIO BAENA", "", "66085230", "PEDREIRA", "989606973"),
    rec("ERICK RAFAEL GOMES DOS SANTOS", "MASCULINO", "019509481805", "0487", "001", "RUA CURUCA", "853", "67013560", "ATALAIA", "980603950"),
    rec("EDIENE GOMES DOS SANTOS", "FEMININO", "060815471376", "0131", "095", "RUA CURUCA", "853", "67013560", "ATALAIA", "980103306"),
    rec("NELSON CIONCIO ALDO DOS SANTOS SIQUEIRA", "MASCULINO", "", "0173", "095", "RUA CURUCA", "853", "67013560", "ATALAIA", "983030449"),

    rec("EDNA SANTANA MARCET RODRIGUES", "FEMININO", "010802521350", "0035", "095", "TV. ANTONIO BAENA", "", "66085051", "PEDREIRA", "982523456"),
    rec("GIANIO GUTEMBERG ALVES LOPES", "MASCULINO", "025195331392", "0094", "095", "TV. ANTONIO BAENA", "402", "66085051", "PEDREIRA", "982523456"),
    rec("DEBORAH SANTANA SOUZA", "FEMININO", "053980714350", "0172", "095", "PASS. ITAMARATI", "107", "66080280", "PEDREIRA", "998268801"),
    rec("CRISTHIANU GABRIEL PASSOS COSTA", "MASCULINO", "080890941368", "0045", "095", "PASS. ITAMARATI", "", "66080280", "PEDREIRA", "998268801"),
    rec("MARIA DA GLORIA SILVA DO NASCIMENTO", "FEMININO", "010995177309", "", "", "PASS. SAO JOSE", "", "", "PEDREIRA", "", "CASA"),

    rec("SAMANTHA DE FATIMA ALVES AMARAL", "FEMININO", "074783771338", "0128", "095", "TV. CURUZU VILA SANTA MARIA", "14", "66085710", "PEDREIRA", "984617965"),
    rec("HELOISA DIAS DA SILVA", "FEMININO", "040553711333", "0106", "095", "PASS. JOSE MARIA DA COSTA", "67", "66085230", "PEDREIRA", "982242532"),
    rec("GUILHERME VIEIRA PINTO NETO", "MASCULINO", "", "0177", "095", "PASS. JOSE MARIA DA COSTA", "67", "66085230", "PEDREIRA", "982242532"),
    rec("LUCIELEIDE DIAS ARAUJO", "FEMININO", "044917909133", "0097", "095", "PASS. JOSE MARIA DA COSTA", "74", "66085230", "PEDREIRA", "993338771"),
    rec("ROSEMARY APARECIDA SILVA", "FEMININO", "", "0184", "095", "PASS. JOSE MARIA DA COSTA", "92", "66085230", "PEDREIRA", "98606542"),

    rec("CLEBER DOS SANTOS DIAS", "MASCULINO", "037645113333", "0293", "095", "PASS. ALVARO ADOLFO", "01", "66085030", "PEDREIRA", "99357747"),
    rec("ANA MARIA ALVES PINTO", "FEMININO", "012370141325", "0180", "095", "AV. MARQUES DE HERVAL", "53", "66085030", "PEDREIRA", "98358323"),
    rec("MARLENE DOS SANTOS DIAS", "FEMININO", "050841081368", "0107", "095", "TV. CURUZU", "99", "66085710", "PEDREIRA", "998268801", "CASA 8"),
    rec("GEANY SANTANA MARCET RODRIGUES", "FEMININO", "010802521350", "0035", "095", "TV. ANTONIO BAENA", "402", "66085051", "PEDREIRA", "982523456"),
    rec("ELDER HENRIQUE MACIEL DA SILVA", "MASCULINO", "064431221333", "0130", "095", "TV. ANTONIO BAENA", "402", "66085051", "PEDREIRA", "982523456"),

    rec("VANESSA DA SILVA SANTOS", "FEMININO", "052566011833", "0126", "095", "AV. MARQUES DE HERVAL", "30", "66085052", "PEDREIRA", "980512462"),
    rec("RUTH HELENA DA SILVA GOMES", "FEMININO", "", "0095", "095", "AV. MARQUES DE HERVAL", "", "66085052", "PEDREIRA", "998316987"),
    rec("ALAN CARLOS SILVA MORAES", "MASCULINO", "019509481805", "0487", "001", "RUA CURUCA", "853", "67013560", "ATALAIA", "982337001"),
    rec("RAFAELA PRISCILA RODRIGUES SARAIVA", "FEMININO", "064438961311", "0135", "095", "PASS. DA CONQUISTA", "43", "66085460", "PEDREIRA", "982232105"),
    rec("KATIA CILENE DE SOUZA MACIEL", "FEMININO", "024117937136", "0126", "095", "AVENIDA ESPERANCA", "", "66085320", "OUTEIRO", "993256435"),

    rec("CASSIO EDUARDO DIAS ARAUJO", "MASCULINO", "085701333384", "0309", "095", "PASS. JOSE MARIA DA COSTA", "74", "66085230", "PEDREIRA", "989566640"),
    rec("VITORIA RAQUEL MENEZES ALMEIDA", "FEMININO", "091679651368", "0374", "095", "PASS. JOSE MARIA DA COSTA", "74", "66085230", "PEDREIRA", "989566640"),
    rec("RAFAEL SOUZA MIRANDA", "MASCULINO", "064432581309", "0121", "095", "PASS. JOSE MARIA DA COSTA", "68", "66085230", "PEDREIRA", ""),
    rec("FATIMA VALERIA CARNEIRO CORREA", "FEMININO", "037462651325", "0105", "095", "PASS. FREITAS", "63", "", "PEDREIRA", "987001251"),
    rec("JOELSON JOSE SILVA SANTOS", "MASCULINO", "074770901309", "0285", "095", "TV. ANTONIO BAENA", "50", "66085050", "", "998400764"),
]


assert len(rows) == 45, len(rows)

with zipfile.ZipFile(INPUT) as zf:
    macro_entries = [n for n in zf.namelist() if any(x in n.lower() for x in ("vbaproject", "macros", "activex", "ctrlprops"))]
if macro_entries:
    raise RuntimeError(f"Modelo contém entradas relacionadas a macro: {macro_entries}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(INPUT, OUTPUT)
wb = openpyxl.load_workbook(OUTPUT, keep_vba=False)
ws = wb[wb.sheetnames[0]]

headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
header_index = {str(v): i + 1 for i, v in enumerate(headers) if v is not None}
style_row = 2
style_values = []
for c in range(1, ws.max_column + 1):
    cell = ws.cell(style_row, c)
    style_values.append((copy(cell._style), cell.number_format, copy(cell.font), copy(cell.fill), copy(cell.border), copy(cell.alignment), copy(cell.protection)))
row_height = ws.row_dimensions[style_row].height
if ws.max_row >= 2:
    ws.delete_rows(2, ws.max_row - 1)

for data in rows:
    ws.append([data.get(str(headers[c - 1]), "") if headers[c - 1] is not None else "" for c in range(1, ws.max_column + 1)])

for r in range(2, ws.max_row + 1):
    if row_height is not None:
        ws.row_dimensions[r].height = row_height
    for c in range(1, ws.max_column + 1):
        cell = ws.cell(r, c)
        st, numfmt, font, fill, border, alignment, protection = style_values[c - 1]
        cell._style = copy(st)
        cell.number_format = numfmt
        cell.font = copy(font)
        cell.fill = copy(fill)
        cell.border = copy(border)
        cell.alignment = copy(alignment)
        cell.protection = copy(protection)
        if c in (header_index.get("N TÍTULO"), header_index.get("SEÇÃO"), header_index.get("ZONA"), header_index.get("N CASA"), header_index.get("CEP")):
            cell.number_format = "@"

wb.save(OUTPUT)

with zipfile.ZipFile(OUTPUT) as zf:
    final_macro_entries = [n for n in zf.namelist() if any(x in n.lower() for x in ("vbaproject", "macros", "activex", "ctrlprops"))]
if final_macro_entries:
    raise RuntimeError(f"Arquivo final contém entradas relacionadas a macro: {final_macro_entries}")

check = openpyxl.load_workbook(OUTPUT, read_only=True, data_only=False)
check_ws = check[check.sheetnames[0]]
assert check_ws.max_row == 46 and check_ws.max_column == 32
print(f"created={OUTPUT}")
print(f"rows={check_ws.max_row - 1}, columns={check_ws.max_column}, macros={final_macro_entries}")
