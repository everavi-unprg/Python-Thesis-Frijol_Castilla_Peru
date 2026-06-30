import pandas as pd
import matplotlib.pyplot as plt
import os


ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Frijol Castilla 2012-2024.xlsx")
output_folder = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Graficos Generados")

##input_path = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-Azatrade\Resultados_Consolidados\Frijol Castilla 2012-2024.xlsx"
##output_folder = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-Azatrade\Resultados_Consolidados\Graficos Generados"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

df = pd.read_excel(input_path)
df = df[df['AÑO_DECLARACION'].isin(range(2012, 2025))]
df_lam = df[df['DEPARTAMENTO_DESCRIPCION'] == 'LAMBAYEQUE'].copy()

if 'MES_NUMERACION' in df_lam.columns:
    df_lam['Mes']=df_lam['MES_NUMERACION']
else:
    df_lam['Mes']=pd.to_datetime(df_lam['FECHA_EMBARQUE']).dt.month

col_peso = 'PESO_NETO_KG'

est_mensuales = df_lam.groupby('Mes').agg(
    Total_FOB=('FOBUSD', 'sum'),
    Total_Peso=(col_peso, 'sum')
).reset_index()
est_mensuales['Precio_Promedio']=est_mensuales['Total_FOB']/est_mensuales['Total_Peso']

cuota_mensual = df_lam.groupby(['AÑO_DECLARACION', 'Mes'])[col_peso].sum().reset_index()
cuota_anual = cuota_mensual.groupby('AÑO_DECLARACION')[col_peso].transform('sum')
cuota_mensual['Pct'] =(cuota_mensual[col_peso]/cuota_anual) * 100
cuota_promedio = cuota_mensual.groupby('Mes')['Pct'].mean().reset_index()

data_maestra=pd.merge(cuota_promedio, est_mensuales[['Mes','Precio_Promedio']],on='Mes')
data_maestra['Mes_Nombre']=data_maestra['Mes'].map({
    1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 
    7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'})

tabla1 = data_maestra.copy()

def logica_tabla1(row):
    m = row['Mes']
    if m == 4: rent = "Muy Alta (Max Precio)";est="Venta Premium"
    elif m in [2,3]: rent = "Alta"; est = "Oportunidad"
    elif m in [11, 12]: rent = "Media (Volumen)"; est = "Campaña Masiva"
    elif m == 1: rent = "Media"; est = "Liquidación"
    elif m in [5,6,7,8]: rent = "Baja"; est = "Transición"
    else: rent = "Media"; est = "Pre-Campaña"
    return pd.Series([est, rent])

tabla1[['Estrategia', 'Rentabilidad']] = tabla1.apply(logica_tabla1, axis=1)

tabla1_final = tabla1[['Mes_Nombre', 'Pct', 'Precio_Promedio', 'Estrategia', 'Rentabilidad']].copy()
tabla1_final['Pct'] = tabla1_final['Pct'].apply(lambda x: f"{x:.1f}%")
tabla1_final['Precio_Promedio'] = tabla1_final['Precio_Promedio'].apply(lambda x: f"$ {x:.2f}")
tabla1_final.columns = ['Mes', 'Oferta (Volumen)', 'Precio Promedio', 'Estrategia Recomendada', 'Nivel Rentabilidad']

path_t1 = os.path.join(output_folder, "Objetivo4_Tabla1_Mensual.xlsx")
tabla1_final.to_excel(path_t1, index=False)


def calcular_ventana(meses_lista, nombre_ventana, estrategia_txt, accion_txt, rent_txt):
    subset = data_maestra[data_maestra['Mes'].isin(meses_lista)]
    
    precio_promedio = subset['Precio_Promedio'].mean()
    precio_minimo = subset['Precio_Promedio'].min()
    precio_max = subset['Precio_Promedio'].max()
    cuota_promedio = subset['Pct'].mean()
    
    nombres = [subset[subset['Mes']==m]['Mes_Nombre'].values[0] for m in meses_lista]
    if len(nombres) > 2:
        rango_meses = f"{nombres[0]} - {nombres[-1]}"
    else:
        rango_meses = ", ".join(nombres)
        
    comportamiento = f"Oferta: ~{cuota_promedio:.1f}% mensual. Precios: ${precio_minimo:.2f} - ${precio_max:.2f}."
    
    return {
        "Ventana Comercial": nombre_ventana,
        "Mes": rango_meses,
        "Comportamiento del Mercado": comportamiento,
        "Estrategia Comercial": estrategia_txt,
        "Acción Operativa": accion_txt,
        "Rentabilidad": rent_txt
    }

filas_tabla2 = []

filas_tabla2.append(calcular_ventana(
    [2, 3, 4], "I. Oportunidad (Premium)", 
    "Arbitraje Temporal: Venta a nichos.", 
    "Liberar stocks. Negociar Spot.", "Muy Alta"
))

filas_tabla2.append(calcular_ventana(
    [5, 6, 7, 8], "II. Transición", 
    "Mantenimiento: Contratos fijos.", 
    "Planificar siembras. Relaciones.", "Media - Baja"
))

filas_tabla2.append(calcular_ventana(
    [9, 10], "III. Pre-Campaña", 
    "Preventa: Cierre contratos futuros.", 
    "Acopio temprano. Fletes.", "Media"
))

filas_tabla2.append(calcular_ventana(
    [11, 12, 1], "IV. Campaña Masiva", 
    "Rotación Rápida: Venta volumen.", 
    "Logística intensiva.", "Media (x Volumen)"
))

tabla2_final = pd.DataFrame(filas_tabla2)

path_t2 = os.path.join(output_folder, "Objetivo4_Tabla2_Estrategica.xlsx")
tabla2_final.to_excel(path_t2, index=False)

def guardar_imagen_tabla(df, titulo, filename):
    fig, ax = plt.subplots(figsize=(12, len(df)*0.8 + 2))
    ax.axis('off')
    tabla = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='left', loc='center')
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1, 2)
    
    for (i, j), cell in tabla.get_celld().items():
        if i == 0:
            cell.set_text_props(weight='bold', color='white', family='Times New Roman')
            cell.set_facecolor('#40466e')
        else:
            cell.set_text_props(family='Times New Roman')
            
    plt.title(titulo, fontname='Times New Roman', fontsize=14, pad=10)
    plt.savefig(os.path.join(output_folder, filename), dpi=300, bbox_inches='tight')
    plt.close()

guardar_imagen_tabla(tabla1_final, "Objetivo4_Tabla 1: Calendario Mensual Detallado", "Objetivo4_Tabla1_Visual.png")
guardar_imagen_tabla(tabla2_final, "Objetivo4_Tabla 2: Calendario Estratégico Agrupado", "Objetivo4_Tabla2_Visual.png")

print(f"¡Listo! Archivos generados en: {output_folder}")
print("1. Tabla1_Mensual.xlsx y Tabla1_Visual.png (Original)")
print("2. Tabla2_Estrategica.xlsx y Tabla2_Visual.png (Mejorada)")