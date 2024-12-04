import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Cargar los datos
new_df = pd.read_excel('C:\\Users\\IVAN.LIPES\\Documents\\Prueba.xlsx')

# Limpiar los datos
new_df.columns = new_df.columns.str.strip()  # Eliminar espacios extra en los nombres de las columnas

# Definir las etiquetas de meses en formato 'ene-21', 'feb-21', ... 
labels = ['Promedio', 'ene--21', 'feb--21', 'mar--21', 'abr--21', 'may--21', 'jun--21', 'jul--21', 'ago--21', 'sep--21', 'oct--21', 'nov--21', 'dic--21',
          'ene--22', 'feb--22', 'mar--22', 'abr--22', 'may--22', 'jun--22', 'jul--22', 'ago--22', 'sep--22', 'oct--22', 'nov--22', 'dic--22',
          'ene--23', 'feb--23', 'mar--23', 'abr--23', 'may--23', 'jun--23', 'jul--23', 'ago--23', 'sep--23', 'oct--23', 'nov--23', 'dic--23',
          'ene--24', 'feb--24', 'mar--24', 'abr--24', 'may--24', 'jun--24', 'jul--24', 'ago--24', 'sep--24', 'oct--24']

# Cargar el segundo dataframe Recaudo
Recaudo = pd.read_excel('C:\\Users\\IVAN.LIPES\\Documents\\Recaudo_pagos.xlsx')

# Limpiar los datos
Recaudo.columns = Recaudo.columns.str.strip()  # Eliminar espacios extra en los nombres de las columnas

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    # Contenedor para la imagen en la esquina superior derecha
    html.Div(
        children=[html.Img(src='assets/alafecha_logo.jpg', style={
            'position': 'absolute',
            'top': '10px',
            'right': '10px',
            'width': '200px',  # Ajusta el tamaño de la imagen según lo necesites
        })],
        style={'position': 'relative'}
    ),
    
    # Título principal
    html.H1("Análisis Cosecha por Fecha de Marcado"),
    
    # Segmentador para seleccionar las etiquetas
   dcc.Dropdown(
    id='label-dropdown',
    options=[{'label': label, 'value': label} for label in labels],
    value=labels,  # Valor por defecto: todas las etiquetas seleccionadas
    multi=True,  # Permitir selección múltiple
    placeholder="Selecciona las etiquetas a graficar",
    style={'width': '300px'}  # Ajuste el ancho a un valor fijo (en píxeles) o un porcentaje
),
    
    # Gráfico de líneas original
    dcc.Graph(id='line-chart'),
    
    # Título para el nuevo gráfico
    html.H2("Recaudo Mensual y Capital Neto Mensual"),
    
    # Gráfico de líneas del nuevo dataframe 'Recaudo'
    dcc.Graph(id='recaudo-chart')
])

# Callback para actualizar el gráfico original
@app.callback(
    Output('line-chart', 'figure'),
    [Input('label-dropdown', 'value')]
)
def update_graph(selected_labels):
    # Filtrar las columnas necesarias, excluyendo la columna 'Meses'
    selected_columns = selected_labels  # Estas son las etiquetas de las fechas como 'ene--21', 'feb--21', etc.

    # Filtrar el DataFrame para que solo contenga la columna 'Meses' y las columnas seleccionadas
    filtered_df = new_df[['Meses'] + selected_columns]

    # Renombrar las columnas para que el gráfico sea claro
    filtered_df.columns = ['Fecha'] + list(filtered_df.columns[1:])

    # Usar lambda para eliminar los valores nulos (por ejemplo, usando dropna)
    for col in selected_columns:
        filtered_df[col] = filtered_df.apply(lambda row: row[col] if pd.notnull(row[col]) else None, axis=1)

    # Eliminar filas donde todas las series seleccionadas sean nulas
    filtered_df = filtered_df.dropna(subset=selected_columns, how='all')

    # Crear el gráfico de líneas
    fig = px.line(
        filtered_df,
        x='Fecha',  # Las fechas serán el eje X (meses)
        y=selected_columns,  # Las columnas seleccionadas serán las series
        title="Recuperación Acumulada por Fecha de Marcado",
        labels={'Fecha': 'Mes', 'value': 'Porcentaje Recuperación Acumulada'},
        markers=True  # Añadir puntos a la línea
    )
    
    # Ajustes para mejorar la visualización
    fig.update_layout(
        title_x=0.5,  # Centrar el título
        xaxis=dict(
            tickmode='array',
            tickvals=filtered_df['Fecha'],  # Usar los valores de 'Fecha' (Meses)
            ticktext=filtered_df['Fecha'],  # Etiquetas de los meses
            title='Meses',
            tickangle=45,  # Rotar las etiquetas del eje X para que no se solapen
        ),
        yaxis=dict(
            title='Porcentaje Recuperación Acumulada',
            tickformat='.0%',  # Formato del eje Y como porcentaje
            range=[0, 0.75],  # Ajuste del rango del eje Y entre 0 y 0.75
        ),
        height=600,  # Ajustar el tamaño del gráfico para que sea más grande
        margin=dict(t=40, b=100, l=100, r=20)  # Ajustar los márgenes para dar espacio a las etiquetas
    )
    
    return fig

# Convertir valores a millones de pesos
Recaudo['Recaudo Mensual'] = Recaudo['Recaudo Mensual'] / 1000000
Recaudo['Capital Neto Mensual'] = Recaudo['Capital Neto Mensual'] / 1000000

# Callback para actualizar el gráfico de recaudo
@app.callback(
    Output('recaudo-chart', 'figure'),
    [Input('recaudo-chart', 'id')]
)
def update_recaudo_graph(_):
    # Eliminar los valores nulos de las columnas 'Recaudo Mensual' y 'Capital Neto Mensual'
    Recaudo.loc[:, 'Recaudo Mensual'] = Recaudo['Recaudo Mensual'].where(pd.notnull(Recaudo['Recaudo Mensual']))
    Recaudo.loc[:, 'Capital Neto Mensual'] = Recaudo['Capital Neto Mensual'].where(pd.notnull(Recaudo['Capital Neto Mensual']))

    # Crear el gráfico para "Recaudo Mensual" y "Capital Neto Mensual"
    fig = px.line(
        Recaudo,
        x='Meses',  # Asegúrate de que el dataframe 'Recaudo' tenga la columna 'Meses'
        y=['Recaudo Mensual', 'Capital Neto Mensual'],
        title="Recaudo Mensual y Capital Neto Mensual",
        labels={'Meses': 'Mes', 'value': 'Valor'},
        markers=True
    )
    
    # Ajustes para mejorar la visualización
    fig.update_layout(
        title_x=0.5,  # Centrar el título
        xaxis=dict(
            tickmode='array',
            tickvals=Recaudo['Meses'],
            ticktext=Recaudo['Meses'],
            title='Meses',
            tickangle=45,  # Rotar las etiquetas del eje X para que no se solapen
        ),
        yaxis=dict(
            title='Recaudo y Capital Neto Mensual (millones de pesos)',
            tickformat='.0f',  # Formato del eje Y para mostrar dos decimales
            range=[0, 25000],  # Ajustar el rango del eje Y en millones
        ),
        height=600,  # Ajustar el tamaño del gráfico
        margin=dict(t=40, b=100, l=100, r=20)
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
