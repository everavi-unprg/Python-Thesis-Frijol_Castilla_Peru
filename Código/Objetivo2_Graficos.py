import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.ticker as ticker


ubicacion_codigo =os.path.dirname(os.path.abspath(__file__))
link_carpeta = os.path.join(ubicacion_codigo,"..","Data","Exportaciones por año-AdexDatatrade","Resultados_Consolidados")

# 1 Ponemos los links

##ink_carpeta = r"C:\Users\jeffe\OneDrive\Desktop\Frijoles\Frijol Castilla\Data\Exportaciones por año-AdexDatatrade\Resultados_Consolidados"
excel = "Resultados_Finales_Tesis_Objetivo2.xlsx" 

link_archivo = os.path.join(link_carpeta,excel)
carpeta_graficos = os.path.join(link_carpeta,"Gráficos Generados")

if not os.path.exists(carpeta_graficos):
    os.makedirs(carpeta_graficos)

print("Creando gráficos con APA 7...")
try:
    # Mientras carga data
    try:
        df = pd.read_excel(link_archivo, sheet_name='Data_Maestra')
    except:
        df = pd.read_excel(link_archivo)

    # Calculamos indicadores
    df['Precio_Lambayeque'] =df['Frijol_FOB_Lambayeque']/df['Frijol_Kg_Lambayeque']
    df['Precio_Piura'] =df['Frijol_FOB_Piura']/df['Frijol_Kg_Piura']
    df['Gap'] =((df['Precio_Lambayeque']-df['Precio_Piura'])/df['Precio_Piura'])*100
    
    parte_lambayeque = df['Frijol_FOB_Lambayeque']/df['Total_Agro_Lambayeque']
    parte_piura = df['Frijol_FOB_Piura']/df['Total_Agro_Piura']
    parte_Peru = df['Total_Frijol_Peru']/df['Total_Agro_Peru']
    df['IVCR_Lambayeque'] = parte_lambayeque/parte_Peru
    df['IVCR_Piura'] = parte_piura/parte_Peru

# Cuadramos para APA 7ma --------------------------------------

    plt.rcParams['font.family']='serif'
    plt.rcParams['font.serif']=['Times New Roman']
    plt.rcParams['font.size']=12
    plt.rcParams['axes.edgecolor']= 'black'
    plt.rcParams['axes.linewidth']=0.8
    plt.rcParams['axes.spines.top']=False
    plt.rcParams['axes.spines.right']=False

# GRÁFICO 1: IVCR mejores etquetas
    fig, ax = plt.subplots(figsize=( 6.4, 4.5 ))
    ax.grid(axis='y', linestyle='--',alpha=0.4, zorder=0)

   # para las líneas
    sns.lineplot(data=df, x='Año', y='IVCR_Lambayeque', marker='o', markersize=8,linewidth=2, label='LAMBAYEQUE', color='#1f77b4', ax=ax, zorder=3, alpha=0.8)
    sns.lineplot(data=df, x='Año', y='IVCR_Piura', marker='s', markersize=8, linewidth=2,  label='PIURA', color='#ff7f0e', ax=ax, zorder=3, alpha=0.8)
    
    # Para que no se contrapongan los números de etiquetas una sobre otra
    for i, row in df.iterrows():
        valor_lamba = row['IVCR_Lambayeque']
        valor_piura = row['IVCR_Piura']
        diff = valor_lamba-valor_piura
        
        # Esto es por si llegasn ae star a menos de 0.4 de distancia
        if abs(diff) < 0.5:
            # El mayor valor mayor o Lambayeque si son iguales ----> va arriba
            if valor_lamba >= valor_piura:
                offset_lamba = (0, 8)   
                offset_piura = (0, -18) 
            else:
                offset_lamba = (0, -18) # Lamba Abajo
                offset_piura = (0, 8)   # Piura Arriba
        else:
            offset_lamba = (0, 6)
            offset_piura = (0, 6)

        # Para la etiqueta Lambayeque
        ax.annotate(f"{valor_lamba:.2f}", 
                    xy=(row['Año'], valor_lamba),
                    xytext=offset_lamba,
                    textcoords= "offset points",
                    ha='center',va='bottom',
                    fontsize=9,fontweight='bold', color='#1f77b4')
        
        # Etiqueta Piura
        ax.annotate(f"{ valor_piura:.2f}", 
                    xy=(row['Año'], valor_piura),
                    xytext= offset_piura,
                    textcoords="offset points",
                    ha='center' , va='bottom',
                    fontsize=9, fontweight='bold', color='#bf600b')

    # Línea roja del umbral
    ax.axhline(y=1, color='red', linestyle='--', alpha=0.6, linewidth=1.5, zorder=2)
    ax.text(df['Año'].min(), 1.05, 'Umbral Especialización (1.0)', color='red', fontsize=10, fontstyle='italic', alpha=0.8)

    ax.set_ylabel('Índice IVCR (Balassa)', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_xlabel('Año', fontsize=12, fontweight='bold', labelpad=8)
    ax.set_xticks(df['Año'].astype(int))
    ax.tick_params(axis='both', which='major', labelsize=11)

    # Leyenda
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=2, 
              frameon=False, fontsize=11)
    
    plt.subplots_adjust(left=0.12,  
                        right=0.95, 
                        bottom=0.15,
                        top=0.85)  # Margen superior hacer espacio para la leyenda
    #plt.tight_layout()
    plt.savefig(os.path.join(carpeta_graficos, "Objetivo2_IVCR-Balassa.png"), dpi=300)
    plt.close()

    # GRÁFICO 2: PRICE GAP
    fig, ax = plt.subplots(figsize=(6.4, 4.5 ))
    ax.grid(axis='y', linestyle='--' , alpha=0.4, zorder=0)
    
    colores = ['#2ca02c' if x >= 0 else '#d62728' for x in df['Gap']]
    barras = ax.bar(df['Año'], df['Gap'], color=colores, edgecolor='black', 
                    alpha = 0.85, width=0.7, zorder=3)
    ax.axhline(0, color='black', linewidth=1, zorder=4)

    for barra in barras:
        height = barra.get_height()
        xy_pos = (barra.get_x() + barra.get_width() / 2, height*0.965)
        if height >= 0:
            offset = (0, 3) 
        else:
            offset = (0, -14)
            
        ax.annotate( f'{height:.2f}%', xy=xy_pos, xytext=offset,
                     textcoords="offset points", ha='center', va='bottom', 
                     fontsize=9, fontweight='bold', fontfamily='serif')

    ax.set_ylabel('Diferencia Porcentual (%)',fontsize=12,fontweight='bold', labelpad=8)
    ax.set_xlabel('Año', fontsize=12, fontweight='bold',labelpad=8)
    ax.set_xticks(df['Año'].astype(int))
    ax.tick_params(axis='both', which='major', labelsize=11)
    
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='#2ca02c',lw=4, label='Precio Lambayeque > Piura'),
                       Line2D([0], [0], color='#d62728',lw=4,label='Precio Piura >Lambayeque')]
    ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.15), 
              ncol=2, frameon=False, fontsize=11)

    plt.subplots_adjust(left=0.12, right=0.95, bottom=0.15, top=0.85)  
    #plt.tight_layout()
    plt.savefig(os.path.join(carpeta_graficos, "Objetivo2_PriceGAP.png"), dpi=300)
    plt.close()

    print(f" LISTO!! Gráficos en: {carpeta_graficos}")

except Exception as e:
    print(f" ERROR: {e}")