import math
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, dash_table, Input, Output, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import enum
import requests

times_df = pd.read_csv('datasets/times_2011_2023.csv')
times_complete_columns = ['Teaching', 'International', 'Research', 'Citations', 'Income']
times_year_columns = {'{}'.format(i): times_complete_columns for i in range(2011, 2024)}

shanghai_df = pd.read_csv('datasets/shanghai_2012_2022.csv')
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
rankings_names = ['Times Higher Education World Rankings', 'Academic Ranking of World Universities', 'Center for World University Rankings']
rankings_complete_columns = [times_complete_columns, shanghai_complete_columns, cwur_complete_columns]
rankings_year_columns = [times_year_columns, shanghai_year_columns, cwur_year_columns]

cont = requests.get(
    "https://gist.githubusercontent.com/hrbrmstr/91ea5cc9474286c72838/raw/59421ff9b268ff0929b051ddafafbeb94a4c1910/continents.json"
)
gdf = gpd.GeoDataFrame.from_features(cont.json())

countries = gpd.read_file("datasets/world_countries.json")
countries_csv = gpd.read_file("datasets/countries.csv")
school = pd.read_csv("datasets/school_and_country_table.csv")

countries_csv = countries_csv.drop(['geometry', 'country', 'latitude', 'longitude'], axis = 1)
countries = countries.join(countries_csv.set_index('name'), on = 'name', how = 'left')
school.join(countries.set_index('name'), on = 'country', how = 'left')
school.join(countries.set_index('name'), on = 'country', how = 'left')
school.groupby('country').count()
school_count = school.groupby('country').count()
countries = countries.join(school_count, on = 'name', how = "left")
countries.rename(columns = {'school_name':'school_count'}, inplace = True)


#Main Dashboard
#Chloropleth Map
def load_choropleth_map():
    choropleth_fig = px.choropleth(countries, locations = countries['name'], labels = countries['name'], locationmode = "country names", scope = "world", color = countries['school_count'], geojson = gdf, color_continuous_scale = ['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c'])
    return choropleth_fig

choropleth_fig = load_choropleth_map()

# Bar Chart (Criteria Comparision)
current_main_rankings = Rankings.times
current_main_university_list = pd.DataFrame() 
current_main_criterion = "Overall Score"
current_main_year = 2012

def load_main_bar_chart(university_list, university_rankings, main_year):
    if not university_list.empty:
        criteria = ["University"] + rankings_complete_columns[current_main_rankings.value]
        current_df = university_list[criteria]
        fig = px.bar(current_df, x=criteria, y="University", barmode='group', labels=criteria)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig.update_layout(dict(template="plotly_white"))
        fig.update_layout(title="Comparsion of the Selected Universities Based on the Selected Criteria in the {} {}".format(main_year, rankings_names[university_rankings.value]), xaxis_title="Score", yaxis_title="University Name")
    else:
        fig=px.bar().add_annotation(text="Select a University from the Table", showarrow=False, font={"size":20})

    return fig

main_trend_fig = load_main_bar_chart(current_main_university_list, current_main_rankings, current_main_year)

# Line Chart(Trend)
def load_main_line_chart(university_list, university_rankings, criterion):
    if not university_list.empty:
        fig = make_subplots(rows=len(university_list), cols=1, subplot_titles=university_list["University"].values.tolist())

        for index, university_name in enumerate(university_list["University"]):
            current_df = rankings_df[university_rankings.value]
            university_df = current_df[current_df["University"] == university_name].sort_values(by=["Year"], ascending=True)
            year_list = university_df["Year"].values.tolist()
            criteria_list = university_df[criterion].values.tolist()
            
            fig.add_trace(go.Scatter(x=year_list, y=criteria_list, name=university_name, mode='lines', line=dict(color="#EF553B")), row=index+1, col=1)

        fig.update_layout(showlegend=False)
        fig.update_layout(height=700, width=1200, title_text="{} Trend in the {}".format(criterion, rankings_names[university_rankings.value]))    
        return fig
    else:
        fig=px.bar().add_annotation(text="Select a University from the Table", showarrow=False, font={"size":20})
        return fig

main_line_fig = load_main_line_chart(current_main_university_list, current_main_rankings, current_main_criterion)

# University Page
#Selected University
current_university_rankings = Rankings.times
current_university_name = "Harvard University"
current_university_year = 2012

