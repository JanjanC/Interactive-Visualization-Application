import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
from datetime import date
import requests

times_df = pd.read_csv('datasets/times_2011_2023.csv')
times_columns = ['teaching', 'international', 'research', 'citations', 'income']

shanghai_df = pd.read_csv('datasets/shanghai_2012_2022.csv')
shanghai_columns = ['alumni', 'award', 'hici', 'ns', 'pub', 'pcp']

cwur_df = pd.read_csv('datasets/cwur_2012_2022.csv')

cwur_2012_df = cwur_df[cwur_df['year'] == 2012]
cwur_columns = {
    '2012': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'patents'],
    '2013': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'patents'],
    '2014': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'broad_impact', 'patents'],
    '2015': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'broad_impact', 'patents'],
    '2016': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'broad_impact', 'patents'],
    '2017': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'research_output'],
    '2018': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'research_performance'],
    '2019': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'research_performance'],
    '2020': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'research_performance'],
    '2021': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'research_performance'],
    '2022': ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'research_performance'],
} 

#preprocess ranks to score
rank_columns = ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'patents', 'broad_impact', 'research_output', 'research_performance']
cwur_years = []
for year in range(2012, 2023):
    cwur_year_df = cwur_df[cwur_df['year'] == year]
    for column in rank_columns:
        column_min = cwur_year_df[column].min()
        column_max = cwur_year_df[column].max()
        print(column, year, cwur_year_df.shape, column_min, column_max)
        cwur_year_df[column] = (column_max - cwur_year_df[column]) / (column_max - column_min) * 100
        print(cwur_year_df[column].min(), cwur_year_df[column].max())
        print(cwur_year_df.head())
        cwur_years.append(cwur_year_df)
cwur_df = pd.concat(cwur_years)

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
#TODO: load your dashboards here
choropleth_fig = px.choropleth(countries, locations = countries['name'], labels = countries['name'], locationmode = "country names", scope = "world", color = countries['school_count'], geojson = gdf, color_continuous_scale = ['#eff3ff','#bdd7e7','#6baed6','#3182bd','#08519c'])

# Bar Chart
times_bar_data = times_df[["University", 'teaching', 'international', 'research', 'citations', 'income']]
times_bar_x = "University"
times_bar_y = ['teaching','international']
times_bar_fig = px.bar(times_bar_data[0:5], x=times_bar_y, y=times_bar_x, barmode='group', labels=times_columns)
times_bar_fig.update_layout(yaxis=dict(autorange="reversed"))
times_bar_fig.update_layout(dict(template="plotly_white"))
times_bar_fig.update_layout(title="Times Ranking Top 5 Universities", xaxis_title="Score", yaxis_title="University Name")


# University Page
#Selected University
current_university_name = "Harvard University"
current_university_year = 2012

#radar Charts
def load_university_radar(university_name, university_year):
    times_university = times_df[(times_df["University"] == university_name) & (times_df["Year"] == university_year)].squeeze()
    times_university.name = "Times Higher Education World Rankings"
    times_fig = px.line_polar(times_university, r=times_university[times_columns], theta=times_columns, line_close=True)
    times_fig.update_traces(fill='toself')
    times_fig.update_layout(
        font=dict(size=18), 
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True
    )

    cwur_university = cwur_df[(cwur_df["University"] == university_name) & (cwur_df["Year"] == university_year)].squeeze()
    cwur_university.name = "Center for World University Rankings"
    cwur_fig = px.line_polar(cwur_university, r=cwur_university[cwur_columns[str(university_year)]], theta=cwur_columns[str(university_year)], line_close=True)
    cwur_fig.update_traces(fill='toself')
    cwur_fig.update_layout(
        font=dict(size=18), 
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True
    )

    shanghai_university = shanghai_df[(shanghai_df["University"] == university_name) & (shanghai_df["Year"] == university_year)].squeeze()
    shanghai_university.name = "Academic Ranking of World Universities"
    shanghai_fig = px.line_polar(shanghai_university, r=shanghai_university[shanghai_columns], theta=shanghai_columns, line_close=True)
    shanghai_fig.update_traces(fill='toself')
    shanghai_fig.update_layout(
        font=dict(size=18), 
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True
    )

    return times_fig, cwur_fig, shanghai_fig

times_radar_fig, cwur_radar_fig, shanghai_radar_fig = load_university_radar(current_university_name, current_university_year)

