from copy import copy
from pathlib import Path
import shutil
import zipfile
import openpyxl

INPUT = Path(r"C:\Users\sammt\OneDrive\Área de Trabalho\modelo_importacao_apoiadores.xlsx")
OUTPUT = Path(r"C:\Users\sammt\OneDrive\Documentos\ClimaPrevV3\climaprev-atualiza-ao-geral\importacao_apoiadores_LEVA04.xlsx")

def rec(nome, sexo, titulo="", secao="", zona="", endereco="", n_casa="", cep="", bairro="", telefone="", complemento=""):
    return {"NOME": nome, "SEXO": sexo, "N TÍTULO": titulo, "SEÇÃO": secao, "ZONA": zona,
            "ENDEREÇO": endereco, "N CASA": n_casa, "CEP": cep, "COMPLEMENTO": complemento,
            "BAIRRO": bairro, "TELEFONE": telefone}

rows = [
    rec("BEATRIZ MELISSA DE OLIVEIRA DA SILVA", "FEMININO", "086908061384", "0310", "095", "TV. ANTONIO BERENDONA", "1780", "66083051", "PEDREIRA", "91998281943"),
    rec("MARCELO MARQUES DE OLIVEIRA", "MASCULINO", "057564841317", "0143", "095", "TV. ANTONIO BERENDONA", "1780", "66083051", "PEDREIRA", "91983206225 / 91999424191"),
    rec("SUENE OLIVEIRA VASCONCELOS", "FEMININO", "037160371309", "0085", "095", "TV. TIMBO", "1658", "66083051", "PEDREIRA", "91983280001"),
    rec("FRANCIEL SILVA DE PAULA", "MASCULINO", "041751871368", "0286", "095", "TV. TIMBO", "1658", "66083051", "PEDREIRA", "91998204802"),
    rec("VALDETE NUNES MONTEIRO", "FEMININO", "039379231309", "0065", "095", "TV. TIMBO", "1664", "66083051", "PEDREIRA", "91980139482"),

    rec("JOLYTHA ISUANDRA C. BAIA", "FEMININO", "086987851325", "0293", "095", "PASSAGEM 22 DE NOVEMBRO", "51", "66085460", "PEDREIRA", "981609701"),
    rec("ANA LUIZA C. BAIA", "FEMININO", "045196921333", "0374", "095", "PASSAGEM 22 DE NOVEMBRO", "51", "66085460", "PEDREIRA", "981067746"),
    rec("REINALDO FERREIRA DO ROSARIO", "MASCULINO", "037340551376", "0134", "095", "TRAVESSA TIMBO", "1670", "6608-654", "PEDREIRA", "980123661", "F"),
    rec("ANALICE CARNEIRO BAIA", "FEMININO", "054019771309", "0056", "095", "PASSAGEM 22 DE NOVEMBRO", "51", "66085460", "PEDREIRA", "91993495484"),
    rec("MANOELI CAROLINA DOS SANTOS", "FEMININO", "059088871376", "0046", "095", "TRAVESSA TIMBO, PASSAGEM OTILIA", "58", "66085652", "PEDREIRA", "91980245008"),

    rec("DIONE SOCORRO ALVES BAIA", "FEMININO", "011042911350", "0073", "095", "PASSAGEM ALVARO ADOLFO", "70", "66085030", "PEDREIRA", "980501708"),
    rec("MARIA REGINA CARNEIRO BAIA", "FEMININO", "054019791368", "0048", "095", "AV. TIMBO", "1915", "66095028", "MARCO", "9198054164"),
    rec("CRISTIANE DOS SANTOS DUARTE", "FEMININO", "028573813325", "0109", "095", "TV. TIMBO, PASS. OTILIA", "58", "66085652", "PEDREIRA", "91983358363"),
    rec("LUIZA RAFAELLE BAIA DE SOUZA", "FEMININO", "052478284333", "0133", "095", "PASSAGEM 22 DE NOVEMBRO", "51", "66085460", "PEDREIRA", "91981701144"),
    rec("ALBERT GABRIEL CASTRO MORAES", "MASCULINO", "091681193376", "0317", "095", "TV. PINANGI", "15", "66083541", "PEDREIRA", "91980110497"),

    rec("CLAUDIO ALAN MACHADO", "MASCULINO", "032877861395", "0131", "095", "AVENIDA VISCONDE DE INHAUMA", "17", "66085733", "PEDREIRA", "982789897"),
    rec("ANA LUCIA C. B.", "FEMININO", "038041861333", "0134", "095", "AVENIDA VISCONDE DE INHAUMA", "17", "66085733", "PEDREIRA", "987495935"),
    rec("ANA CRISTINA C. BAIA", "FEMININO", "065307313350", "0139", "095", "PASSAGEM 22 DE NOVEMBRO", "51", "66085460", "PEDREIRA", "981432396"),
    rec("ANA CLARA BAIA MACHADO", "FEMININO", "086994871350", "0107", "095", "AVENIDA VISCONDE DE INHAUMA", "17", "66085733", "PEDREIRA", "988650565"),
    rec("ANDRE LUIZ C. BAIA", "MASCULINO", "033519913350", "0131", "095", "PASS. ALVARO ADOLFO", "70", "66085030", "PEDREIRA", "993733381"),

    rec("WORLISSON PAULO AMARAL GOUVEIA", "MASCULINO", "064249493325", "0337", "096", "AVENIDA VISCONDE DE INHAUMA", "17", "66085733", "PEDREIRA", "9198327197", "B"),
    rec("GUILIANE DO SOCORRO DA CRUZ COSTA", "FEMININO", "050105711309", "0087", "095", "TRAVESSA PRACA", "15", "66083541", "PEDREIRA", "9198253258"),
    rec("ADRIANA DA CONCEICAO QUEIROS", "FEMININO", "057050141376", "0178", "095", "TRAVESSA PRACA", "15", "66083541", "PEDREIRA", "91986441255"),
    rec("SONIA ALVES DA SILVA", "FEMININO", "069603701376", "0045", "001", "AV. PRESIDENTE VARGAS", "560", "66017000", "CAMPINA", "983149813"),
    rec("SAMARA ALVES DA SILVA", "FEMININO", "065562721309", "0094", "096", "TV. CASTELO BRANCO", "2336", "66063223", "GUAMA", "998016293"),

    rec("AMANDA LUCIA CARNEIRO BAIA", "FEMININO", "059084951325", "0105", "095", "AV. VISCONDE DE INHAUMA", "17", "66085733", "PEDREIRA", "9198246313", "CASA B"),
    rec("RAFAEL DA SILVA LOBO", "MASCULINO", "073079481392", "0495", "001", "RUA DOS MUNDURUCUS", "255", "66030680", "JURUNAS", "91981639231"),
    rec("RUAN MIKAEL DA COSTA", "MASCULINO", "091674891317", "0065", "095", "PASSAGEM ALVARO ADOLFO", "67", "66085030", "PEDREIRA", "91982165370"),
    rec("MARIA DE LOURDES CORREA COSTA", "FEMININO", "017706641376", "0105", "095", "ALAMEDA DA CONQUISTA", "60", "66085030", "PEDREIRA", "91982064249"),
    rec("MICHAEL RUAN BAIA", "MASCULINO", "085098871368", "0297", "095", "TRAVESSA TIMBO", "1915", "66095128", "MARCO", "91982853439"),
    rec("OLIVANDO COUTINHO JUNIOR", "MASCULINO", "034242921392", "0106", "095", "TRAVESSA TIMBO", "1915", "66095308", "MARCO", "91920062571"),
]

