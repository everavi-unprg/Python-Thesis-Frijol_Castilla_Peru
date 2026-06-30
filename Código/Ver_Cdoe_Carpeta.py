import pandas as pd
import glob
import os

# 1. Detección automática de la ruta (Rutas Relativas)

# A. Detectar dónde está este archivo de código (Carpeta "Código")
# Nota: Si estás ejecutando esto en un Jupyter Notebook (.ipynb), usa: carpeta_codigo = os.getcwd()
carpeta_codigo = os.path.dirname(os.path.abspath(__file__))

# B. Retroceder una carpeta para llegar al directorio principal (Donde están Código, Data, Tesis)
carpeta_principal = os.path.dirname(carpeta_codigo)

# C. Entrar a la carpeta Data y armar la ruta final de búsqueda
# os.path.join se encarga de poner los slashes correctos ( \ o / ) dependiendo de si usas Windows o Mac
ruta_busqueda = os.path.join(carpeta_principal, "Data", "Exportaciones por año-Azatrade", "*.xlsx")

archivos_excel = glob.glob(ruta_busqueda)
print(f"Se encontraron {len(archivos_excel)} archivos. En la ruta {ruta_busqueda}")
