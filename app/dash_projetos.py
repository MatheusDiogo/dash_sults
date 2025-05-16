import pandas as pd
import dash
from dash import html, dcc, Input, Output, dash_table, Dash
import dash_bootstrap_components as dbc
import datetime
import plotly.graph_objects as go

# Carrega os dados
file_path = 'data/projetos_sults.xlsx'
df = pd.read_excel(file_path)

# Converte colunas de datas
for col in ['dtCriacao', 'dtConclusao', 'dtPausado', 'dtFim']:
    df[col] = pd.to_datetime(df[col], errors='coerce', utc=True).dt.tz_localize(None)

hoje = datetime.datetime.now()

def calcula_status(row):
    if row['concluido'] == True:
        return 'Concluídos'
    elif row['pausado'] == True:
        return 'Pausados'
    elif (row['ativo'] == True) and (row['concluido'] == False) and (row['pausado'] == False):
        if (row['dtFim'] < hoje) and (row['concluido'] == False):
            return 'Atrasados'
        else:
            return 'Em Andamento'
    else:
        return 'Outros'

df['status'] = df.apply(calcula_status, axis=1)

# Função para truncar o nome, exemplo máximo 12 caracteres
def truncate_name(name, max_len=20):
    return (name[:max_len] + '...') if len(name) > max_len else name

# Preparar listas únicas para filtros
unidades_opcoes = [{'label': u, 'value': u} for u in sorted(df['unidade'].dropna().unique())]
responsaveis_opcoes = [{'label': r, 'value': r} for r in sorted(df['responsavel'].dropna().unique())]

# Inicializa o app com tema Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Projetos Grau"

# Navbar + filtros
navbar = dbc.Navbar(
    dbc.Container(
        dbc.Row([
            # LOGO + TÍTULO
            dbc.Col(
                dbc.Row([
                    dbc.Col(
                        html.Img(src="/assets/logo.png", height="40px"),
                        width="auto"
                    ),
                    dbc.Col(
                        dbc.NavbarBrand("Projetos Grau", style={
                            "fontWeight": "bold",
                            "fontSize": "1.5rem",
                            "color": "white",
                            "marginLeft": "10px"
                        }),
                        width="auto"
                    )
                ], align="center", className="g-0"),
                width="auto"
            ),

            # FILTROS NA DIREITA
            dbc.Col(
                dbc.Row([
                    dbc.Col([
                        html.Label("Unidade", style={
                            "color": "white",
                            "fontSize": "0.8rem",
                            "marginBottom": "2px"
                        }),
                        dcc.Dropdown(
                            id='filtro_unidade',
                            options=unidades_opcoes,
                            multi=True,
                            placeholder="Unidades...",
                            style={"fontSize": "0.8rem", "height": "32px"}
                        ),
                    ], width="auto", style={"minWidth": "220px", "marginRight": "10px"}),

                    dbc.Col([
                        html.Label("Responsável", style={
                            "color": "white",
                            "fontSize": "0.8rem",
                            "marginBottom": "2px"
                        }),
                        dcc.Dropdown(
                            id='filtro_responsavel',
                            options=responsaveis_opcoes,
                            multi=True,
                            placeholder="Responsáveis...",
                            style={"fontSize": "0.8rem", "height": "32px"}
                        ),
                    ], width="auto", style={"minWidth": "220px", "marginRight": "10px"}),

                    dbc.Col([
                        html.Label("Período", style={
                            "color": "white",
                            "fontSize": "0.8rem",
                            "marginBottom": "2px"
                        }),
                        dcc.DatePickerRange(
                            id='filtro_periodo',
                            start_date=df['dtCriacao'].min().date(),
                            end_date=df['dtCriacao'].max().date(),
                            display_format='DD/MM/YYYY',
                            style={"fontSize": "0.8rem", "height": "32px"}
                        ),
                    ], width="auto", style={"minWidth": "250px"}),
                ],
                className="gx-2 justify-content-end",
                align="center"),
                width=True
            )
        ],
        className="w-100 justify-content-between align-items-center"),
    ),
    color="#80BF6E",
    dark=False,
    style={
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.3)",
        "paddingTop": "0.4rem",
        "paddingBottom": "0.4rem"
    },
    className="mb-3"
)

