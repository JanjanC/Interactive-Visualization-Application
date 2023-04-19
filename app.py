# -*- coding: utf-8 -*-

import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, dash_table, Input, Output, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import geojson
import enum

times_df = pd.read_csv('datasets/times_2011_2023.csv')
times_complete_columns = ['Teaching', 'International', 'Research', 'Citations', 'Income']
times_year_columns = {'{}'.format(i): times_complete_columns for i in range(2011, 2024)}

shanghai_df = pd.read_csv('datasets/shanghai_2012_2022.csv', encoding='cp1252')
shanghai_complete_columns = ['Alumni', 'Award', 'HiCi', 'N&S', 'PUB', 'PCP']
shanghai_year_columns = {'{}'.format(i): shanghai_complete_columns for i in range(2012, 2023)}

cwur_df = pd.read_csv('datasets/cwur_2012_2022.csv')
cwur_complete_columns = ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Broad Impact', 'Patents', 'Research Output', 'Research Performance']
cwur_year_columns = {
    '2012': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Patents'],
    '2013': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Patents'],
    '2014': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Broad Impact', 'Patents'],
    '2015': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Broad Impact', 'Patents'],
    '2016': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Broad Impact', 'Patents'],
    '2017': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Broad Impact', 'Patents'],
    '2018': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Publications', 'Influence', 'Citations', 'Research Output'],
    '2019': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Research Performance'],
    '2020': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Research Performance'],
    '2021': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Research Performance'],
    '2022': ['Quality of Education', 'Alumni Employment', 'Quality of Faculty', 'Research Performance'],
}


class Rankings(enum.Enum):
    times = 0
    shanghai = 1
    cwur = 2


rankings_df = [times_df, shanghai_df, cwur_df]
rankings_names = ['Times Higher Education World Rankings',
                  'Academic Ranking of World Universities', 'Center for World University Rankings']
rankings_complete_columns = [times_complete_columns,
                             shanghai_complete_columns, cwur_complete_columns]
rankings_year_columns = [times_year_columns,
                         shanghai_year_columns, cwur_year_columns]

token = open("datasets/.mapbox_token").read()
with open('datasets/natural-earth-countries-1_110m@public.geojson') as f:
    countries = geojson.load(f)

# Global Variables for the Selected Data
# Main Dashboard
current_main_rankings = Rankings.times
current_main_university_list = pd.DataFrame()
current_main_criterion = "Overall Score"
current_main_year = 2022

# University Overview Page
current_university_rankings = Rankings.times
current_university_name = "Harvard University"
current_university_year = 2022

activated_class = 'btn btn-primary mx-3'
deactivated_class = 'btn btn-secondary mx-3'

# Main Dashboard Buttons
btn_main_times_class = activated_class
btn_main_shanghai_class = deactivated_class
btn_main_cwur_class = deactivated_class

# University Overview Buttons
btn_univ_times_class = activated_class
btn_univ_shanghai_class = deactivated_class
btn_univ_cwur_class = deactivated_class

# Main Dashboard

# Chloropleth Map
def load_choropleth_map(university_rankings, main_year):
    current_df = rankings_df[university_rankings.value]
    current_df = current_df[current_df['Year'] == main_year]
    country_df = current_df[['Country', 'University']].groupby(['Country'], as_index = False).count()
    choropleth_fig = px.choropleth_mapbox(country_df,
                                    geojson = countries,
                                    featureidkey = 'properties.name_en',
                                    locations = 'Country',
                                    color = 'University',
                                    zoom = 0.2,
                                    color_continuous_scale = px.colors.sequential.Blues
                                    )
    choropleth_fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0}, mapbox_accesstoken = token)
    
    return choropleth_fig

choropleth_mapbox = load_choropleth_map(current_main_rankings, current_main_year)

# Bar Chart (Criteria Comparision)
def load_main_bar_chart(university_list, university_rankings, main_year):
    if not university_list.empty:
        criteria = ["University"] + rankings_complete_columns[university_rankings.value]
        current_df = university_list[criteria]
        fig = px.bar(current_df, x=criteria, y="University", barmode='group', labels=criteria)
        fig.update_layout(width=800, height=600)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig.update_layout(dict(template="plotly_white"))
        fig.update_layout(
            title="<b>{} {}</b> University Criteria".format(main_year, rankings_names[university_rankings.value]),
            title_x=0.5,
            xaxis_title="Score", 
            yaxis_title="University"
        )
        return fig
    else:
        fig = go.Figure().add_annotation(text="Select a University from the Table", showarrow=False, font={"size": 20}).update_xaxes(visible=False).update_yaxes(visible=False)
        fig.update_layout(width=800, height=600)
        return fig

