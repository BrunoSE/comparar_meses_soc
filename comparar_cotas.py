import pandas as pd
import plotly.graph_objects as go

carpeta_mes = {'Nov20': 'graficos_2020_11_02_2020_11_23',
               'Dic20': 'graficos_2020_11_02_2020_12_21',
               'Ene21': 'graficos_2020_11_02_2021_01_25',
               'Feb21': 'graficos_2020_11_02_2021_02_22',
               'Mar21': 'graficos_2020_11_02_2021_03_22'
               }

nombre_archivo = 'Cotas_resumen.xlsx'

df = {}
for mes in carpeta_mes:
    df[mes] = (pd.read_excel(f'{carpeta_mes[mes]}/{nombre_archivo}',
                             sheet_name=None, index_col=1))

print('Servicios en Nov20', df['Nov20'].keys())
print('Meses con datos', df.keys())

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
        if ss in df[mes] and df25.empty:
            df25 = df[mes][ss][[col_perc]].copy()
            df25.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
            continue

        dfx = df[mes][ss][[col_perc]].copy()
        dfx.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
        df25 = df25.merge(dfx, how='outer',
                          left_index=True, right_index=True,
                          suffixes=['', f''])

    col_perc = 'perc75'
    df75 = pd.DataFrame()

    for mes in carpeta_mes:
        if ss in df[mes] and df75.empty:
            df75 = df[mes][ss][[col_perc]].copy()
            df75.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
            continue

        dfx = df[mes][ss][[col_perc]].copy()
        dfx.rename(columns={f'{col_perc}': f'{mes}'}, inplace=True)
        df75 = df75.merge(dfx, how='outer',
                          left_index=True, right_index=True,
                          suffixes=['', f''])

    ddf = df25.to_dict('index')
    meses = list(df25.columns)
    x_ = []
    y_ = []
    z_ = []

    for mes in meses:
        for key1 in ddf:
            x_.append(mes)
            y_.append(key1)
            z_.append(ddf[key1][mes])
        x_.append(mes)
        y_.append('23:59')
        z_.append(float('nan'))

    fig6 = go.Figure(layout=go.Layout(
                     title=go.layout.Title(text=f"Delta SOC por MH {ss} entre {meses[0]}-{meses[-1]}"),
                     margin=dict(b=0, l=0, r=0, t=25)))

    fig6.update_layout(title={'y': 0.9,
                              'x': 0.5,
                              'xanchor': 'center',
                              'yanchor': 'top'})

    fig6.add_trace(go.Scatter3d(x=x_, y=y_, z=z_,
                                mode='lines+markers',
                                marker=dict(size=6,
                                            opacity=0.9,
                                            symbol='diamond'
                                            ),
                                name='perc25'
                                ))

    ddf = df75.to_dict('index')
    meses = list(df75.columns)
    x_ = []
    y_ = []
    z_ = []

    for mes in meses:
        for key1 in ddf:
            x_.append(mes)
            y_.append(key1)
            z_.append(ddf[key1][mes])
        x_.append(mes)
        y_.append('23:59')
        z_.append(float('nan'))

    fig6.add_trace(go.Scatter3d(x=x_, y=y_, z=z_,
                                mode='lines+markers',
                                marker=dict(size=6,
                                            opacity=0.9,
                                            symbol='circle'
                                            ),
                                name='perc75'
                                ))

    fig6.update_layout(scene_aspectmode='manual',
                       scene_aspectratio=dict(x=1.6, y=1.2, z=0.8),
                       scene=dict(xaxis_title='Mes',
                                  yaxis_title='Media Hora',
                                  zaxis_title='Delta SOC [%]')
                       )

    fig6.write_html(f'dSOC_{ss}_{meses[-1]}.html',
                    config={'scrollZoom': True, 'displayModeBar': True})