# Line Charts
def load_university_line_chart(university_rankings, university_name):
    current_df = rankings_df[university_rankings.value]
    criteria = ["World Rank", "Overall Score"] + rankings_complete_columns[university_rankings.value]
    fig = make_subplots(rows=math.ceil(len(criteria) / 2), cols=2, subplot_titles=criteria)
    current_df = current_df[current_df["University"] == university_name].sort_values(by=["Year"], ascending=True)
    for index, criterion in enumerate(criteria):
        year_list = current_df["Year"].values.tolist()

        if criterion == "World Rank":
            criteria_list = current_df["World Rank Order"].values.tolist()
            #TODO: change hover data
        else:
            criteria_list = current_df[criterion].values.tolist()
        
        fig.add_trace(go.Scatter(x=year_list, y=criteria_list, name=criterion, mode='lines'), row = index // 2 + 1, col = index % 2 + 1)

    fig.update_yaxes(autorange="reversed", row=1, col=1)

    fig.update_layout(height=600, width=1200, title_text="Times Ranking of Harvard University")
    return fig

university_trend_fig = load_university_line_chart(current_university_rankings, current_university_name)

#Radar Charts
def load_university_radar_chart(university_name, university_year):
    figs = []
    for university_rankings in Rankings:
        current_df = rankings_df[university_rankings.value]
        current_university = current_df[(current_df["University"] == university_name) & (current_df["Year"] == university_year)].squeeze()
        current_year_columns = rankings_year_columns[university_rankings.value][str(university_year)]
        current_university.name = "Center for World University Rankings"
        fig = px.line_polar(current_university, r=current_university[current_year_columns], theta=current_year_columns, line_close=True)
        fig.update_traces(fill='toself')
        fig.update_layout(
            font=dict(size=18), 
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True
        )
        figs.append(fig)

    return tuple(figs)

times_radar_fig, cwur_radar_fig, shanghai_radar_fig = load_university_radar_chart(current_university_name, current_university_year)

#initialize application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#HTML for Main Dashboard
main = html.Div([
    html.H1('Main Dashboard'), #automatically placed inside the HTML body
    
    html.Div([
        html.Div([dcc.Graph(id='choropleth_map', figure=choropleth_fig)], className='col-4'),
    ], className='row'),
    
    html.Div([
        html.Button('Times Higher Education Rankings', id='btn-times-main'),
        html.Button('Academic Ranking of World Universities', id='btn-shanghai-main'),
        html.Button('Center for World University Rankings', id='btn-cwur-main'),
    ]),

    html.Div([
        dcc.Slider(
            min=2012, 
            max=2022,
            step=1,
            value=2012,
            marks={i: '{}'.format(i) for i in range(2012, 2023)},
            id='main-slider'
        ),
    ]),

    html.Div([
        dcc.Dropdown(
            ['World Rank', 'Overall Score'] + rankings_year_columns[current_main_rankings.value][str(current_main_year)], 
            (['World Rank', 'Overall Score'] + rankings_year_columns[current_main_rankings.value][str(current_main_year)])[0],
            placeholder='Select a Criteria',
            clearable=False,
            id='criteria-dropdown',
        ),

        dash_table.DataTable(
            id='university-table',
            data = rankings_df[current_main_rankings.value][rankings_df[current_main_rankings.value]['Year'] == current_main_year].to_dict('records'), 
            columns = [{"name": i, "id": i} for i in [current_main_criterion, "University", 'Country']],
            sort_action='native',
            filter_action='native',
            row_selectable='multi',
            cell_selectable=False,
            page_size=10
        )
    ]),

    html.Div([
        dcc.Tabs(id="tab-graphs", value='criteria-comparison-tab', children=[
            dcc.Tab(label='Criteria Comparsion', value='criteria-comparison-tab', children=[dcc.Graph(id='main-bar-chart', figure=main_trend_fig)]),
            dcc.Tab(label='Trends', value='trends-tab', children=[dcc.Graph(id='main-line-chart', figure=main_line_fig)]),
        ]),
    ])
])

#HTML for University Page
modal =  html.Div([
    html.H1('University Home Page'),

    html.Div([
        html.Button('Times Higher Education Rankings', id='btn-times-university'),
        html.Button('Academic Ranking of World Universities', id='btn-shanghai-university'),
        html.Button('Center for World University Rankings', id='btn-cwur-university'),
    ]),

    html.Div([
        dcc.Slider(
            min=2012, 
            max=2022,
            step=1,
            value=2012,
            marks={i: '{}'.format(i) for i in range(2012, 2023)},
            id='university-slider'
        ),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='university-line-chart', figure=university_trend_fig)], className='col-12'),        
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='radar-times', figure=times_radar_fig)], className='col-4'),
        html.Div([dcc.Graph(id='radar-shanghai', figure=shanghai_radar_fig)], className='col-4'),
        html.Div([dcc.Graph(id='radaw-cwur', figure=cwur_radar_fig)], className='col-4')
    ], className='row'),   
])