assert len(rows) == 31, len(rows)

with zipfile.ZipFile(INPUT) as zf:
    bad = [n for n in zf.namelist() if any(x in n.lower() for x in ("vbaproject", "macros", "activex", "ctrlprops"))]
if bad:
    raise RuntimeError(f"Modelo contém macros: {bad}")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(INPUT, OUTPUT)
wb = openpyxl.load_workbook(OUTPUT, keep_vba=False)
ws = wb[wb.sheetnames[0]]
headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
style_values = []
for c in range(1, ws.max_column + 1):
    cell = ws.cell(2, c)
    style_values.append((copy(cell._style), cell.number_format, copy(cell.font), copy(cell.fill), copy(cell.border), copy(cell.alignment), copy(cell.protection)))
row_height = ws.row_dimensions[2].height
ws.delete_rows(2, ws.max_row - 1)
for data in rows:
    ws.append([data.get(str(headers[c - 1]), "") if headers[c - 1] is not None else "" for c in range(1, ws.max_column + 1)])

header_index = {str(v): i + 1 for i, v in enumerate(headers) if v is not None}
text_cols = {header_index.get(x) for x in ("N TÍTULO", "SEÇÃO", "ZONA", "N CASA", "CEP")}
for r in range(2, ws.max_row + 1):
    if row_height is not None:
        ws.row_dimensions[r].height = row_height
    for c in range(1, ws.max_column + 1):
        cell = ws.cell(r, c)
        st, nf, font, fill, border, alignment, protection = style_values[c - 1]
        cell._style = copy(st)
        cell.number_format = "@" if c in text_cols else nf
        cell.font, cell.fill, cell.border = copy(font), copy(fill), copy(border)
        cell.alignment, cell.protection = copy(alignment), copy(protection)
wb.save(OUTPUT)

with zipfile.ZipFile(OUTPUT) as zf:
    final_bad = [n for n in zf.namelist() if any(x in n.lower() for x in ("vbaproject", "macros", "activex", "ctrlprops"))]
if final_bad:
    raise RuntimeError(f"Arquivo final contém macros: {final_bad}")
check = openpyxl.load_workbook(OUTPUT, read_only=True)
assert check.active.max_row == 32 and check.active.max_column == 32
print(f"created={OUTPUT}; rows=31; columns=32; macros=[]")
