import pandas as pd
import os
import sys


ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
link_excel_datos = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-AdexDatatrade","Resultados_Consolidados","DB_Final_Objetivo2_BalassayPriceGap.xlsx")
# 1 DIRECCIONES
# dirección EXACTA del excel 
##link_excel_datos = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-AdexDatatrade\Resultados_Consolidados\DB_Final_Objetivo2_BalassayPriceGap.xlsx"

carpeta_destino = os.path.dirname(link_excel_datos)
archivo_newexcel = os.path.join(carpeta_destino, "Resultados_Finales_Tesis_Objetivo2.xlsx")

print(" INICIANDO CÁLCULO DE COMPETITIVIDAD (BALASSA & PRECIOS)...")
print(f" Leyendo datos de: {link_excel_datos}")

try:
    # CARGA DATOS
    if not os.path.exists(link_excel_datos):
        print(f"ERROR: No encuentro el archivo en la ruta especificada.")
        print("Verifica que la ruta 'link_excel_datos' sea correcta.")
        sys.exit()

    df = pd.read_excel(link_excel_datos)
    print("Archivo leído correctamente.")
    
    # Convertir a numéro y rellenar nulos
    cols_numericas =[ c for c in df.columns if c != 'Año']
    for col in cols_numericas:
        df[col]=pd.to_numeric(df[col], errors='coerce').fillna(0)
# 2- CÁLCULO DE INDICADORES
    resultados = df.copy()    
    # A- PRECIOS UNITARIOS USD/KG
    # Precio = FOB/Peso
    resultados['Precio_Lambayeque' ]= resultados_lamba =resultados.apply(lambda row: row['Frijol_FOB_Lambayeque']/row['Frijol_Kg_Lambayeque'] if row[ 'Frijol_Kg_Lambayeque']>0 else 0 , axis=1)
    resultados['Precio_Piura'] = resultados_piura = resultados.apply(lambda row: row['Frijol_FOB_Piura']/row['Frijol_Kg_Piura'] if row['Frijol_Kg_Piura']>0 else 0, axis=1)
    
    # B- BRECHA DE PRECIOS convertidos en porcentaje
    # Fórmula: [(Precio Lamba - Precio Piura)/Precio Piura]*100
    resultados['Brecha_Precios_Lamba_vs_Piura']= resultados.apply(
        lambda row:((row['Precio_Lambayeque']-row['Precio_Piura'])/row['Precio_Piura']) * 100 if row['Precio_Piura'] > 0 else 0, axis=1)

    # C- VENTJA COMPARATIVA REVELADA IVCR
    # Numerador: (Frijol Región/Agro Región)
    part_lamba =resultados['Frijol_FOB_Lambayeque']/resultados['Total_Agro_Lambayeque']
    part_piura =resultados['Frijol_FOB_Piura']/resultados['Total_Agro_Piura']
    
    # Denominador: (Frijol País/Agro País)
    part_nacional =resultados['Total_Frijol_Peru']/resultados['Total_Agro_Peru']
    
    # Evitamos división entre cero en el denominador
    resultados['IVCR_Lambayeque']= part_lamba/part_nacional.replace(0, 1)
    resultados['IVCR_Piura']= part_piura/part_nacional.replace(0, 1)

    resultados['Estatus_Lamba']=resultados['IVCR_Lambayeque'].apply(lambda x: 'Especialista (>1)' if x>1 else 'No Especialista')
    resultados['Estatus_Piura']=resultados['IVCR_Piura'].apply(lambda x: 'Especialista (>1)' if x>1 else 'No Especialista')

# 3. PROMEDIOS -------------------------
    resumen = pd.DataFrame({
        'Indicador': [
            'IVCR Promedio (Competitividad)', 
            'Precio Promedio (USD/Kg)', 
            'Brecha de Precios Promedio (%)'
        ],
        'Lambayeque': [
            resultados['IVCR_Lambayeque'].mean(),
            resultados['Precio_Lambayeque'].mean(),
            resultados['Brecha_Precios_Lamba_vs_Piura'].mean()
        ],
        'Piura': [
            resultados['IVCR_Piura'].mean(),
            resultados['Precio_Piura'].mean(),
            0
        ]
    })
# 4 EXPORTAR A EXCEL ------------------
    try:
        import xlsxwriter
        sistema = 'xlsxwriter'
    except ImportError:
        sistema = 'openpyxl'
        print("Nota: Se usará 'openpyxl'.")

    with pd.ExcelWriter(archivo_newexcel, engine=sistema) as nombre_hoja:
        
        # Hoja 1: Indicadores Anuales
        cols_finales = [
            'Año', 
            'Precio_Lambayeque', 'Precio_Piura', 'Brecha_Precios_Lamba_vs_Piura',
            'IVCR_Lambayeque', 'IVCR_Piura', 
            'Estatus_Lamba', 'Estatus_Piura'
        ]
        resultados[cols_finales].to_excel(nombre_hoja, sheet_name='Indicadores_Anuales', index=False)
        
        # Hoja 2: Resumen
        resumen.to_excel(nombre_hoja, sheet_name='Resumen_Competitividad', index=False)
        
        # Hoja 3: Data Original
        df.to_excel(nombre_hoja, sheet_name='Data_Maestra', index=False)

        # solo si funciona xlsxwriter
        if sistema == 'xlsxwriter':
            excel_archivo = nombre_hoja.book
            ws = nombre_hoja.sheets[ 'Indicadores_Anuales' ]
            formato_dinero=excel_archivo.add_format({'num_format': '$0.00'})
            formato_num=excel_archivo.add_format({'num_format': '0.00'})
            
            ws.set_column('B:C', 15, formato_dinero)
            ws.set_column('D:F', 15, formato_num)

    print("-"*60)
    print(f" ANÁLISIS COMPLETADO!!!")
    print(f"Archivo generado en: {archivo_newexcel}")

except Exception as e:
    print(f"\n OCURRIÓ UN ERROR: {e}")