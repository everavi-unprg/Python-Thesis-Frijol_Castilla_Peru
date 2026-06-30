import pandas as pd
import glob
import os

#1. Buscamos todos los excel
carpeta_codigo = os.path.dirname(os.path.abspath(__file__))
carpeta_principal = os.path.dirname(carpeta_codigo)
link_busqueda = os.path.join(carpeta_principal, "Data", "Exportaciones por año-Azatrade", "*.xlsx")
archivos_excel = glob.glob(link_busqueda)
print(f" Se encontraron {len(archivos_excel)} archivos : {archivos_excel}")

#2-
lista_datos = []

#3-Circutio para leer cada archivo y juntarlos
for archivo in archivos_excel:
    try:
        print(f"Leyendo : {archivo}...")
        df_temporal=pd.read_excel( archivo ) # acá leemos el excel en la primera hoja
        #columna para ver de qué archivo vino
        df_temporal['ARCHIVO_ORIGEN'] = archivo
        lista_datos.append(df_temporal)
    except Exception as e:
        print(f"Error al leer {archivo} : {e}")

# 4. Unir todo en un solo Dataframe (Excel aún todavía) gigante
if lista_datos:
    df_principal = pd.concat(lista_datos, ignore_index=True)
    # A- eviar al excel princiapl
    # Donde está la carpeta donde estaba el primer archivo encontrado
    carpeta_origen= os.path.dirname(archivos_excel[0])

    # B- Creamos la ruta completa (Nueva Carpeta+Nombre Nuevo)
    carpeta_nueva= os.path.join(carpeta_origen, "Resultados_Consolidados")
    # B.1 Crear nueva carpeta
    os.makedirs(carpeta_nueva,exist_ok=True) #exist_ok es cuando el sistema verifica que si existe entonces normal no te da error, si no existe lo crea pues
    # B.2  Link parte final
    nombre_archivo = "Frijol Castilla 2012-2024.xlsx"
    ruta_final= os.path.join(carpeta_nueva,nombre_archivo)

    #C. Guardamos en la ruta completa
    df_principal.to_excel(ruta_final,index=False)

    print("-"*50)
    print(f" ÉXITO!!! Archivo creado: {ruta_final}")
    print(f"Total de filas unidas: {len(df_principal)}")
    print("-"* 50)
else:
    print("No se encontraron datos.")