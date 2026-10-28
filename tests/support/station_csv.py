"""Synthetic annual-station CSV fixture shared by experimental tools tests."""

from datetime import UTC, datetime, timedelta


def station_variables_csv(*, humidity=True, missing=False):
    header = ("REGIAO:;N\nUF:;PA\nESTACAO:;Synthetic\nCODIGO (WMO):;A201\n"
              "LATITUDE:;0\nLONGITUDE:;0\nALTITUDE:;10\nDATA DE FUNDACAO:;2003-01-01\n"
              "Data;Hora UTC;PRECIPITAÇÃO TOTAL, HORÁRIO (mm);VENTO, RAJADA MAXIMA (m/s);"
              "TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C);"
              "TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C);"
              "TEMPERATURA DO AR - BULBO SECO, HORARIA (°C);")
    if humidity:
        header += "UMIDADE RELATIVA DO AR, HORARIA (%);"
    header += "\n"
    for i in range(25):
        stamp = datetime(2024, 1, 2, tzinfo=UTC) + timedelta(hours=i)
        header += f"{stamp:%Y/%m/%d};{stamp:%H%M} UTC;1;2;22;18;20;"
        if humidity:
            header += ("-9999" if missing and i == 4 else "50") + ";"
        header += "\n"
    return header.encode()