app.layout = dbc.Container([
    main,
    modal
])

#Callback for Main Dashboard
#Tables
@app.callback(
    Output(component_id="criteria-dropdown", component_property="options"),
    Output(component_id="main-bar-chart", component_property="figure"),
    Output(component_id="main-line-chart", component_property="figure"),
    Output(component_id="university-table", component_property="data"),
    Output(component_id="university-table", component_property="columns"),
    Input(component_id="btn-times-main", component_property="n_clicks"),
    Input(component_id="btn-shanghai-main", component_property="n_clicks"),
    Input(component_id="btn-cwur-main", component_property="n_clicks"),
    Input(component_id="main-slider", component_property="value"),
    Input(component_id="criteria-dropdown", component_property="value"),
    Input(component_id='university-table', component_property="derived_virtual_data"),
    Input(component_id='university-table', component_property="derived_virtual_selected_rows")
)
def update_main(btn_times, btn_shanghai, btn_cwur, slider_value, dropdown_value, rows, selected_rows):
    #Slider and Dropdown Data
    global current_main_year
    global current_main_criterion
    global current_main_rankings

    current_main_year = slider_value
    current_main_criterion = dropdown_value

    # Buttons Data
    button_rankings = Rankings.times
    if "btn-times-main" == ctx.triggered_id:
        current_main_rankings = Rankings.times
    elif "btn-shanghai-main" == ctx.triggered_id:
        current_main_rankings = Rankings.shanghai
    elif "btn-cwur-main" == ctx.triggered_id:
        current_main_rankings = Rankings.cwur

    print(current_main_rankings)
    options = ['World Rank', 'Overall Score'] + rankings_year_columns[current_main_rankings.value][str(current_main_year)]

    if current_main_criterion not in options:
        current_main_criterion = "World Rank"

    # Tables Data
    if selected_rows is None:
        selected_rows = []
    
    current_main_university_list = pd.DataFrame() if rows is None else pd.DataFrame(rows).iloc[selected_rows]
    
    data = rankings_df[current_main_rankings.value][rankings_df[current_main_rankings.value]['Year'] == current_main_year].to_dict('records')
    columns = [{"name": i, "id": i} for i in [current_main_criterion, "University", 'Country']]

    return (
        options,
        load_main_bar_chart(current_main_university_list, current_main_rankings, current_main_year), 
        load_main_line_chart(current_main_university_list, current_main_rankings, current_main_criterion), 
        data,
        columns
    )

#Rankings Buttons
# @app.callback(
#     Output(component_id="main-line-chart", component_property="figure"),
#     Input(component_id="btn-times-main", component_property="n_clicks"),
#     Input(component_id="btn-shanghai-main", component_property="n_clicks"),
#     Input(component_id="btn-cwur-main", component_property="n_clicks"),
# )
# def select_ranking(btn_times, btn_shanghai, btn_cwur):
#     if "btn-times-university" == ctx.triggered_id:
#         current_university_rankings = Rankings.times
#     elif "btn-shanghai-university" == ctx.triggered_id:
#         current_university_rankings = Rankings.shanghai
#     elif "btn-cwur-university" == ctx.triggered_id:
#         current_university_rankings = Rankings.cwur
#     else:
#         current_university_rankings = Rankings.times

#     return load_main_line_chart(current_main_university_list, "Overall Score")

#Callback for University Overview Page
#Rankings Buttons
@app.callback(
    Output(component_id="university-line-chart", component_property="figure"),
    Input(component_id="btn-times-university", component_property="n_clicks"),
    Input(component_id="btn-shanghai-university", component_property="n_clicks"),
    Input(component_id="btn-cwur-university", component_property="n_clicks"),
)
def select_ranking(btn_times, btn_shanghai, btn_cwur):
    global current_university_rankings
    if "btn-times-university" == ctx.triggered_id:
        current_university_rankings = Rankings.times
    elif "btn-shanghai-university" == ctx.triggered_id:
        current_university_rankings = Rankings.shanghai
    elif "btn-cwur-university" == ctx.triggered_id:
        current_university_rankings = Rankings.cwur
    else:
        current_university_rankings = Rankings.times

    return load_university_line_chart(current_university_rankings, current_university_name)

#Year Sliders
@app.callback(
    Output(component_id="radar-times", component_property="figure"),
    Output(component_id="radar-shanghai", component_property="figure"),
    Output(component_id="radaw-cwur", component_property="figure"),
    Input(component_id="university-slider", component_property="value")
)
def update_radar(slider_value):
    global current_university_year
    current_university_year = slider_value
    return load_university_radar_chart(current_university_name, current_university_year)

if __name__ == '__main__':
    app.run_server(debug=True) #run server