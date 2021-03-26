import matplotlib
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from celluloid import Camera
from matplotlib.lines import Line2D
matplotlib.use("Agg")
plt.rcParams["figure.figsize"] = (16, 12)

carpeta_mes = {'Nov20': 'graficos_2020_11_02_2020_11_23',
               'Dic20': 'graficos_2020_11_02_2020_12_21',
               'Ene21': 'graficos_2020_11_02_2021_01_25',
               'Feb21': 'graficos_2020_11_02_2021_02_22',
               'Mar21': 'graficos_2020_11_02_2021_03_22'
               }

los_colores = {'Nov20': 'purple',
               'Dic20': 'blue',
               'Ene21': 'cyan',
               'Feb21': 'orange',
               'Mar21': 'red'
               }

leyendas = []
for color_mes in los_colores:
    leyendas.append(Line2D([0], [0], color=los_colores[color_mes], label=color_mes))
p25_style = ['--'] * len(leyendas)
p75_style = ['-.'] * len(leyendas)


# devuelve para printear titulo de graficos
def sentido_titulo(x):
    if x[-1].upper() == 'I':
        return f'{x[:-1]} Ida'
    elif x[-1].upper() == 'R':
        return f'{x[:-1]} Ret'
    else:
        return x


nombre_archivo = 'Cotas_resumen.xlsx'
df = {}

for mes in carpeta_mes:
    df[mes] = (pd.read_excel(f'{carpeta_mes[mes]}/{nombre_archivo}',
                             sheet_name=None, index_col=1))

print('Servicios en Nov20', df['Nov20'].keys())
print('Meses: ', df.keys())

servicios = []
for mes in carpeta_mes:
    servicios = servicios + [x for x in df[mes].keys()]

servicios = list(set(servicios))

# elegir un servicio
for ss in servicios:
    print('Dibujando', ss)

    col_perc = 'perc25'
    df25 = pd.DataFrame()

    for mes in carpeta_mes:
        if ss not in df[mes]:
            continue

        if df25.empty:
            df25 = df[mes][ss][[col_perc]].copy()
            df25.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
            continue

        dfx = df[mes][ss][[col_perc]].copy()
        dfx.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
        df25 = df25.merge(dfx, how='outer',
                          left_index=True, right_index=True,
                          suffixes=['', f''])
    if df25.empty:
        print(f"{ss} no tiene datos p25 para ningún mes")
        continue

    col_perc = 'perc75'
    df75 = pd.DataFrame()

    for mes in carpeta_mes:
        if ss not in df[mes]:
            continue

        if df75.empty:
            df75 = df[mes][ss][[col_perc]].copy()
            df75.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
            continue

        dfx = df[mes][ss][[col_perc]].copy()
        dfx.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
        df75 = df75.merge(dfx, how='outer',
                          left_index=True, right_index=True,
                          suffixes=['', f''])

    if df75.empty:
        print(f"{ss} no tiene datos p75 para ningún mes")
        continue

    col_perc = 'cota_debil'
    df_cotadb = pd.DataFrame()
    for mes in carpeta_mes:
        if ss not in df[mes]:
            continue

        if df_cotadb.empty:
            df_cotadb = df[mes][ss][[col_perc]].copy()
            df_cotadb.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
            continue

        dfx = df[mes][ss][[col_perc]].copy()
        dfx.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
        df_cotadb = df_cotadb.merge(dfx, how='outer',
                                    left_index=True, right_index=True,
                                    suffixes=['', f''])

    if df_cotadb.empty:
        print(f"{ss} no tiene datos cota_debil para ningún mes")
        continue

    meses = list(df75.columns)
    shift = len(los_colores) - len(meses)  # por meses faltantes
    fig, ax = plt.subplots()
    camera = Camera(fig)

    for i in range(1, len(meses) + 1):
        df_cotadb[meses[:i]].plot.line(color=los_colores, ax=ax, grid=True)
        df75[meses[:i]].plot.line(color=los_colores, ax=ax, alpha=0.7, style=p75_style[:i])
        df25[meses[:i]].plot.line(color=los_colores, ax=ax, alpha=0.5, style=p25_style[:i])
        plt.tick_params(axis='both', which='major', labelsize=16)
        plt.legend(handles=leyendas[shift:(i + shift)], loc='upper right', fontsize=18)
        plt.xlabel('Media Hora de despacho', fontsize=18)
        plt.ylabel(f'Consumo en SOC [%]', fontsize=18)
        plt.title(f'Delta SOC {sentido_titulo(ss)} (percentil 25%, 75% y Criterio Outlier Débil)',
                  fontsize=20)
        camera.snap()

    # anim = ani.ArtistAnimation(fig, ims, interval=500, repeat_delay=3000, blit=True)
    if True:
        WriterClass = animation.writers['ffmpeg']
        writer = WriterClass(fps=10, metadata=dict(artist='bww'), bitrate=1800)
        anim = camera.animate(interval=1500, repeat_delay=4000, blit=True)
        anim.save(f'mp4/dSOC_{ss}_{meses[-1]}.mp4', writer=writer)
    else:
        anim = camera.animate(interval=1500, repeat_delay=4000, blit=True)
        anim.save(f'mp4/dSOC_{ss}_{meses[-1]}.gif')
