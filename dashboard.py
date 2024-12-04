import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Cargar el archivo CSV con el delimitador correcto (en este caso, es un punto y coma ';')
df = pd.read_csv('https://drive.google.com/uc?export=download&id=12WYzIFROHM7nB12BScxHHiVNzwg0dr02', delimiter=';')
# Descargar el archivo de la URL debido que el tamaño del archivo no se puede cargar en la plataforma la base de data con el archivo de Jupyter, y agregar la ubicación del archivo en el Código
# Limpiar los datos eliminando filas con valores nulos
df = df.dropna()

# Convertir las columnas relevantes en datos numéricos, manejando errores (por ejemplo, valores no convertibles)
df['Valor_Total'] = pd.to_numeric(df['Valor_Total'], errors='coerce')
df['Copago'] = pd.to_numeric(df['Copago'], errors='coerce')
df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Diseño de la interfaz de usuario
app.layout = html.Div([
    # Título del análisis
    html.Div([
        html.Pre(children="ANALISIS DE VENTAS DISPENSACION",
                 style={"text-align": "center", "font-size": "100%", "color": "black"})
    ]),

    # Dropdown para seleccionar el tipo de gráfico
    html.Div([
        html.Label("Seleccione el tipo de gráfico:"),
        dcc.Dropdown(
            id='chart-type',  # Identificador del dropdown
            options=[
                {'label': 'Gráfico de dispersión', 'value': 'scatter'},
                {'label': 'Gráfico de burbujas', 'value': 'bubble'},
                {'label': 'Gráfico de área', 'value': 'area'},
                {'label': 'Gráfico de densidad', 'value': 'density'},
                {'label': 'Gráfico de barras', 'value': 'bar'}
            ],
            value='scatter'  # Valor inicial
        )
    ], style={'width': '20%', 'display': 'inline-block', 'padding': '10px'}),
    
    # RadioItems para seleccionar la categoría del eje X
    html.Div([
        html.Label(['X-axis categories to compare:'], style={'font-weight': 'bold'}),
        dcc.RadioItems(
            id='xaxis_raditem',  # Identificador del componente
            options=[
                {'label': 'Item_Formula', 'value': 'Item_Formula'},
                {'label': 'Copago', 'value': 'Copago'},
                {'label': 'Cuota_Moderadora', 'value': 'Cuota_Moderadora'},
                {'label': 'Tipo_Documento', 'value': 'Tipo_Documento'},
            ],
            value='Item_Formula',  # Valor inicial
            style={"width": "50%"}
        ),
    ]),

    # RadioItems para seleccionar la categoría del eje Y
    html.Div([
        html.Br(),
        html.Label(['Y-axis values to compare:'], style={'font-weight': 'bold'}),
        dcc.RadioItems(
            id='yaxis_raditem',  # Identificador del componente
            options=[
                {'label': 'Valor_Total', 'value': 'Valor_Total'},
                {'label': 'Copago', 'value': 'Copago'},
                {'label': 'Cantidad', 'value': 'Cantidad'},
            ],
            value='Copago',  # Valor inicial
            style={"width": "50%"}
        ),
    ]),

    # Contenedor donde se mostrará el gráfico
    html.Div([
        dcc.Graph(id='main-plot', style={'height': '500px', 'width': '100%'})  # Componente gráfico principal
    ])
])

# Función que crea las gráficas con base en las selecciones del usuario
def create_figure(df, chart_type, x_axis, y_axis):
    # Verificar si la columna del eje Y es numérica
    if not pd.api.types.is_numeric_dtype(df[y_axis]):
        return px.scatter(title=f'Error: {y_axis} debe ser numérico para {chart_type}')
    
    # Crear el gráfico de acuerdo al tipo seleccionado
    if chart_type == 'scatter':
        fig = px.scatter(df, x=x_axis, y=y_axis, color='Tipo_Documento', title=f'{y_axis} vs {x_axis} (Dispersión)')
    elif chart_type == 'bubble':
        # Verificar si el valor Y es numérico para gráfico de burbujas
        if pd.api.types.is_numeric_dtype(df[y_axis]):
            fig = px.scatter(df, x=x_axis, y=y_axis, size=y_axis, color='Tipo_Documento', title=f'{y_axis} vs {x_axis} (Burbujas)')
        else:
            fig = px.scatter(df, x=x_axis, y=y_axis, color='Tipo_Documento', title=f'Error: {y_axis} debe ser numérico para Burbujas')
    elif chart_type == 'area':
        fig = px.area(df, x=x_axis, y=y_axis, color='Tipo_Documento', title=f'{y_axis} vs {x_axis} (Área)')
    elif chart_type == 'density':
        fig = px.density_contour(df, x=x_axis, y=y_axis, color='Tipo_Documento', title=f'{y_axis} vs {x_axis} (Densidad)')
    elif chart_type == 'bar':
        fig = px.bar(df, x=x_axis, y=y_axis, color='Tipo_Documento', title=f'{y_axis} vs {x_axis} (Barras)')
    
    return fig

# Callback que se activa cuando se cambia una opción en el dropdown o los RadioItems
@app.callback(
    Output('main-plot', 'figure'),  # Salida que actualiza el gráfico
    [Input('chart-type', 'value'),  # Entrada del tipo de gráfico seleccionado
     Input('xaxis_raditem', 'value'),  # Entrada del eje X
     Input('yaxis_raditem', 'value')]  # Entrada del eje Y
)
def update_graph(chart_type, x_axis, y_axis):
    # Retorna la figura generada en base a las selecciones
    return create_figure(df, chart_type, x_axis, y_axis)

# Correr la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)  # Iniciar el servidor de la app Dash
