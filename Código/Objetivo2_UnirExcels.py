import pandas as pd
import os
import glob
import warnings

warnings.filterwarnings('ignore')

ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
#link_dato = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-AdexDatatrade"
link_dato = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-AdexDatatrade")
# 1. Vemos link
carpeta_salida = os.path.join(link_dato,'Resultados_Consolidados')

if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

grupos = {
    "Unido_Lambayeque_Agro": "Sectores_Lambayeque_*.xlsx",
    "Unido_Piura_Agro":"Sectores_Piura_*.xlsx",
    "Unido_Peru_Agro":"Sectores_Per*_*.xlsx",
    "Unido_Peru_Frijol":"Partida_Per*_*.xlsx"
}

print("INICIANDO UNIÓN FINAL...")
# 2. Desde el 2012-2023
def leer_historico(ruta_archivo, tipo_dato):
    try:
        df_raw = pd.read_excel(ruta_archivo, header=None)        
        # Buscar fila de años
        index_años = -1
        col_indices = []
        for i, row in df_raw.head(30).iterrows():
            matches = []
            for c, val in enumerate(row):
                s = str(val).replace('.0','').strip()
                # Excluimos 2024 para trabajarlo más adelante
                if s.isdigit() and len(s)==4 and s.startswith('20') and s != "2024":
                    matches.append(c)
            if len(matches) >= 1 :
                index_años = i;col_indices=matches; break
        if index_años == -1: return pd.DataFrame()

        index_categorias = index_años - 1
        categorias = df_raw.iloc[index_categorias].astype(str).tolist()
        años = df_raw.iloc[index_años].tolist()
        categorias_lista = []
        last = ""
        for x in categorias:
            if x.lower() != 'nan': last = x
            categorias_lista.append(last)
            
        mapa = []
        for c in col_indices:
            anio = str(años[c]).replace('.0','').strip()
            cat = categorias_lista[c].upper()
            tipo = "Valor_FOB" if "FOB" in cat or "VALOR" in cat else ("Peso_Kg" if "PESO" in cat or "KG" in cat else "SKIP")
            if tipo != "SKIP": mapa.append({'col': c, 'anio': anio, 'tipo': tipo})

        # Buscar Data
        df_data = df_raw.iloc[index_años+1:]
        target_row = None
        for i, row in df_data.iterrows():
            txt = row.astype(str).str.cat(sep=' ').upper()
            if "Frijol" in tipo_dato:
                if "0713" in txt: target_row = row; break
                if "TOTAL" in txt and "TRADICIONAL" not in txt and target_row is None: target_row = row
            else:
                if "AGROPECUARIO" in txt and "AGROINDUSTRIAS" in txt: target_row = row; break
                
        if target_row is None: return pd.DataFrame()
        
        res = {}
        for m in mapa:
            a = m['anio']
            if a not in res: res[a] = {'Valor_FOB':0, 'Peso_Kg':0}
            res[a][m['tipo']] = target_row.iloc[m['col']]
            
        lista = []
        for a, v in res.items():
            lista.append({'Año': int(a), 'Valor_FOB': v['Valor_FOB'], 'Peso_Kg': v['Peso_Kg'], 'Fuente': os.path.basename(ruta_archivo)})
        return pd.DataFrame(lista)
    except:
        return pd.DataFrame()

