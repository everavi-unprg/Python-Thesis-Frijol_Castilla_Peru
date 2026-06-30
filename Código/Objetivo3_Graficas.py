import pandas as pd
import matplotlib.pyplot as plt
import os


ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
link_excel = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Frijol Castilla 2012-2024.xlsx")
graf_carpeta = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Graficos Generados")

# 1 Links iniciales del excel donde se saca la informaicón y de la carpeta donde se guardarán las gráficas
##link_excel = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-Azatrade\Resultados_Consolidados\Frijol Castilla 2012-2024.xlsx"
##graf_carpeta = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-Azatrade\Resultados_Consolidados\Graficos Generados"

if not os.path.exists(graf_carpeta):
    os.makedirs(graf_carpeta)

# 2- Filtros para las gráficas que se hará más adelante
df = pd.read_excel(link_excel)
df = df[df['AÑO_DECLARACION'].isin(range(2012, 2025))]
df = df[df['DEPARTAMENTO_DESCRIPCION'].isin(['LAMBAYEQUE', 'PIURA'])]

export_empresa =df.groupby(['AÑO_DECLARACION', 'DEPARTAMENTO_DESCRIPCION','RAZON_SOCIAL'])['FOBUSD'].sum().reset_index()
anualxregion_total= export_empresa.groupby(['AÑO_DECLARACION','DEPARTAMENTO_DESCRIPCION'])['FOBUSD'].transform('sum')
export_empresa['Market_Share'] = export_empresa['FOBUSD']/anualxregion_total

indicators = []
top4_empresas_data=[]
for año in range(2012, 2025):
    for dept in ['LAMBAYEQUE', 'PIURA']:
        subset = export_empresa[(export_empresa['AÑO_DECLARACION']==año)&(export_empresa['DEPARTAMENTO_DESCRIPCION'] == dept)]
        subset = subset.sort_values('Market_Share', ascending=False)
        ihh = ((subset['Market_Share']*100)**2).sum()
        top4_df= subset.head(4) # Para las 4 empresas de mayor participación
        cr4=subset['Market_Share'].head(4).sum()*100
        indicators.append({'Año':año,'Región':dept,'IHH':ihh,'CR4':cr4})

        nombres_con_porcentaje=[]
        for puesto, row in enumerate(top4_df.itertuples(),1):
            nombre= str(row.RAZON_SOCIAL).strip()
            participacion_individual= row.Market_Share*100

            top4_empresas_data.append({
                'Año': año,
                'Region': dept,
                'Puesto': puesto,
                'Razón Social': nombre,
                'Participación Individual (%)': round(participacion_individual, 2),
                'Cr4 Región (%)': round(cr4,2), 
            })

df_ind = pd.DataFrame(indicators)
df_top4_export = pd.DataFrame(top4_empresas_data)

# Coeficiente de Variación
export_anuales=df.groupby(['AÑO_DECLARACION', 'DEPARTAMENTO_DESCRIPCION'])['FOBUSD'].sum().reset_index()
cv_data=[]
cv_sensibilidad_data=[]
for dept in ['LAMBAYEQUE', 'PIURA']:
    data = export_anuales[export_anuales['DEPARTAMENTO_DESCRIPCION']==dept]['FOBUSD']
    cv = (data.std()/data.mean())*100
    cv_data.append({'Región':dept,'CV':cv})

    data_sens=export_anuales[(export_anuales['DEPARTAMENTO_DESCRIPCION']==dept) & (export_anuales['AÑO_DECLARACION']>=2013)]['FOBUSD']
    cv_sens= (data_sens.std()/data_sens.mean())*100

    cv_sensibilidad_data.append({
        'Región': dept,
        'CV Oficial (2012-2024) %': round(cv, 2),
        'CV Ajustado (2013-2024) %': round(cv_sens, 2)
    })

df_cv = pd.DataFrame(cv_data)
df_cv_sensibilidad= pd.DataFrame(cv_sensibilidad_data)

