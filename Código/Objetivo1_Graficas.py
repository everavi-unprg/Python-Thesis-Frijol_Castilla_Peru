import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import matplotlib.ticker as ticker

# 1. 
ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
link_casa = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados")
excel_datos = os.path.join(link_casa, "Objetivo_1_Resultados.xlsx")
nueva_carpeta_graf = os.path.join(link_casa, "Graficos Generados")
print("Obteniendo datos ...")


if not os.path.exists(nueva_carpeta_graf): #acá se crea la carpeta
    os.makedirs(nueva_carpeta_graf)

if os.path.exists(excel_datos): #para cargar los datos
    df_graf =pd.read_excel(excel_datos,sheet_name='Evolucion_Anual')
    df_indicadores = pd.read_excel(excel_datos,sheet_name='Indicadores_CAGR_R2')
    print("Datos cargados correctamente.")
else:
    print(f"ERROR: No se encontró {excel_datos}. Ejecuta primero el Código de Cálculos.")
    exit()
# PARA tener formato APA 7ma edición
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 9 
colores = {'LAMBAYEQUE': '#1f77b4', 'PIURA': '#d62728'}

#2. FUNCIONES ------------------------------------------

def agregar_etiquetas(ax, tipo='dinero'):
    for line in ax.lines:
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        for x, y in zip(x_data, y_data):
            if pd.isna(y): continue
            
            if tipo == 'dinero': # Como está en millones la info se quiere convertir a  3.5M
                label = f'{y/1000000:.1f}M'
            elif tipo == 'precio': # Para quedar en formato tipo 1.35
                label = f'{y:.2f}'
            
            ax.text(x, y, label, color='black', fontsize=7, ha='center', va='bottom', fontweight='bold')

def configurar_eje_x_rotado(ax, df):
    ax.set_xticks(df['AÑO_DECLARACION'].unique())
    plt.xticks(rotation=45)

# 3. Gráficos estadósticos de valor y volumen Precio Promedio

# 1. VALOR FOB -----------

nombre_1 = "Objetivo1_1_Valor_FOB.png"
print(f"Creando : {nombre_1}...")

plt.figure(figsize=(6.4, 4.5))
ax1 = sns.lineplot(data=df_graf, x='AÑO_DECLARACION',y='FOBUSD', hue='DEPARTAMENTO_DESCRIPCION',palette=colores, marker='o', linewidth=2)
#plt.title('Dinámica del Valior Exportado FOB (2012-2024)',fontsize=11, fontweight='bold')
plt.ylabel('Valor FOB (USD)')
plt.xlabel('')
plt.legend(title='',loc='upper right', fontsize=8, frameon=True)
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x,pos: '{:,.0f}M'.format(x/1000000)))
configurar_eje_x_rotado(ax1,df_graf)
agregar_etiquetas(ax1,  tipo='dinero')

plt.tight_layout()
plt.savefig(os.path.join(nueva_carpeta_graf, nombre_1),dpi=300)
plt.close()

# 2 VOLUMEN -----------------

nombre_2 = "Objetivo1_2_Volumen_Kg.png"
print(f"Creando: {nombre_2}...")

plt.figure(figsize=(6.4, 4.5))
ax2 = sns.barplot(data=df_graf,x='AÑO_DECLARACION',y='PESO_NETO_KG', hue='DEPARTAMENTO_DESCRIPCION',palette=colores, alpha=0.9)
#plt.title('Dinámica del Volumen Exportado(Peso Neto)',fontsize=11, fontweight='bold')
plt.ylabel('Volumen (Kg)')
plt.xlabel('')
plt.legend(title='', loc='upper right', fontsize=8)
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}M'.format(x/1000000)))
plt.xticks(rotation=45)

# Etiquetas de barras
for container in ax2.containers:
    labels = [f'{v/1000000:.1f}M' if v > 1000000 else f'{v/1000:.0f}k' for v in container.datavalues]
    ax2.bar_label(container, labels=labels, fontsize=6, padding=2, rotation=90)

plt.tight_layout()
plt.savefig(os.path.join(nueva_carpeta_graf, nombre_2), dpi=300)
plt.close()

