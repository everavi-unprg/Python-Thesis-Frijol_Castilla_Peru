import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Frijol Castilla 2012-2024.xlsx")
output_folder = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Graficos Generados")

#input_path = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-Azatrade\Resultados_Consolidados\Frijol Castilla 2012-2024.xlsx"
#output_folder = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-Azatrade\Resultados_Consolidados\Graficos Generados"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)



df = pd.read_excel(input_path)
df = df[df['AÑO_DECLARACION'].isin(range(2012, 2025))]


df_regional = df[df['DEPARTAMENTO_DESCRIPCION'].isin(['LAMBAYEQUE', 'PIURA'])].copy()

col_peso = 'PESO_NETO_KG'

if 'MES_NUMERACION' in df.columns:
    df['Mes'] = df['MES_NUMERACION']
    df_regional['Mes'] = df_regional['MES_NUMERACION']
else:
    df['Mes'] = pd.to_datetime(df['FECHA_EMBARQUE']).dt.month
    df_regional['Mes'] = pd.to_datetime(df_regional['FECHA_EMBARQUE']).dt.month


#*******************************************************************
# --- CÁLCULO ESTACIONAL REGIONAL (LAMBAYEQUE Y PIURA) ---
# Suma total histórica por mes y región
vol_total_mes = df_regional.groupby(['DEPARTAMENTO_DESCRIPCION', 'Mes'])[col_peso].sum().reset_index()

# Suma total histórica de toda la región (todos los años)
vol_total_dept = vol_total_mes.groupby('DEPARTAMENTO_DESCRIPCION')[col_peso].transform('sum')

# Razón de promedios (Porcentaje estacional histórico exacto)
vol_total_mes['Share_Pct'] = (vol_total_mes[col_peso] / vol_total_dept) * 100

# Asegurar que existan los 12 meses
idx_meses = pd.MultiIndex.from_product([['LAMBAYEQUE', 'PIURA'], range(1, 13)], names=['DEPARTAMENTO_DESCRIPCION', 'Mes'])
prov_temporada = vol_total_mes.set_index(['DEPARTAMENTO_DESCRIPCION', 'Mes']).reindex(idx_meses, fill_value=0).reset_index()


# --- PRECIOS PROMEDIO REGIONALES ---
precio_mensual = df_regional.groupby(['DEPARTAMENTO_DESCRIPCION', 'Mes'])[['FOBUSD', col_peso]].sum().reset_index()
precio_mensual['Avg_Price'] = precio_mensual['FOBUSD'] / precio_mensual[col_peso]


# --- CÁLCULO ESTACIONAL NACIONAL (VALIDACIÓN) ---
# Suma total histórica nacional por mes
nacional_mes = df.groupby('Mes')[col_peso].sum().reset_index()

# Suma total histórica de todos los meses a nivel nacional
total_nac = nacional_mes[col_peso].sum()

# Razón de promedios nacional
nacional_mes['Share_Pct_Nac'] = (nacional_mes[col_peso] / total_nac) * 100
prov_temporada_nac = nacional_mes.set_index('Mes').reindex(range(1, 13), fill_value=0).reset_index()

# Precios promedio nacionales
agrupo_precio_nacional = df.groupby('Mes')[['FOBUSD', col_peso]].sum().reset_index()
agrupo_precio_nacional['Avg_Price_Nac'] = agrupo_precio_nacional['FOBUSD'] / agrupo_precio_nacional[col_peso]

#*******************************************************************

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
colors = {'LAMBAYEQUE': '#1f77b4', 'PIURA': '#ff7f0e', 'NACIONAL': 'gray'}
nombres_mes = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

def setup_apa(ax, ylabel):
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.tick_params(axis='both', labelsize=10)

def etiquetar_puntos_clasico(ax, df_data, col_valor, sufijo=""):
    reorganizado = df_data.pivot(index='Mes', columns='DEPARTAMENTO_DESCRIPCION', values=col_valor)
    for mes in reorganizado.index:
        val_lam = reorganizado.loc[mes, 'LAMBAYEQUE']
        val_piu = reorganizado.loc[mes, 'PIURA']
        if pd.isna(val_lam): val_lam = 0
        if pd.isna(val_piu): val_piu = 0
        if val_piu >= val_lam:
            off_piu, off_lam = 5, -10
        else:
            off_piu, off_lam = -10, 5
        ax.annotate(f"{val_lam:.{2 if sufijo=='' else 1}f}{sufijo}", (mes, val_lam), 
                    textcoords="offset points", xytext=(0, off_lam), ha='center', fontsize=8, 
                    color=colors['LAMBAYEQUE'], fontweight='bold', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=0.1))
        ax.annotate(f"{val_piu:.{2 if sufijo=='' else 1}f}{sufijo}", (mes, val_piu), 
                    textcoords="offset points", xytext=(0, off_piu), ha='center', fontsize=8, 
                    color=colors['PIURA'], fontweight='bold', bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=0.1))