# 3- Para el cómo se verán las gráficas ordenado y normal como para un estilo APA formal nomás
plt.rcParams['font.family']='serif'
plt.rcParams['font.serif']=['Times New Roman']
colors={'LAMBAYEQUE':'#1f77b4','PIURA':'#ff7f0e'}

def estilo_APA(ax, ylabel):
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=0) 
    ax.tick_params(axis='both', labelsize=10)
    ax.set_axisbelow(True)

# Gráfica 1_IHH según Merger Guidelines del 2023 ojo ya no se pone como de 3500 a más es concentrado, basta con 1801 a más para ser concentrado el mercado
fig1, ax1 = plt.subplots(figsize=(6.4, 4.5))
plt.subplots_adjust(left=0.12, right=0.95, bottom=0.15, top=0.9)

max_ihh = df_ind['IHH'].max()
ylim_top = max_ihh*1.2
if ylim_top<3500: ylim_top=3500 

# Ahora según la MG 2023 es antes de 1000 y después de 1800 muy concentrado
ax1.axhspan(0, 1000, color='#e5f5e0', alpha=0.4, zorder=0)
ax1.axhspan(1000,1800, color='#fff7bc', alpha=0.4, zorder=0)
ax1.axhspan(1800,ylim_top + 1000, color='#fee0d2', alpha=0.4, zorder=0)

props = dict(facecolor='white', alpha=0.6, edgecolor='none', pad=2)

# Etiqueta cuando no Concentrado
ax1.text(2015,350,'No Concentrado (<1000)',fontsize=10,color='green',style='italic',ha='center',bbox=props)
# Cuando mercado es moderado entre 1000 a 1800
ax1.text(2015, 1450, 'Moderado (1000-1800)', fontsize=10, color='#b38f00', style='italic', ha='center',bbox=props)
# Cuando sí hay alta Concentración
ax1.text(2019, 2800,'Alta Concentración (>1800)', fontsize=10, color='#b30000', style='italic', ha='center', bbox=props)

df_neworden_ihh = df_ind.pivot(index='Año', columns='Región', values='IHH')
años_index = df_neworden_ihh.index

ax1.plot(años_index, df_neworden_ihh['LAMBAYEQUE'], marker='o', label='Lambayeque', color=colors['LAMBAYEQUE'], linewidth=2, zorder=3)
ax1.plot(años_index, df_neworden_ihh['PIURA'], marker='o', label='Piura', color=colors['PIURA'], linewidth=2, zorder=3)

# Para que no se contrapongan las etiquetas
for año in años_index:
    val_lam = df_neworden_ihh.loc[año, 'LAMBAYEQUE']
    val_piu = df_neworden_ihh.loc[año, 'PIURA']
    diferencia = val_piu - val_lam
    
    if abs(diferencia) < 600:
        if val_piu >= val_lam:
            coordenada_piura = 15; coordenada_lambay = -20
        else:
            coordenada_piura = -20; coordenada_lambay = 15
    else:
        coordenada_lambay = -15; coordenada_piura = 10

    ax1.annotate(f"{val_lam:.0f}", (año, val_lam), textcoords="offset points", xytext=(0, coordenada_lambay), 
                 ha='center',fontsize=9, color=colors['LAMBAYEQUE'], fontweight='bold', zorder=4,
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.1))

    ax1.annotate(f"{val_piu:.0f}", (año, val_piu), textcoords="offset points", xytext=(0, coordenada_piura), 
                 ha='center', fontsize=9, color=colors['PIURA'], fontweight='bold', zorder=4,
                 bbox=dict(facecolor='white',alpha=0.7, edgecolor='none', pad=0.1))

estilo_APA(ax1, 'Índice IHH (0 - 10,000)')
ax1.set_ylim(0, ylim_top)
ax1.legend(frameon=False,loc='upper right')
fig1.savefig(os.path.join(graf_carpeta, "Objetivo3_IHH_Final_Norma2023.png"),dpi=300)
plt.close(fig1)