# Cards, gráfico e tabela vão ficar dentro do container principal
app.layout = html.Div([
    navbar,

    dbc.Container([
        # Cards para os indicadores (valores dinâmicos, atualizados via callback)
        dbc.Row([
            dbc.Col(dbc.Card(id='card_concluidos', className="m-2 shadow-sm"), md=3),
            dbc.Col(dbc.Card(id='card_andamento', className="m-2 shadow-sm"), md=3),
            dbc.Col(dbc.Card(id='card_atrasado', className="m-2 shadow-sm"), md=3),
            dbc.Col(dbc.Card(id='card_pausados', className="m-2 shadow-sm"), md=3),
        ], className="my-4"),

        html.Hr(),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Projetos Pausados ou Atrasados", className="card-title mb-3"),
                        dash_table.DataTable(
                            id='tabela_pausados_atrasados',
                            columns=[
                                {"name": "Projeto", "id": "nome"},
                                {"name": "Unidade", "id": "unidade"},
                                {"name": "Status", "id": "status"},
                                {"name": "Responsável", "id": "responsavel"},
                                {"name": "Data Início", "id": "dtCriacao"},
                                {"name": "Data Planejada", "id": "dtFim"},
                            ],
                            style_table={
                                "overflowY": "auto",
                                "maxHeight": "400px",
                                "overflowX": "auto",
                                "border": "1px solid #dee2e6",
                            },
                            style_cell={
                                "textAlign": "left",
                                "padding": "8px",
                                "fontFamily": "Arial",
                                "fontSize": "14px",
                                "borderBottom": "1px solid #dee2e6",
                            },
                            style_header={
                                "backgroundColor": "#80BF6E",
                                "color": "white",
                                "fontWeight": "bold",
                                "fontSize": "15px",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "#f9f9f9",
                                }
                            ],
                            page_action='none'
                        ),
                    ])
                ], className="shadow-sm m-2")
            ], md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Quantidade de Projetos por Responsável e Status", className="card-title"),
                        dcc.Graph(
                            id='grafico_status',
                            config={'displayModeBar': False},
                            style={"maxHeight": "408px", "overflowY": "auto", "overflowX": "auto"},
                        )
                    ])
                ], className="shadow-sm m-2")
            ], md=6),
        ])
    ], fluid=True),
])

