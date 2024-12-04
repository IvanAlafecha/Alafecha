import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Cargar los datos
new_df = pd.read_excel('C:\\Users\\IVAN.LIPES\\Documents\\Modelo_dc\\Base_Consolidados.xlsx')

# Limpiar los datos
new_df = new_df.dropna(subset=['Año', 'Mes'])  # Eliminar filas con valores nulos en 'Año' o 'Mes'
new_df['Año'] = new_df['Año'].astype(int)  # Asegurarnos de que los Años sean enteros
new_df['Mes'] = new_df['Mes'].str.capitalize()  # Convertir la primera letra de los meses a mayúscula para consistencia

# Asegurarnos de que no haya espacios en los nombres de las columnas
new_df.columns = new_df.columns.str.strip()

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    # Contenedor para la imagen en la esquina superior derecha
    html.Div(
        children=[
            html.Img(src='assets/alafecha_logo.jpg', style={
                'position': 'absolute',
                'top': '10px',
                'right': '10px',
                'width': '200px',  # Ajusta el tamaño de la imagen según lo necesites
            })
        ],
        style={'position': 'relative'}
    ),
    
    # Título principal
    html.H1("Análisis Cosecha por Fecha de Mercado", style={'textAlign': 'center', 'color': '#ef794b', 'fontSize': '36px'}),
    
    # Filtros para Año y Mes en una sola fila (usando Flexbox)
    html.Div(
        children=[
            # Dropdown para Año
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in new_df['Año'].unique()],
                value=[],  # Cambiar a una lista vacía por defecto para permitir la selección múltiple
                placeholder="Selecciona los Años",
                multi=True,  # Permitir selección múltiple
                style={'width': '48%', 'padding': '3px', 'margin': '10px'}
            ),
            # Dropdown para Mes
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': month, 'value': month} for month in new_df['Mes'].unique()],
                value=None,  # Si no selecciona, muestra todos los Meses
                multi=True,
                placeholder="Selecciona los Meses",
                style={'width': '48%', 'padding': '3px', 'margin': '10px'}
            ),
        ],
        style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between', 'alignItems': 'center', 'flexWrap': 'nowrap'}  # Alineación horizontal
    ),
    
    # Gráfico de barras
    dcc.Graph(id='bar-chart')
])

# Callback para actualizar el gráfico
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_graph(selected_years, selected_months):
    # Si no se selecciona ningún Año ni Mes, mostramos todo el consolidado
    if not selected_years and (selected_months is None or len(selected_months) == 0):
        filtered_df = new_df
    elif selected_years and (selected_months is None or len(selected_months) == 0):
        # Si solo se seleccionan años, mostramos todos los meses de esos años
        filtered_df = new_df[new_df['Año'].isin(selected_years)]
    elif not selected_years and selected_months:
        # Si solo se seleccionan meses, mostramos todos los años para los meses seleccionados
        filtered_df = new_df[new_df['Mes'].isin(selected_months)]
    else:
        # Si se seleccionan tanto Años como Meses, filtramos por ambos
        filtered_df = new_df[(new_df['Año'].isin(selected_years)) & (new_df['Mes'].isin(selected_months))]
    
    # Sumar los valores de los Meses seleccionados
    months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre']
    
    # Si no se seleccionaron meses, tomamos todos los meses del año o el total
    if selected_months is None or len(selected_months) == 0:
        monthly_sum = filtered_df[months].sum()
    else:
        monthly_sum = filtered_df[months].sum()

    # Crear el DataFrame para el gráfico
    sum_df = monthly_sum.reset_index()
    sum_df.columns = ['Mes', 'Valor']
    
    # Crear el gráfico de barras
    fig = px.bar(
        sum_df,
        x='Mes',
        y='Valor',
        title=f"Recaudo Pagos por Fecha de Mercado ({', '.join(map(str, selected_years))})" if selected_years else "Recaudo Pagos por Fecha de Mercado Juridica",
        labels={'Valor': 'Suma Recaudo Por Mes'},
        category_orders={'Mes': months}  # Ordenamos los Meses de manera cronológica
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