# 3. Para el PRECIO FOB ---------
nombre_3 = "Objetivo1_3_Precio_Promedio.png"
print(f"Creando: {nombre_3}...")

plt.figure(figsize=(6.4, 4.5))
ax3 = sns.lineplot(data=df_graf, x='AÑO_DECLARACION', y='PRECIO_PROM_USD_KG', hue='DEPARTAMENTO_DESCRIPCION', 
             palette=colores, marker='s', linewidth=2, linestyle='--')
#plt.title('Precio Promedio Implícito (FOB/KG)', fontsize=11, fontweight='bold')
plt.ylabel('Precio (USD / Kg)')
plt.xlabel('')
plt.legend(title='', loc='best', fontsize=8)
configurar_eje_x_rotado(ax3, df_graf)
agregar_etiquetas(ax3, tipo='precio')

plt.tight_layout()
plt.savefig(os.path.join(nueva_carpeta_graf, nombre_3), dpi=300)
plt.close()


# 4. GRÁFICOS 2 Regresiones CAGR

# --- 4. REGRESIÓN LINEAL ---
nombre_4 = "Objetivo1_4_Tendencia_Regresion.png"
print(f"Creando: {nombre_4}...")

g = sns.lmplot(
    data=df_graf, x='AÑO_DECLARACION', y='FOBUSD', hue='DEPARTAMENTO_DESCRIPCION',
    palette=colores, height=4.5, aspect=1.42, 
    legend=False, ci=None,
    scatter_kws={'s': 50, 'alpha':0.6}, line_kws={'linewidth': 2})
#plt.title('Tendencia Lineal de Exportaciones (Regresión)', fontsize=11, fontweight='bold')
plt.ylabel('Valor FOB (USD)')
plt.xlabel('')
plt.legend(title='', loc='upper right',fontsize=8)
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}M'.format(x/1000000)))
plt.gca().set_xticks(df_graf['AÑO_DECLARACION'].unique())
plt.xticks(rotation=45)

plt.savefig(os.path.join(nueva_carpeta_graf, nombre_4), dpi=300, bbox_inches='tight')
plt.close()

# 5. CAGR CORREGIDO 2026
nombre_5 = "Objetivo1_5_Crecimiento_CAGR.png"
print(f"Generando: {nombre_5}...")

plt.figure(figsize=(6.4, 4.5))
ax_cagr = sns.barplot(data=df_indicadores, x='Region', y='CAGR_Valor', hue='Region', palette=colores, legend=False)

#plt.title('Comparativo de Velocidad de Crecimiento (CAGR)', fontsize=11, fontweight='bold')
plt.ylabel('Tasa de Crecimiento Anual')
plt.xlabel('')
plt.axhline(0, color= 'black', linewidth=0.8)
ax_cagr.yaxis.set_major_formatter(ticker.PercentFormatter(1.0))

for container in ax_cagr.containers:
    labels=[f'{v*100:.2f}%' for v in container.datavalues]
    ax_cagr.bar_label(container, labels =labels, padding=3, fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join( nueva_carpeta_graf, nombre_5), dpi=300)
plt.close()

# 6. R2 Nuevo 
nombre_6 = "Objetivo1_6_Estabilidad_R2.png"
print(f"Generando: {nombre_6 }...")

plt.figure(figsize=(6.4, 4.5))
ax_r2 = sns.barplot(data=df_indicadores, x='Region', y='R_Cuadrado', hue='Region', palette=colores, legend=False)

#plt.title('Comparativo de Estabilidad de Tendencia (R²)', fontsize=11, fontweight='bold')
plt.ylabel('Coeficiente R²')
plt.xlabel('')
plt.ylim(0, 1.1)

for container in ax_r2.containers:
    ax_r2.bar_label(container, fmt='%.4f', padding=3, fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join( nueva_carpeta_graf, nombre_6), dpi=300)
plt.close()

print("-"*50)
print("FINALIZADO!")
print(f"Se han generado los 6 gráficos ordenados en:\n{nueva_carpeta_graf }")
print("-"*50)