main_trend_fig = load_main_bar_chart(current_main_university_list, current_main_rankings, current_main_year)

# Line Chart(Trend)
def load_main_line_chart(university_list, university_rankings, criterion):
    if not university_list.empty:
        fig = make_subplots(rows=len(university_list), cols=1, subplot_titles=university_list["University"].values.tolist())

        for index, university_name in enumerate(university_list["University"]):
            current_df = rankings_df[university_rankings.value]
            university_df = current_df[(current_df["University"] == university_name)].sort_values(by=["Year"], ascending=True)
            year_list = university_df["Year"].values.tolist()
            criteria_list = university_df[criterion].values.tolist()

            color_index = (['World Rank', 'Overall Score'] + rankings_year_columns[current_main_rankings.value][str(current_main_year)]).index(criterion) - 2
            fig.add_trace(
                go.Scatter(
                    x=year_list, y=criteria_list, name=university_name, mode='markers+lines',
                    line=dict(color=px.colors.qualitative.Plotly[color_index]),
                    meta=[university_name, criterion],
                    hovertemplate="<b>%{meta[0]}</b><br><b>Year</b>: %{x}<br><b>%{meta[1]}</b>: %{y}<extra></extra>"
                ),
                row=index+1,
                col=1
            )

        fig.update_layout(showlegend=False)
        fig.update_layout(width=800, height=600)
        fig.update_layout(
            title_text="<b>{}</b> Trend in the <b>{}</b>".format(criterion, rankings_names[university_rankings.value]),
            title_x=0.5,
            xaxis_title="Year", 
            yaxis_title="Score"
        )
        
        return fig
    else:
        fig = go.Figure().add_annotation(text="Select a University from the Table", showarrow=False, font={"size": 20}).update_xaxes(visible=False).update_yaxes(visible=False)
        fig.update_layout(width=800, height=600)
        return fig


main_line_fig = load_main_line_chart(current_main_university_list, current_main_rankings, current_main_criterion)

# University Page
# Line Charts
def load_university_line_chart(university_rankings, university_name):
    current_df = rankings_df[university_rankings.value]
    criteria = ["World Rank", "Overall Score"] + rankings_complete_columns[university_rankings.value]
    fig = make_subplots(rows=math.ceil(len(criteria) / 2), cols=2, subplot_titles=criteria)
    current_df_conditions = (current_df["University"] == university_name)
    current_df = current_df[current_df_conditions].sort_values(by=["Year"], ascending=True)
    if not current_df.empty:
        for index, criterion in enumerate(criteria):
            year_list = current_df["Year"].values.tolist()

            if criterion == "World Rank":
                criteria_list = current_df["World Rank Order"].values.tolist()
                fig.add_trace(
                    go.Scatter(
                        x=year_list, y=criteria_list, name=criterion, mode='markers+lines',
                        meta=criterion,
                        customdata=current_df["World Rank"].values.tolist(),
                        marker=dict(color=px.colors.qualitative.Plotly[(index-2) % 10]),
                        hovertemplate="<b>Year</b>: %{x}<br><b>%{meta}</b>: %{customdata}<extra></extra>"
                    ),
                    row=index // 2 + 1,
                    col=index % 2 + 1
                )
            else:
                criteria_list = current_df[criterion].values.tolist()
                fig.add_trace(
                    go.Scatter(
                        x=year_list, y=criteria_list, name=criterion, mode='markers+lines',
                        meta=criterion,
                        marker=dict(color=px.colors.qualitative.Plotly[(index-2) % 10]),
                        hovertemplate="<b>Year</b>: %{x}<br><b>%{meta}</b>: %{y}<extra></extra>"
                    ),
                    row=index // 2 + 1,
                    col=index % 2 + 1
                )

        fig.update_yaxes(autorange="reversed", row=1, col=1)
        fig.update_layout(height=600, width=1200, title_text="Historical Performance of <b>{}</b> in the <b>{}</b>".format(university_name, rankings_names[university_rankings.value]))
        fig.update_layout(showlegend=False)
        return fig
    else:
        fig = go.Figure().add_annotation(text="No Data", showarrow=False, font={"size": 20}).update_xaxes(visible=False).update_yaxes(visible=False)
        fig.update_layout(height=600, width=1200)
        return fig


