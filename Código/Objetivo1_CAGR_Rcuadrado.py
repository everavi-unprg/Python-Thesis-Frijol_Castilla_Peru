import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os  # Librería necesaria para poder manejar rutas de carpetas
# 1 Cargar los datos
ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
path_archivo = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Frijol Castilla 2012-2024.xlsx")
path_archivo=os.path.normpath(path_archivo)
##path_archivo= r"c:/Users/jeffe/OneDrive/Desktop/Frijoles/Frijol Castilla/Data/Exportaciones por año-Azatrade/Resultados_Consolidados/Frijol Castilla 2012-2024.xlsx"
df= pd.read_excel(path_archivo)

# 2- Filtrar y hacer limpieza
regiones =['LAMBAYEQUE','PIURA']
df_filtrada = df[df['DEPARTAMENTO_DESCRIPCION'].isin(regiones)].copy()
df_filtrada =df_filtrada[df_filtrada['AÑO_DECLARACION']<=2024]
resumen_anual= df_filtrada.groupby(['AÑO_DECLARACION', 'DEPARTAMENTO_DESCRIPCION']).agg({'FOBUSD':'sum','PESO_NETO_KG':'sum'}).reset_index()
resumen_anual['PRECIO_PROM_USD_KG']= resumen_anual['FOBUSD']/resumen_anual['PESO_NETO_KG']

#3 Calcular CAGR y r2
resultados_indicadores = []
for region in regiones:
    data_region =resumen_anual[resumen_anual['DEPARTAMENTO_DESCRIPCION']==region].sort_values('AÑO_DECLARACION')
    if len(data_region)>1: #Porque necesitamos mínimo 2 años para comparar
        # CAGR
        valor_inicial = data_region['FOBUSD'].iloc[0]
        valor_final = data_region['FOBUSD'].iloc[-1]
        n_periodos= len(data_region)-1
        cagr = (valor_final/valor_inicial)**(1/n_periodos)-1
        # R-Cuadrado
        X = data_region['AÑO_DECLARACION'].values.reshape(-1,1)# Pasan de forma horizontal a columna y asi poder trabajar con sklearn
        y = data_region['FOBUSD'].values.reshape(-1,1)
        reg = LinearRegression().fit(X,y)
        r2 = reg.score(X, y)
        
        resultados_indicadores.append({
            'Region': region,
            'CAGR_Valor': cagr,
            'R_Cuadrado': r2,
            'Valor_2019': valor_inicial,
            'Valor_Final': valor_final
        })

df_indicadores = pd.DataFrame(resultados_indicadores)

#4 Guardamos
carpeta_origen = os.path.dirname(path_archivo)
nombre_salida = "Objetivo_1_Resultados.xlsx"
ruta_salida_final = os.path.join(carpeta_origen,nombre_salida)

# ExcelWriter es para guardar dos hojas en el mismo libro
try:
    with pd.ExcelWriter(ruta_salida_final) as nombrehoja:
        resumen_anual.to_excel(nombrehoja,sheet_name='Evolucion_Anual',index=False)
        df_indicadores.to_excel(nombrehoja,sheet_name='Indicadores_CAGR_R2',index=False)

    print("-"*50)
    print("¡PROCESO COMPLETADO!")
    print(f"Se ha creado el archivo:{nombre_salida}")
    print(f"Ubicación:{ruta_salida_final}")
    print("-"*50)

    print("\n RESUMEN GENERADO-->")
    print(resumen_anual)
    print("\n INDICADORES-->")
    print(df_indicadores)

except Exception as e:
    print(f"Error al guardar Excel: {e}")
    print("Asegurarse que el archivo 'Objetivo_1_Resultados.xlsx' no esté abierto.")