def etiquetar_precios(ax, x_data, y_data):
    for x, y in zip(x_data, y_data):
        ax.annotate(f"${y:.2f}", (x, y),
                    textcoords="offset points", 
                    xytext=(0, 5),
                    ha='center', 
                    fontsize=8, 
                    color='#d62728', 
                    fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=0.5))

# GRÁFICA 14: OFERTA
fig1, ax1 = plt.subplots(figsize=(6.4, 4.5))
plt.subplots_adjust(left=0.12, right=0.95, bottom=0.15, top=0.9)
for dept in ['LAMBAYEQUE', 'PIURA']:
    data = prov_temporada[prov_temporada['DEPARTAMENTO_DESCRIPCION'] == dept]
    ax1.plot(data['Mes'], data['Share_Pct'], marker='o', label=dept.title(), color=colors[dept], linewidth=2)
etiquetar_puntos_clasico(ax1, prov_temporada, 'Share_Pct', sufijo="%")
setup_apa(ax1, 'Participación en el Volumen Anual (%)')
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(nombres_mes)
ax1.set_xlabel('Mes')
ax1.legend(frameon=False, loc='upper left')
fig1.savefig(os.path.join(output_folder, "Objetivo4_Oferta_Original.svg"), dpi=300)

# GRÁFICA 15: PRECIOS
fig2, ax2 = plt.subplots(figsize=(6.4, 4.5))
plt.subplots_adjust(left=0.12, right=0.95, bottom=0.15, top=0.9)
for dept in ['LAMBAYEQUE', 'PIURA']:
    data = precio_mensual[precio_mensual['DEPARTAMENTO_DESCRIPCION'] == dept]
    ax2.plot(data['Mes'], data['Avg_Price'], marker='s', label=dept.title(), color=colors[dept], linewidth=2)
etiquetar_puntos_clasico(ax2, precio_mensual, 'Avg_Price', sufijo="")
setup_apa(ax2, 'Precio FOB Promedio (USD/Kg)')
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(nombres_mes)
ax2.set_xlabel('Mes')
ax2.legend(frameon=False, loc='upper right', ncol=2)
fig2.savefig(os.path.join(output_folder, "Objetivo4_Precio_Original.svg"), dpi=300)

# GRÁFICA 16: CALENDARIO COMBINADO 
fig3, ax3 = plt.subplots(figsize=(6.4, 4.5))
plt.subplots_adjust(left=0.12, right=0.85, bottom=0.15, top=0.9)

dept = 'LAMBAYEQUE'
data_vol = prov_temporada[prov_temporada['DEPARTAMENTO_DESCRIPCION'] == dept].copy()
data_price = precio_mensual[precio_mensual['DEPARTAMENTO_DESCRIPCION'] == dept].copy()

ax3.set_ylim(0, data_vol['Share_Pct'].max() * 1.35) # Damos más aire arriba
bars = ax3.bar(data_vol['Mes'], data_vol['Share_Pct'], color='#1f77b4', alpha=0.3, label='Oferta Exportable (%)')
# for bar in bars:
#     height = bar.get_height()
#     ax3.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height),
#                  xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, color='#0b4a75', fontweight='bold')

for i, bar in enumerate(bars):
    height = bar.get_height()
    
    # Pasa que en marzo el indicador de precio se sobrepone al porcentaje de volumen, empieza desde el 0=Enero...entonces 2=Marzo
    multiplicador = 0.85 if i == 2 else 1
    
    ax3.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height * multiplicador),
                 xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8, color='#0b4a75', fontweight='bold')

ax3.set_ylabel('Oferta Exportable (% del anual)', fontsize=11, color='#1f77b4')
ax3.tick_params(axis='y', labelcolor='#1f77b4')
ax3.spines['top'].set_visible(False)

# Paraa la línea roja
ax3b = ax3.twinx()
ax3b.set_ylim(data_price['Avg_Price'].min() * 0.95, data_price['Avg_Price'].max() * 1.2)
ax3b.plot(data_price['Mes'], data_price['Avg_Price'], color='#d62728', marker='o', linewidth=2, label='Precio Promedio (USD/Kg)')

etiquetar_precios(ax3b, data_price['Mes'], data_price['Avg_Price'])

ax3b.set_ylabel('Precio FOB (USD/Kg)', fontsize=11, color='#d62728')
ax3b.tick_params(axis='y', labelcolor='#d62728')
ax3b.spines['top'].set_visible(False)
ax3.set_xticks(range(1, 13))
ax3.set_xticklabels(nombres_mes)
ax3.set_xlabel('Mes')
lineas, etiquetas = ax3.get_legend_handles_labels()
lineas2, etiquetas2 = ax3b.get_legend_handles_labels()
ax3b.legend(lineas + lineas2, etiquetas + etiquetas2, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)
fig3.savefig(os.path.join(output_folder, "Objetivo4_Calendario_Original.svg"), dpi=300)

correlacion = data_vol['Share_Pct'].corr(data_price['Avg_Price'])
print(f"ESTO ES SHARE PCT: {data_vol['Share_Pct']}")
print(f"ESTO ES AVG PRICE{data_price['Avg_Price']}")
print(f"El Coeficiente de Correlación (r) para Lambayeque es: {correlacion:.4f}")