university_trend_fig = load_university_line_chart(current_university_rankings, current_university_name)

# Radar Charts

def load_university_radar_chart(university_name, university_year):
    fig = make_subplots(
        rows=1, 
        cols=3, 
        specs=[[{"type": "polar"}, {"type": "polar"}, {"type": "polar"}]], 
        subplot_titles=["{} {}".format(university_year, university_rankings) for university_rankings in rankings_names]
    )

    for index, university_rankings in enumerate(Rankings):
        current_df = rankings_df[university_rankings.value]
        current_university = current_df[(current_df["University"] == university_name) & (current_df["Year"] == university_year)].squeeze()
        current_year_columns = rankings_year_columns[university_rankings.value][str(university_year)]
        current_year_columns = current_year_columns + [current_year_columns[0]]
        current_university.name = rankings_names[university_rankings.value]
        fig.add_trace(
            go.Scatterpolar(
                r=current_university[current_year_columns],
                theta=current_year_columns,
                name=rankings_names[university_rankings.value],
                hovertemplate="<b>%{theta}</b>: %{r}<extra></extra>",
                marker=dict(color=px.colors.qualitative.Plotly[0])
            ),
            row=1,
            col=index+1
        )

    fig.update_annotations(yshift=20)
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True)
    fig.update_layout(showlegend=False)
    fig.update_traces(fill='toself')
    
    return fig


radar_fig = load_university_radar_chart(current_university_name, current_university_year)

# initialize application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

university_table = dash_table.DataTable(
    style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
    },
    id='university-table',
    data=rankings_df[current_main_rankings.value][rankings_df[current_main_rankings.value]['Year'] == current_main_year].reset_index(drop=True).to_dict('records'),
    columns=[{"name": name, "id": name} for name in [current_main_criterion, "University", 'Country', '']],
    sort_action='native',
    filter_action='native',
    filter_options={"case": "insensitive"},
    row_selectable='multi',
    page_size=5,
    style_cell_conditional=[
        {
            'if': {'column_id': ''},
            'width': '10px',
        },
        {
            'if': {'column_id': current_main_criterion},
            'width': '20px',
        },
    ],
)

# HTML for Main Dashboard
main = html.Div([
    # html.H1('University Rankings Dashboard'),

    html.Div([
        html.Button('Times Higher Education Rankings',
                    id='btn-times-main', className='btn btn-secondary mx-3'),
        html.Button('Academic Ranking of World Universities',
                    id='btn-shanghai-main', className='btn btn-secondary mx-3'),
        html.Button('Center for World University Rankings',
                    id='btn-cwur-main', className='btn btn-secondary mx-3'),
    ], className='py-3 d-flex justify-content-center'),

    html.Div([
        dcc.Slider(
            min=2012,
            max=2022,
            step=1,
            value=2022,
            marks={i: '{}'.format(i) for i in range(2012, 2023)},
            id='main-slider'
        ),
    ]),

    html.Div([
        html.Div(
            children = [
                dcc.Tabs(id="tab-graphs", value='criteria-comparison-tab', children=[
                    dcc.Tab(
                        label='Trends', 
                        value='trends-tab',
                        children=[dcc.Graph(id='main-line-chart')]),
                    dcc.Tab(
                        label='Criteria Comparsion', value='criteria-comparison-tab',
                        children=[
                            dcc.Graph(id='main-bar-chart'),
                        ]
                    ),
                ]),
            ], 
            id="tab-container", 
            style={'width' : '70%'},
        ),

        html.Div(
           children= [
                dcc.Graph(id='choropleth_map', figure = choropleth_mapbox, config={'displayModeBar': False}, animate = False),
                html.Div([
                    html.Div(children=[html.H5("Criteria:")], className="col-2"),
                    html.Div(
                        children = [
                            dcc.Dropdown(
                                ['World Rank', 'Overall Score'] + rankings_year_columns[current_main_rankings.value][str(current_main_year)],
                                (['World Rank', 'Overall Score'] + rankings_year_columns[current_main_rankings.value][str(current_main_year)])[0],
                                placeholder='Select a Criteria',
                                clearable=False,
                                id='criteria-dropdown',
                            ),
                        ],
                        className="col-10"
                    ),
                ], className="row"),
                university_table,
            ], 
        ),
    ], className='d-flex flex-row'),

], className='container')