# Callback para atualizar cards, tabela e gráfico com base nos filtros
@app.callback(
    Output('card_concluidos', 'children'),
    Output('card_andamento', 'children'),
    Output('card_atrasado', 'children'),
    Output('card_pausados', 'children'),
    Output('tabela_pausados_atrasados', 'data'),
    Output('grafico_status', 'figure'),
    Input('filtro_unidade', 'value'),
    Input('filtro_responsavel', 'value'),
    Input('filtro_periodo', 'start_date'),
    Input('filtro_periodo', 'end_date'),
)
def atualiza_dashboard(unidades_selecionadas, responsaveis_selecionados, data_inicio, data_fim):
    df_filtrado = df.copy()

    # Filtra unidades
    if unidades_selecionadas:
        df_filtrado = df_filtrado[df_filtrado['unidade'].isin(unidades_selecionadas)]

    # Filtra responsáveis
    if responsaveis_selecionados:
        df_filtrado = df_filtrado[df_filtrado['responsavel'].isin(responsaveis_selecionados)]

    # Filtra período dtCriacao
    if data_inicio:
        df_filtrado = df_filtrado[df_filtrado['dtCriacao'] >= pd.to_datetime(data_inicio)]
    if data_fim:
        df_filtrado = df_filtrado[df_filtrado['dtCriacao'] <= pd.to_datetime(data_fim)]

    # Calcula os indicadores
    concluidos = df_filtrado[df_filtrado['status'] == 'Concluídos'].shape[0]
    pausados = df_filtrado[df_filtrado['status'] == 'Pausados'].shape[0]
    andamento = df_filtrado[df_filtrado['status'] == 'Em Andamento'].shape[0]
    atrasados = df_filtrado[df_filtrado['status'] == 'Atrasados'].shape[0]

    # Atualiza cards
    card_concluidos = dbc.CardBody([
        html.H5("Projetos Concluídos", className="card-title"),
        html.H2(f"{concluidos}", className="card-text text-success"),
    ])
    card_pausados = dbc.CardBody([
        html.H5("Projetos Pausados", className="card-title"),
        html.H2(f"{pausados}", className="card-text text-warning"),
    ])
    card_andamento = dbc.CardBody([
        html.H5("Projetos em Andamento", className="card-title"),
        html.H2(f"{andamento}", className="card-text text-primary"),
    ])
    card_atrasados = dbc.CardBody([
        html.H5("Projetos Atrasados", className="card-title"),
        html.H2(f"{atrasados}", className="card-text text-danger"),
    ])

    # Prepara dados para tabela pausados e atrasados
    df_pausados_atrasados = df_filtrado[df_filtrado['status'].isin(['Pausados', 'Atrasados'])].copy()

    # Ajustar datas para string dd/mm/aaaa
    df_pausados_atrasados['dtCriacao'] = df_pausados_atrasados['dtCriacao'].dt.strftime('%d/%m/%Y')
    df_pausados_atrasados['dtFim'] = df_pausados_atrasados['dtFim'].dt.strftime('%d/%m/%Y')

    tabela_data = df_pausados_atrasados[[
        'nome', 'unidade', 'status', 'responsavel', 'dtCriacao', 'dtFim'
    ]].to_dict('records')

    # Ordena os responsáveis pela quantidade total de projetos em ordem decrescente
    totais = df_filtrado.groupby('responsavel').size().sort_values(ascending=False)
    responsaveis = totais.index.tolist()
    responsaveis_full = [' '.join([w.capitalize() for w in name.split()]) for name in responsaveis]

    # Função para truncar o nome, exemplo máximo 12 caracteres
    def truncate_name(name, max_len=20):
        return (name[:max_len] + '...') if len(name) > max_len else name

    # Lista com nomes truncados
    responsaveis_trunc = [truncate_name(r, 20) for r in responsaveis_full]

    # Função para contar projetos por status e responsável
    def contar_por_status(status):
        temp = df_filtrado[df_filtrado['status'] == status].groupby('responsavel').size()
        return [temp.get(r, 0) for r in responsaveis]

    # Cores personalizadas para cada status
    cores_status = {
        'Concluídos': '#28a745',  # verde
        'Pausados': '#ffc107',    # amarelo
        'Em Andamento': '#007bff',# azul
        'Atrasados': '#dc3545',   # vermelho
    }

    # Criando as barras para cada status
    barras = []
    for status in ['Concluídos', 'Pausados', 'Em Andamento', 'Atrasados']:
        barras.append(
            go.Bar(
                y=responsaveis_trunc ,
                x=contar_por_status(status),
                name=status,
                orientation='h',
                marker_color=cores_status[status],
                hovertemplate='<b>%{customdata}</b><br>Status: '+status+'<br>Projetos: %{x}<extra></extra>',
                customdata=responsaveis_full,        # para mostrar nome completo no hover
            )
        )

    # Montando o layout do gráfico
    fig_status = go.Figure(data=barras)

    fig_status.update_layout(
        barmode='stack',
        xaxis=dict(title='Quantidade', showgrid=True, gridcolor='#e5e5e5'),
        yaxis=dict(title='Responsável', autorange='reversed', tickfont=dict(size=18)),
        legend=dict(title='Status', bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
        margin=dict(l=10, r=20, t=15, b=10),
        plot_bgcolor='white',
        font=dict(family='Arial', size=14),
        height = max(50 * len(responsaveis_full), 100)
    )

    fig_status.update_traces(marker_line_width=0, width=0.8)

    return card_concluidos, card_andamento, card_atrasados, card_pausados, tabela_data, fig_status

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