# 3 FUNCIÓN FRIJOL 2024 
def leer_frijol_2024_posicional(ruta_archivo):
    nombre = os.path.basename(ruta_archivo)
    try:
        df_raw = pd.read_excel(ruta_archivo, header=None)
        
        # 1.BUSCAR Donde aparece 2024
        fila_años_index = -1
        cols_2024 = []
        
        for r_idx, row in df_raw.head(30).iterrows():
            matches = []
            for c_idx, val in enumerate(row):
                if "2024" in str(val):
                    matches.append(c_idx)
            
            if len(matches) > 0:
                fila_años_index = r_idx
                cols_2024= matches
                if len(matches)>= 2:
                    break
        
        if fila_años_index== -1:
            print(f"Frijol -> No encontré 2024 en filas de {nombre}")
            return pd.DataFrame()

        # 2 REGLA -> 1ro es FOB, 2do es PESO
        col_fob =cols_2024[0]
        col_peso = cols_2024[1] if len(cols_2024) > 1 else -1 # Si existe una segunda columna con 2024 es Peso Si no error o 0.
        
        #3. ENCONTRAR FILA
        df_data =df_raw.iloc[fila_años_index+1:]
        fila_datos=None
        
        for r_idx, row in df_data.iterrows():
            s = row.astype(str).str.cat(sep=' ').upper()
            if "0713" in s:
                fila_datos=row; break
            if "TOTAL" in s and "TRADICIONAL" not in s and fila_datos is None: # Fallback Total
                fila_datos=row

        if fila_datos is None:
            print(f" No encontré fila de datos en {nombre}")
            return pd.DataFrame()

        # 4- EXTRAemos xd
        val_fob = fila_datos.iloc[col_fob]
        val_peso = fila_datos.iloc[col_peso] if col_peso != -1 else 0
        
        return pd.DataFrame([{
            'Año': 2024 ,
            'Valor_FOB':val_fob,
            'Peso_Kg':val_peso,
            'Fuente':nombre
        }])

    except Exception as e:
        print(f"Error Frijol 2024 {nombre} : {e}")
        return pd.DataFrame()

# 4. FUNCIÓN PARA EL SECTOR 2024 AGRO
def leer_sector_2024(ruta_archivo):
    # buscando fila AGROPECUARIO
    nombre = os.path.basename(ruta_archivo)
    try:
        df_raw = pd.read_excel(ruta_archivo, header=None)
        
        # Buscar fila años
        cols_2024 = []
        fila_años_index = -1
        for r, row in df_raw.head(30).iterrows():
            matches = [ c for c,v in enumerate(row) if "2024" in str(v)]
            if matches:
                cols_2024 =matches; fila_años_index=r
                if len(matches) >= 2: break
        
        if fila_años_index == -1:return pd.DataFrame()
        
        col_fob = cols_2024[ 0 ]
        col_peso = cols_2024[ 1 ] if len(cols_2024) > 1 else -1
        
        # Buscar fila Agro
        fila_datos = None
        for r, row in df_raw.iloc[fila_años_index+1:].iterrows():
            s = row.astype(str).str.cat(sep=' ').upper()
            if "AGROPECUARIO" in s and "AGROINDUSTRIAS" in s:
                fila_datos = row ; break
                
        if fila_datos is None: return pd.DataFrame()
        
        return pd.DataFrame([{
            'Año': 2024,
            'Valor_FOB' : fila_datos.iloc[col_fob],
            'Peso_Kg' : fila_datos.iloc[col_peso] if col_peso != -1 else 0,
            'Fuente':nombre
        }])
    except: return pd.DataFrame()

# 5. EJECUCIÓN
for etiqueta, patron in grupos.items():
    print(f"\nProcesando grupo: {etiqueta}")
    archivos = sorted(glob.glob(os.path.join(link_dato, patron)))
    
    dfs = []
    for arch in archivos:
        nombre = os.path.basename(arch)
        es_2024 = "2024" in nombre and "2023" not in nombre
        
        df = pd.DataFrame()
        if es_2024:
            print(f" MODO 2024: {nombre}")
            if "Frijol" in etiqueta or "Partida" in nombre:
                df = leer_frijol_2024_posicional(arch)
            else:
                df = leer_sector_2024(arch)
        else:
            df = leer_historico(arch, etiqueta)
            
        if not df.empty:
            dfs.append(df)
            
    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
        df_final = df_final.sort_values('Año').drop_duplicates(subset=['Año'], keep='last')
        
        ruta_out = os.path.join(carpeta_salida, f"{etiqueta}_2012-2024.xlsx")
        df_final.to_excel(ruta_out, index=False)
        print(f"CONSOLIDADO OK: {etiqueta}_2012-2024.xlsx")
        print(f"Rango: {df_final['Año'].min()}-{df_final['Año'].max()}")
    else:
        print("ERROR: No se generó data.")

print("\n LISTO! Revisa la carpeta Resultados_Consolidados.")