# HTML for University Page
modal_body = html.Div([

    html.H5('Main Dashboard', id='university-name-title'),

    html.Div([
        html.Button(children='Times Higher Education Rankings',
                    id='btn-times-university', 
                    className='btn btn-secondary mx-3'),
        html.Button(children='Academic Ranking of World Universities',
                    id='btn-shanghai-university', 
                    className='btn btn-secondary mx-3'),
        html.Button(children='Center for World University Rankings',
                    id='btn-cwur-university', 
                    className='btn btn-secondary mx-3'),
    ], className='py-3 d-flex justify-content-center'),

    html.Div([
        html.Div([dcc.Graph(id='university-line-chart', figure=university_trend_fig)], className='col-12'),
    ], className='row'),

    html.Div([
        dcc.Slider(
            min=2012,
            max=2022,
            step=1,
            value=2022,
            marks={i: '{}'.format(i) for i in range(2012, 2023)},
            id='university-year-slider'
        ),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='university-radar-chart', figure=radar_fig)], className='col-12'),
    ], className='row'),
], className='container')

app.layout = dbc.Container([
    main,
    html.Div([
        dbc.Modal(
            [
                dbc.ModalHeader(),
                dbc.ModalBody(modal_body),
            ],
            id="university-modal",
            fullscreen=True,
            is_open=False,
        ),
    ])
])

# Callback for Main Dashboard
# Tables


@ app.callback(
    Output(component_id="criteria-dropdown", component_property="options"),
    Output(component_id="main-bar-chart", component_property="figure"),
    Output(component_id="main-line-chart", component_property="figure"),
    Output(component_id="choropleth_map", component_property="figure"),
    Output(component_id="university-table", component_property="data"),
    Output(component_id="university-table", component_property="columns"),
    Output(component_id='university-table', component_property="selected_rows"),
    Output(component_id="university-table", component_property="filter_query"),
    Output(component_id="university-table", component_property="style_cell_conditional"),
    Output(component_id="choropleth_map", component_property="clickData"),
    Output(component_id="btn-times-main", component_property="className"),
    Output(component_id="btn-shanghai-main", component_property="className"),
    Output(component_id="btn-cwur-main", component_property="className"),
    Input(component_id="btn-times-main", component_property="n_clicks"),
    Input(component_id="btn-shanghai-main", component_property="n_clicks"),
    Input(component_id="btn-cwur-main", component_property="n_clicks"),
    Input(component_id="main-slider", component_property="value"),
    Input(component_id="criteria-dropdown", component_property="value"),
    Input(component_id='university-table', component_property="derived_virtual_data"),
    Input(component_id='university-table', component_property="derived_virtual_selected_rows"),
    Input(component_id="university-table", component_property="filter_query"),
    Input(component_id="tab-graphs", component_property="value"),
    Input(component_id="choropleth_map", component_property="clickData")
)
def update_main_dashboard(btn_times, btn_shanghai, btn_cwur, slider_value, dropdown_value, rows, selected_rows, filter_query, tab_value, selected_map):
    # Slider and Dropdown Data
    global current_main_year
    global current_main_criterion
    global current_main_rankings
    global current_main_university_list
    global btn_main_times_class
    global btn_main_shanghai_class
    global btn_main_cwur_class


    current_main_year = slider_value
    current_main_criterion = dropdown_value

    # Buttons Data
    button_rankings = Rankings.times
    if "btn-times-main" == ctx.triggered_id:
        current_main_rankings = Rankings.times
        btn_main_times_class = activated_class
        btn_main_shanghai_class = deactivated_class
        btn_main_cwur_class = deactivated_class
    elif "btn-shanghai-main" == ctx.triggered_id:
        current_main_rankings = Rankings.shanghai
        btn_main_times_class = deactivated_class
        btn_main_shanghai_class = activated_class
        btn_main_cwur_class = deactivated_class
    elif "btn-cwur-main" == ctx.triggered_id:
        current_main_rankings = Rankings.cwur
        btn_main_times_class = deactivated_class
        btn_main_shanghai_class = deactivated_class
        btn_main_cwur_class = activated_class
 
    # Dropdown Data
    options = ['World Rank', 'Overall Score'] + rankings_year_columns[current_main_rankings.value][str(current_main_year)]

    if current_main_criterion not in options:
        current_main_criterion = "World Rank"

    # Tables Data
    # load new df based on selected rankings and year
    df = rankings_df[current_main_rankings.value][rankings_df[current_main_rankings.value]['Year'] == current_main_year].reset_index(drop=True)
    df[''] = 'ⓘ'
    data = df.to_dict('records')
    columns=[{"name": name, "id": name} for name in [current_main_criterion, "University", 'Country', '']]

    if filter_query is None:
        filter_query = ''
    
    # print('filter_query', filter_query)

    if selected_rows is None:
        selected_rows = []
    # update the index of the currently selected universities
    # print("rows", rows)

    university_names = [] if rows is None else pd.DataFrame(rows)
    university_names = university_names if len(university_names) == 0 else university_names.iloc[selected_rows]['University']  # currently selected universities
    selected_index = df[df["University"].isin(university_names)].index.tolist()  # update the index

     # update the university list based on the new data and index
    current_main_university_list = pd.DataFrame() if rows is None else pd.DataFrame(data).iloc[selected_index]
    
    choropleth_mapbox = load_choropleth_map(current_main_rankings, current_main_year)
    
    style_cell_conditional=[
        {
            'if': {'column_id': ''},
            'width': '10px',
        },
        {
            'if': {'column_id': current_main_criterion},
            'width': '20px',
        },
    ]

    print('selected_map', selected_map)
    if selected_map is not None:
        country = selected_map['points'][0]['location']
        # print('country', country)
        if '{Country}' in filter_query: #{Country} exists
            filter_split = filter_query.split(' && ')
            for i in range(len(filter_split)):
                if '{Country}' in filter_split[i]: #replace {Country}
                    filter_split[i] = '{Country} ="' + country + '"'
            filter_query = ' && '.join(filter_split)
        else:
            if filter_query == '':
                filter_query = '{Country} ="' + country + '"'
            else:
                filter_query = filter_query + ' && {Country} ="' + country + '"'

    return (
        options,
        load_main_bar_chart(current_main_university_list, current_main_rankings, current_main_year),
        load_main_line_chart(current_main_university_list, current_main_rankings, current_main_criterion),
        choropleth_mapbox,
        data,
        columns,
        selected_index,
        filter_query,
        style_cell_conditional,
        None,
        btn_main_times_class,
        btn_main_shanghai_class,
        btn_main_cwur_class,
    )