# Aaron University Specific
times_df["world_rank"] = times_df["world_rank"].str.removeprefix("=")
year = 2023
t_head_df = times_df[times_df["Year"] == year].head(10)
criteria = ["World_Rank", "Total_Score", "Teaching", "International", "Research", "Citations", "Income"]
specific_fig = make_subplots(rows=4, cols=2, subplot_titles=criteria)
x_count = 1
y_count = 1
temp = times_df[times_df["University"] == current_university_name].sort_values(by=["Year"], ascending=True)

for criterion in criteria:            
    temp_year = temp["Year"].values.tolist()
    temp_criteria = temp[criterion.lower()].values.tolist()
    if criterion == "World_Rank":
        temp_criteria = [-int(x) for x in temp_criteria]
        specific_fig.update_yaxes(range=[0, 100])    
    specific_fig.add_trace(go.Scatter(x=temp_year, y=temp_criteria, name=criterion, mode='lines'), row=x_count, col=y_count)
    
    if y_count == 2:
        x_count += 1
        y_count = 1
    else:
        y_count += 1

specific_fig.update_yaxes(range=[-10, -1], row=1, col=1)
specific_fig.update_layout(height=600, width=1200, title_text="Times Ranking of Harvard University")    

# Aaron Top 5 Front
year = 2022
s_head_df = shanghai_df[shanghai_df["Year"] == year].head(5)

top5_fig = make_subplots(rows=5, cols=1, subplot_titles=s_head_df["University"].values.tolist())

x_count = 1
y_count = 1

for idx in s_head_df.index:        
    university_name = s_head_df["University"][idx]
    temp = shanghai_df[shanghai_df["University"] == university_name].sort_values(by=["Year"], ascending=True)
    temp_year = temp["Year"].values.tolist()
    temp_criteria = temp["total_score"].values.tolist()
    
    top5_fig.add_trace(go.Scatter(x=temp_year, y=temp_criteria, name=university_name, mode='lines', line=dict(color="#EF553B")), row=x_count, col=1)
    
    x_count += 1

top5_fig.update_yaxes(range=[0, 100])
top5_fig.update_layout(showlegend=False)
top5_fig.update_layout(height=700, width=1200, title_text="Shanghai Ranking of Top 5 Universities Score")    

#initialize application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([ #we can access html components through html.xxx
    html.H1('Main Dashboard'), #automatically placed inside the HTML body
    
    html.Div([
        html.Div([dcc.Graph(id='choropleth_map', figure=choropleth_fig)], className='col-4'),
    ], className='row'),
    
    html.Div([
        html.Button('Times Higher Education Rankings', id='btn-times-home'),
        html.Button('Academic Ranking of World Universities', id='btn-shanghai-home'),
        html.Button('Center for World University Rankings', id='btn-cwur-home'),
    ]),

    html.Div([
        dcc.Slider(2011, 2023, 1,
               value=2012,
               id='main-slider'
        ),
    ]),

    html.Div([
        dash_table.DataTable(
            data = times_df.to_dict('records'), 
            columns = [{"name": i, "id": i} for i in ['world_rank', "University", 'country']],
            page_size=10
        )
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='bar-chart', figure=times_bar_fig)
        ])
    ]),

    html.Div([
        html.Div([dcc.Graph(id='top-shanghai', figure=top5_fig)], className='col-12'),        
    ], className='row'),

    html.H1('University Home Page'),

    html.Div([
        html.Button('Times Higher Education Rankings', id='btn-times-university'),
        html.Button('Academic Ranking of World Universities', id='btn-shanghai-university'),
        html.Button('Center for World University Rankings', id='btn-cwur-university'),
    ]),

    html.Div([
        dcc.Slider(2011, 2023, 1,
               value=2012,
               id='university-slider'
        ),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='specific-times', figure=specific_fig)], className='col-12'),        
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='radar-times', figure=times_radar_fig)], className='col-4'),
        html.Div([dcc.Graph(id='radar-shanghai', figure=shanghai_radar_fig)], className='col-4'),
        html.Div([dcc.Graph(id='radaw-cwur', figure=cwur_radar_fig)], className='col-4')
    ], className='row'),        
])

@app.callback(
    #input - dropdown, output - histogram
    Output(component_id="radar-times", component_property="figure"),\
    Output(component_id="radar-shanghai", component_property="figure"),
    Output(component_id="radaw-cwur", component_property="figure"),
    Input(component_id="university-slider", component_property="value")
)
def update_radar(slider_value):
    current_university_year = slider_value
    return load_university_radar(current_university_name, current_university_year)

if __name__ == '__main__':
    app.run_server(debug=True) #run server