# GRÁFICA 2 CR4 priincipales empresas
fig2, ax2 = plt.subplots(figsize=(6.4, 4.5))
plt.subplots_adjust(left=0.12, right=0.95, bottom=0.15, top=0.9)
df_orden_cr4 = df_ind.pivot(index='Año', columns='Región', values='CR4')

ax2.plot(años_index, df_orden_cr4['LAMBAYEQUE'], marker='s', label='Lambayeque', color=colors['LAMBAYEQUE'], linewidth=2, zorder=3)
ax2.plot(años_index, df_orden_cr4['PIURA'], marker='s', label='Piura', color=colors['PIURA'], linewidth=2, zorder=3)

for año in años_index:
    val_lam =df_orden_cr4.loc[año,'LAMBAYEQUE']
    val_piu =df_orden_cr4.loc[año,'PIURA']
    diferencia = val_piu-val_lam
    
    if abs(diferencia)<8:
        if val_piu>=val_lam:
            coordenada_piura=18;coordenada_lambay=-22
        else:
            coordenada_piura=-22;coordenada_lambay=18
    else:
        coordenada_lambay=-15;coordenada_piura=10

    ax2.annotate(f"{val_lam:.1f}%", (año, val_lam), textcoords="offset points", xytext=(0, coordenada_lambay), 
                 ha='center', fontsize=9, color=colors['LAMBAYEQUE'], fontweight='bold', zorder=4,
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.2))
    ax2.annotate(f"{val_piu:.1f}%", (año, val_piu), textcoords="offset points", xytext=(0, coordenada_piura), 
                 ha='center', fontsize=9, color=colors['PIURA'], fontweight='bold', zorder=4,
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.2))

estilo_APA(ax2,'Participación de Mercado (%)')
ax2.set_ylim(30,119) 
ax2.legend(frameon=False,loc='lower right')
fig2.savefig(os.path.join(graf_carpeta,"Objetivo3_CR4_Final.png"), dpi=300)
plt.close(fig2)

# GRÁFICA 3 -> Coeficiente de variacón igual revisar el word
fig3, ax3 = plt.subplots(figsize=(6.4, 4.5))
plt.subplots_adjust(left=0.12,right=0.95, bottom=0.15, top=0.9)
regiones = df_cv['Región']; cvs=df_cv['CV']
bar_colors = [colors[r] for r in regiones]
bars = ax3.bar(regiones.str.title(), cvs, color=bar_colors, width=0.6, zorder=3)

for bar in bars:
    altura = bar.get_height()
    ax3.annotate(f'{altura:.1f}%', xy=(bar.get_x()+bar.get_width()/2,altura),
                 xytext=(0,3), textcoords="offset points", ha='center',va='bottom', fontsize=11, fontweight='bold', zorder=4)

estilo_APA(ax3, 'Coeficiente de Variación (%)')
ax3.set_ylim(0,max(cvs)*1.2)
fig3.savefig(os.path.join(graf_carpeta, "Objetivo3_CV_Final.png"),dpi=300)
plt.close(fig3)

print(" GRÁFICOS LISTOSS!!!")

ruta_tabla_top4= os.path.join(ubicacion_codigo,'..',"Data","Exportaciones por año-Azatrade","Resultados_Consolidados","Tabla_Top4_Empresas.xlsx")
ruta_tabla_top4= os.path.normpath(ruta_tabla_top4)

ruta_tabla_cv= os.path.join(ubicacion_codigo,'..',"Data","Exportaciones por año-Azatrade", "Resultados_Consolidados","Tabla_CV_Sensibilidad.xlsx")
ruta_tabla_cv= os.path.normpath(ruta_tabla_cv)

try:
    df_top4_export.to_excel(ruta_tabla_top4, index=False)
    print(f"Tabla de empresas exportada exitosamente en : {{ruta_tabla_top4}}")

    df_cv_sensibilidad.to_excel(ruta_tabla_cv, index=False)
    print("Tabla de sensibilidad SV exportada exitosamente en : {ruta_tabla_cv}")


except Exception as e:
    print(f"Error al guardar la tabla de empresas: {e}")