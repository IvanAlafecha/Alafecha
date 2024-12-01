import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Cargar los datos
new_df = pd.read_excel('C:\\Users\\IVAN.LIPES\\Documents\\COSECHAS_INTERNOS_DEFINITIVO.xlsx')

# Limpiar los datos
new_df.columns = new_df.columns.str.strip()  # Eliminar espacios extra en los nombres de las columnas

# Definir las etiquetas de meses en formato 'ene-21', 'feb-21', ... 
labels = ['ene--21', 'feb--21', 'mar--21', 'abr--21', 'may--21', 'jun--21', 'jul--21', 'ago--21', 'sep--21', 'oct--21', 'nov--21', 'dic--21',
          'ene--22', 'feb--22', 'mar--22', 'abr--22', 'may--22', 'jun--22', 'jul--22', 'ago--22', 'sep--22', 'oct--22', 'nov--22', 'dic--22',
          'ene--23', 'feb--23', 'mar--23', 'abr--23', 'may--23', 'jun--23', 'jul--23', 'ago--23', 'sep--23', 'oct--23', 'nov--23', 'dic--23',
          'ene--24', 'feb--24', 'mar--24', 'abr--24', 'may--24', 'jun--24', 'jul--24', 'ago--24', 'sep--24', 'oct--24']

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
    html.H1("Análisis Cosecha por Fecha de Marcado", style={'textAlign': 'center', 'color': '#ef794b', 'fontSize': '36px'}),
    
    # Segmentador para seleccionar las etiquetas
    dcc.Dropdown(
        id='label-dropdown',
        options=[{'label': label, 'value': label} for label in labels],
        value=labels,  # Valor por defecto: todas las etiquetas seleccionadas
        multi=True,  # Permitir selección múltiple
        placeholder="Selecciona las etiquetas a graficar",
        style={'width': '80%', 'padding': '3px', 'margin': '10px'}  # Aumentado al 80% de ancho
    ),
    
    # Gráfico de líneas
    dcc.Graph(id='line-chart')
])

# Callback para actualizar el gráfico
@app.callback(
    Output('line-chart', 'figure'),
    [Input('label-dropdown', 'value')]
)
def update_graph(selected_labels):
    # Crear la figura vacía
    fig = go.Figure()

    # Iterar sobre las etiquetas seleccionadas y agregar trazos al gráfico
    for label in selected_labels:
        # Copiar los datos de la columna seleccionada
        series = new_df[['Meses', label]].copy()
        series.columns = ['Fecha', 'Valor']
        
        # Añadir un valor vacío al inicio de la serie para crear un espacio vacío
        series = pd.DataFrame({
            'Fecha': [None] + list(series['Fecha']),
            'Valor': [None] + list(series['Valor'])
        })
        
        # Reemplazar los valores nulos por NaN (Plotly no muestra NaN, interrumpe la línea en esos puntos)
        series['Valor'] = series['Valor'].apply(lambda x: float(x) if pd.notnull(x) else None)
        
        # Agregar un trazo para cada serie
        fig.add_trace(go.Scatter(x=series['Fecha'], y=series['Valor'], mode='lines+markers', name=label))

    # Ajustes del gráfico
    fig.update_layout(
        title="Recuperación Acumulada por Fecha de Marcado",
        title_x=0.5,
        xaxis_title="Meses",
        yaxis_title="Porcentaje Recuperación Acumulada",
        height=600,
        margin=dict(t=40, b=100, l=100, r=20),
        xaxis=dict(tickmode='array', tickvals=new_df['Meses'], ticktext=new_df['Meses'], tickangle=45),
        yaxis=dict(
            range=[0, 0.75],
             tickformat='.0%'),  # Ajustar el rango del eje Y entre 0 y 0.75
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
