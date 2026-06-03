from pydataxm.pydataxm import ReadDB
from datetime import datetime
import pandas as pd

print("Conectando con XM...")
obj = ReadDB()

print("Descargando datos de embalses 2010-2025...")
df = obj.request_data(
    "NivelEmbalsesVolumeUtil",
    "Sistema",
    datetime(2010, 1, 1),
    datetime(2025, 6, 1)
)

print("Primeras filas:")
print(df.head(10))
print("\nColumnas:", df.columns.tolist())
print("Shape:", df.shape)

df.to_csv("data/embalses_historico.csv", index=False)
print("\nArchivo guardado en data/embalses_historico.csv")