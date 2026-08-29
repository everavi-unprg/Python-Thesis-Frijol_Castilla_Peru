import pandas as pd
import os


ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
link_orig = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-AdexDatatrade","Resultados_Consolidados")
# 1 LINK DE UBICACIONES
#donde están los excels "Unidos" que se crearon antes
##link_orig = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-AdexDatatrade\Resultados_Consolidados"
# Aplicamos diccionario mejor
archivos_input = {
    "Total_Agro_Lambayeque"  :"Unido_Lambayeque_Agro_2012-2024.xlsx",
    "Total_Agro_Piura" :"Unido_Piura_Agro_2012-2024.xlsx",
    "Total_Agro_Peru" :"Unido_Peru_Agro_2012-2024.xlsx",
    "Total_Frijol_Peru" :"Unido_Peru_Frijol_2012-2024.xlsx" }

print("Iniciando segunda parte -> MACRO DATA...")
print("-"*60)
# Creamos un DataFrame con los años para el orden 
df_bloque_b =pd.DataFrame({'Año': range( 2012 , 2025 )})
try:
    for nombre_columna , archivo in archivos_input.items():
        ruta_archivo = os.path.join(link_orig, archivo)
        if os.path.exists(ruta_archivo) :
            print(f"Leyendo:{archivo} ...")
            df_primero = pd.read_excel(ruta_archivo)
            # para que los datos sean sí o sí numeros enteros de año
            df_primero['Año'] = df_primero['Año'].astype(int)
            # solo año y valor FOB
            if 'Valor_FOB' in df_primero.columns:
                df_primero = df_primero[['Año', 'Valor_FOB']]
                #para saber de dónde vino
                df_primero= df_primero.rename(columns={'Valor_FOB': nombre_columna})
                # Unimos al DataFrame base usando el Año
                df_bloque_b = pd.merge( df_bloque_b, df_primero, on='Año', how='left')
            else:
                print( f"La columna del Valor_FOB no existe en {archivo}")
        else:
            print(f"NO SE ENCONTRÓ ARCHIVO: {archivo}")

# 2. GUARDANOS RESULTADO ---------
    link_final = os.path.join(link_orig , "Bloque_B_Macro_Data.xlsx")
    # Formatear números grandes para que no salgan en notación científica al guardar (opcional, pero útil)
    #Pandas guarda en Excel como números puros, así que Excel se encarga del formato visual
    df_bloque_b.to_excel(link_final, index=False)
    
    print("-" *60)
    print(f"LISTO!! Bloque B creado en:\n{link_final}")
    print("\nEl archivo contiene las columnas:")
    print(list(df_bloque_b.columns))

except Exception as e:
    print(f"ERROR!!! : {e}")