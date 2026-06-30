import pandas as pd
import os


# 1 Links
ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
##ruta_origen_obj1 = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-Azatrade\Resultados_Consolidados"
ruta_origen_obj1 = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados")
archivo_obj1 = "Objetivo_1_Resultados.xlsx"

##ruta_destino_adex = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-AdexDatatrade\Resultados_Consolidados"
ruta_destino_adex = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-AdexDatatrade","Resultados_Consolidados")
archivo_bloque_b = "Bloque_B_Macro_Data.xlsx"
nombre_archivo_final = "DB_Final_Objetivo2_BalassayPriceGap.xlsx"

print("INICIANDO MATRIZ FINAL PARA BALASSA...")
print(f"Origen Datos(Obj 1): ...\\Azatrade\\Resultados_Consolidados")
print(f"Origen Macros y Destino Final:   ...\\AdexDatatrade\\Resultados_Consolidados")
print("-"*60)

try:
    link_obj1 = os.path.join(ruta_origen_obj1, archivo_obj1)
    if not os.path.exists(link_obj1):
        raise FileNotFoundError(f"No encuentro el archivo del Objetivo 1 en: {link_obj1}")
        
    print(f"Leyendo Detalle Frijol (Obj 1)...")
    df_obj1 = pd.read_excel(link_obj1)
    
    df_obj1.columns = [c.upper().strip() for c in df_obj1.columns]

    col_año=  next(c for c in df_obj1.columns if "AÑO" in c)
    col_dpto=next(c for c in df_obj1.columns if "DEPARTAMENTO" in c)
    col_fob= next(c for c in df_obj1.columns if "FOB" in c)
    col_peso = next(c for c in df_obj1.columns if "PESO" in c or "KG" in c)

    # Filtraremo solo Lambayeque y Piura
    df_filt = df_obj1[df_obj1[col_dpto].isin(['LAMBAYEQUE', 'PIURA'])].copy()
    
    # para trasladar de filas a columans y al revés
    df_pivot =df_filt.pivot_table(index=col_año,columns=col_dpto, values=[ col_fob,col_peso ], aggfunc= 'sum').reset_index()

    # solo formato de nombre por ejem -> Frijol_FOB_Lambayeque
    new_cols = ['Año']
    for nivel1, nivel2 in df_pivot.columns[1:]:
        tipo = "FOB" if col_fob in nivel1 else "Kg"
        region = nivel2.title()
        new_cols.append(f"Frijol_{tipo}_{region}")
    
    df_pivot.columns = new_cols
    df_pivot['Año'] = df_pivot['Año'].astype(int)
    print("Datos de Objetivo 1 procesados correctamente.")

    # 2Cargar bloque desde AdexDatatrade
    path_bloque_b = os.path.join(ruta_destino_adex , archivo_bloque_b)
    if not os.path.exists(path_bloque_b):
        raise FileNotFoundError(f"No encuentro el Bloque B en: {path_bloque_b}")
        
    print(f"Leyendo Datos Macro (Bloque B)...")
    df_bloque_b = pd.read_excel(path_bloque_b)
    df_bloque_b['Año'] =df_bloque_b['Año'].astype(int)
    print("Datos macro cargados.")

    # 3. Unión AdexDatatrade usando el Año
    df_final = pd.merge(df_pivot, df_bloque_b, on='Año', how='left')

    # Reordenar columnas primero año, luego frijoles,luego totales macro
    cols_ordenadas = ['Año']+\
                     [c for c in df_final.columns if 'Frijol' in c]+\
                     [c for c in df_final.columns if 'Total' in c]
    
    df_final= df_final[cols_ordenadas]

    path_salida = os.path.join(ruta_destino_adex, nombre_archivo_final)
    df_final.to_excel(path_salida, index=False)

    print("-"*60)
    print(f"Guardado en:\n{path_salida}")
    print("\nEsta tabla 'Resultados_Objetivo2_Balassa.xlsx' contiene:")
    print("1. Exportaciones Frijol Lambayeque/Piura (Obj 1)")
    print("2. Totales Agropecuarios Regionales (Obj 2)")
    print("3. Totales Nacionales (Obj 2)")
    print("4. Datos completos hasta el 2024")

except Exception as e:
    print(f"\n ERROR: {e}")