@ app.callback(
    Output("university-modal", "is_open"),
    Output("university-name-title", "children"),
    Output('university-table', 'selected_cells'),
    Output('university-table', 'active_cell'),
    Output(component_id="university-line-chart", component_property="figure"),
    Output(component_id="university-radar-chart", component_property="figure"),
    Output(component_id="btn-times-university", component_property="className"),
    Output(component_id="btn-shanghai-university", component_property="className"),
    Output(component_id="btn-cwur-university", component_property="className"),
    Input('university-table', 'active_cell'),
    Input(component_id='university-table', component_property="derived_viewport_data"),
    Input("university-modal", "is_open"),
    Input(component_id="btn-times-university", component_property="n_clicks"),
    Input(component_id="btn-shanghai-university", component_property="n_clicks"),
    Input(component_id="btn-cwur-university", component_property="n_clicks"),
    Input(component_id="university-year-slider", component_property="value")
)
def open_university_overview(active_cell, rows, is_open, btn_times, btn_shanghai, btn_cwur, year_slider):

    global current_university_name
    global current_university_rankings
    global current_university_year
    global btn_univ_times_class
    global btn_univ_shanghai_class
    global btn_univ_cwur_class

    if active_cell:
        is_open = not is_open
        current_university_name = rows[active_cell['row']]['University']

    if "btn-times-university" == ctx.triggered_id:
        current_university_rankings = Rankings.times
        btn_univ_times_class = activated_class
        btn_univ_shanghai_class = deactivated_class
        btn_univ_cwur_class = deactivated_class
    elif "btn-shanghai-university" == ctx.triggered_id:
        current_university_rankings = Rankings.shanghai
        btn_univ_times_class = deactivated_class
        btn_univ_shanghai_class = activated_class
        btn_univ_cwur_class = deactivated_class
    elif "btn-cwur-university" == ctx.triggered_id:
        current_university_rankings = Rankings.cwur
        btn_univ_times_class = deactivated_class
        btn_univ_shanghai_class = deactivated_class
        btn_univ_cwur_class = activated_class

    current_university_year = year_slider

    return (
        is_open,
        current_university_name,
        [],
        None,
        load_university_line_chart(current_university_rankings, current_university_name),
        load_university_radar_chart(current_university_name, current_university_year),
        btn_univ_times_class,
        btn_univ_shanghai_class,
        btn_univ_cwur_class
    )

if __name__ == '__main__':
    app.run_server(debug=True)  # run server
