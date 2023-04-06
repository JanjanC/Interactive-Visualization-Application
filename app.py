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

def load_main_bar_chart(university_list):
    if not university_list.empty:
        criteria = ["University"] + rankings_complete_columns[current_main_rankings.value]
        current_df = university_list[criteria]
        fig = px.bar(current_df, x=criteria, y="University", barmode='group', labels=criteria)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        fig.update_layout(dict(template="plotly_white"))
        fig.update_layout(title="Times Ranking Top 5 Universities", xaxis_title="Score", yaxis_title="University Name")
    else:
        fig=px.bar().add_annotation(text="Select a University from the Table", showarrow=False, font={"size":20})

    return fig

main_trend_fig = load_main_bar_chart(current_main_university_list)

#Line Chart(Trend)
def load_main_line_chart():
    year = 2022
    s_head_df = shanghai_df[shanghai_df["Year"] == year].head(5)

    top5_fig = make_subplots(rows=5, cols=1, subplot_titles=s_head_df["University"].values.tolist())

    x_count = 1
    y_count = 1

    for idx in s_head_df.index:        
        university_name = s_head_df["University"][idx]
        temp = shanghai_df[shanghai_df["University"] == university_name].sort_values(by=["Year"], ascending=True)
        temp_year = temp["Year"].values.tolist()
        temp_criteria = temp["Overall Score"].values.tolist()
        
        top5_fig.add_trace(go.Scatter(x=temp_year, y=temp_criteria, name=university_name, mode='lines', line=dict(color="#EF553B")), row=x_count, col=1)
        
        x_count += 1

    top5_fig.update_yaxes(range=[0, 100])
    top5_fig.update_layout(showlegend=False)
    top5_fig.update_layout(height=700, width=1200, title_text="Shanghai Ranking of Top 5 Universities Score")    
    return top5_fig

top5_fig = load_main_line_chart()

#Table
university_table = dash_table.DataTable(
    id='university-table',
    data = times_df.to_dict('records'), 
    columns = [{"name": i, "id": i} for i in ['World Rank', "University", 'country']],
    sort_action='native',
    filter_action='native',
    row_selectable='multi',
    cell_selectable=False,
    page_size=10
)

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
        university_table
    ]),

    html.Div([
        dcc.Tabs(id="tab-graphs", value='criteria-comparison-tab', children=[
            dcc.Tab(label='Criteria Comparsion', value='criteria-comparison-tab', children=[dcc.Graph(id='main-bar-chart', figure=main_trend_fig)]),
            dcc.Tab(label='Trends', children=[dcc.Graph(id='trends-tab', figure=top5_fig)]),
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
    Output(component_id="main-bar-chart", component_property="figure"),
    Input(component_id='university-table', component_property="derived_virtual_data"),
    Input(component_id='university-table', component_property="derived_virtual_selected_rows")
)
def update_tabs(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    
    current_main_university_list = pd.DataFrame() if rows is None else pd.DataFrame(rows).iloc[derived_virtual_selected_rows]

    return load_main_bar_chart(current_main_university_list)

#Rankings Buttons
@app.callback(
    Output(component_id="main-line-chart", component_property="figure"),
    Input(component_id="btn-times-main", component_property="n_clicks"),
    Input(component_id="btn-shanghai-main", component_property="n_clicks"),
    Input(component_id="btn-cwur-main", component_property="n_clicks"),
)
def select_ranking(btn_times, btn_shanghai, btn_cwur):
    if "btn-times-university" == ctx.triggered_id:
        current_university_rankings = Rankings.times
    elif "btn-shanghai-university" == ctx.triggered_id:
        current_university_rankings = Rankings.shanghai
    elif "btn-cwur-university" == ctx.triggered_id:
        current_university_rankings = Rankings.cwur
    else:
        current_university_rankings = Rankings.times

    return load_main_line_chart()

#Callback for University Overview Page
#Rankings Buttons
@app.callback(
    Output(component_id="university-line-chart", component_property="figure"),
    Input(component_id="btn-times-university", component_property="n_clicks"),
    Input(component_id="btn-shanghai-university", component_property="n_clicks"),
    Input(component_id="btn-cwur-university", component_property="n_clicks"),
)
def select_ranking(btn_times, btn_shanghai, btn_cwur):
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
    current_university_year = slider_value
    return load_university_radar_chart(current_university_name, current_university_year)

if __name__ == '__main__':
    app.run_server(debug=True) #run server