# GRÁFICA 17 VALIDACIÓN NACIONAL
fig4, ax4 = plt.subplots(figsize=(6.4, 4.5))
plt.subplots_adjust(left=0.12, right=0.85, bottom=0.15, top=0.9)

ax4.set_ylim(0, prov_temporada_nac['Share_Pct_Nac'].max() * 1.35)
bars_nac = ax4.bar(prov_temporada_nac['Mes'], prov_temporada_nac['Share_Pct_Nac'], color='gray', alpha=0.3, label='Oferta Nacional Total (%)')

for i, bar in enumerate(bars_nac):
    height = bar.get_height()
    
    # Pasa que en marzo el indicador de precio se sobrepone al porcentaje de volumen, empieza desde el 0=Enero...entonces 2=Marzo
    multiplicador = 0.85 if i == 2 else 1
    
    ax4.annotate(f'{height:.1f}%', xy=(bar.get_x() + bar.get_width() / 2, height * multiplicador),
                 xytext=(0, 3), textcoords="offset points", ha='center', fontsize=8, color='black')

ax4.set_ylabel('Oferta Nacional Agregada (%)', fontsize=11, color='gray')
ax4.spines['top'].set_visible(False)
ax4.tick_params(axis='y', labelcolor='gray')

ax4b = ax4.twinx()
ax4b.set_ylim(agrupo_precio_nacional['Avg_Price_Nac'].min()*0.95, agrupo_precio_nacional['Avg_Price_Nac'].max()*1.2)
ax4b.plot(agrupo_precio_nacional['Mes'], agrupo_precio_nacional['Avg_Price_Nac'], color='#d62728', marker='D', linestyle='--', linewidth=2, label='Precio Nacional Promedio')

etiquetar_precios(ax4b, agrupo_precio_nacional['Mes'],agrupo_precio_nacional['Avg_Price_Nac'])

# Resaltar Ventana entre Febrero y Abril
rect = patches.Rectangle((1.5, ax4.get_ylim()[0]), 3,ax4.get_ylim()[1], linewidth=1, edgecolor='none', facecolor='green', alpha=0.1)
ax4.add_patch(rect)
ax4.text(3, ax4.get_ylim()[1]*0.75,'VALIDACIÓN DE\nARBITRAJE SELECTIVO', ha='center', fontsize=8, color='green', fontweight='bold')

ax4b.set_ylabel('Precio Nacional (USD/Kg)',fontsize=11, color='#d62728')
ax4b.spines['top'].set_visible(False)
ax4b.tick_params(axis='y', labelcolor='#d62728')

ax4.set_xticks(range(1, 13))
ax4.set_xticklabels(nombres_mes)
ax4.set_xlabel( 'Mes')

correlacion_nac = prov_temporada_nac['Share_Pct_Nac'].corr(agrupo_precio_nacional['Avg_Price_Nac'])
r2_nac= correlacion_nac**2

print(f"El Coeficiente de Correlación (r) NACIONAL es: {correlacion_nac:.4f}")
print(f"El Coeficiente de Determinación (R2) NACIONAL es: {r2_nac:.4f}")
print(f"ESTO ES SHARE PCT: {prov_temporada_nac['Share_Pct_Nac']}")
print(f"ESTO ES AVG PRICE{agrupo_precio_nacional['Avg_Price_Nac']}")

lineas, etiquetas = ax4.get_legend_handles_labels()
lineas2, etiquetas2 = ax4b.get_legend_handles_labels()
ax4b.legend(lineas + lineas2, etiquetas + etiquetas2, frameon=False, loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2)

fig4.savefig(os.path.join(output_folder, "Objetivo4_Validacion_Nacional.svg"), dpi=300)

print("¡Gráficas generadas!")

# SENSIBILIDAD EXCLUYENDO 2012 PARA LAMBAYEQUE
# Filtramos para quedarnos solo con 2013-2024 y Lambayeque
df_sens = df_regional[(df_regional['AÑO_DECLARACION'] >= 2013) & (df_regional['DEPARTAMENTO_DESCRIPCION'] == 'LAMBAYEQUE')]

# Volumen estacional sin 2012
vol_mes_sens = df_sens.groupby('Mes')[col_peso].sum().reset_index()
total_vol_sens = vol_mes_sens[col_peso].sum()
vol_mes_sens['Share_Pct'] = (vol_mes_sens[col_peso] / total_vol_sens) * 100

# Precio promedio sin 2012
precio_mes_sens = df_sens.groupby('Mes')[['FOBUSD', col_peso]].sum().reset_index()
precio_mes_sens['Avg_Price'] = precio_mes_sens['FOBUSD'] / precio_mes_sens[col_peso]

correlacion_sens = vol_mes_sens['Share_Pct'].corr(precio_mes_sens['Avg_Price'])
r2_sens = correlacion_sens ** 2

print("\n--- ANÁLISIS DE SENSIBILIDAD (2013-2024) ---")
print(f"Correlación (r) Lambayeque sin 2012: {correlacion_sens:.4f}")
print(f"Coeficiente de Determinación (R2) sin 2012: {r2_sens:.4f}")