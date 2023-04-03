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

rank_columns = ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'patents', 'broad_impact', 'research_output']
for column in rank_columns:
    if column in cwur_df[cwur_df['year'] == 2012].columns:
        column_min = cwur_2012_df[column].min()
        column_max = cwur_2012_df[column].max()
        cwur_2012_df[column] = (column_max - cwur_2012_df[column]) / (column_max - column_min) * 100
        
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
times_bar_data = times_df[['university_name', 'teaching', 'international', 'research', 'citations', 'income']]
times_bar_x = 'university_name'
times_bar_y = ['teaching','international']
times_bar_fig = px.bar(times_bar_data[0:5], x=times_bar_y, y=times_bar_x, barmode='group', labels=times_columns)
times_bar_fig.update_layout(yaxis=dict(autorange="reversed"))
times_bar_fig.update_layout(dict(template="plotly_white"))
times_bar_fig.update_layout(title="Times Ranking Top 5 Universities", xaxis_title="Score", yaxis_title="University Name")


# University Page
#Selected University
times_university = times_df.loc[0] #TODO: update these
cwur_university = cwur_2012_df.loc[0] 
shanghai_university = shanghai_df.loc[0]

#Radar Charts
times_radar_fig = px.line_polar(times_university, r=times_university[times_columns], theta=times_columns, line_close=True)
times_radar_fig.update_traces(fill='toself')
# times_fig.update_layout(title={'text': "2012 Times Higher Education World University Rankings", 'x': 0.5})
times_radar_fig.update_layout(
    font=dict(size=18), 
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=True
)

cwur_radar_fig = px.line_polar(cwur_university, r=cwur_university[cwur_columns['2012']], theta=cwur_columns['2012'], line_close=True)
cwur_radar_fig.update_traces(fill='toself')
# cwur_fig.update_layout(title={'text': "2012 Center for World University Rankings", 'x': 0.5})
cwur_radar_fig.update_layout(
    font=dict(size=18), 
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=True
)

shanghai_radar_fig = px.line_polar(shanghai_university, r=shanghai_university[shanghai_columns], theta=shanghai_columns, line_close=True)
shanghai_radar_fig.update_traces(fill='toself')
# shanghai_fig.update_layout(title={'text': "2012 Academic Ranking of World Universities", 'x': 0.5})
shanghai_radar_fig.update_layout(
    font=dict(size=18), 
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=True
)

# Aaron University Specific
times_df["world_rank"] = times_df["world_rank"].str.removeprefix("=")
year = 2023
t_head_df = times_df[times_df["year"] == year].head(10)
criteria = ["World_Rank", "Total_Score", "Teaching", "International", "Research", "Citations", "Income"]
specific_fig = make_subplots(rows=4, cols=2, subplot_titles=criteria)
x_count = 1
y_count = 1
univ_name = "Harvard University"
temp = times_df[times_df["university_name"] == univ_name].sort_values(by=["year"], ascending=True)

for criterion in criteria:            
    temp_year = temp["year"].values.tolist()
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
s_head_df = shanghai_df[shanghai_df["year"] == year].head(5)

top5_fig = make_subplots(rows=5, cols=1, subplot_titles=s_head_df["university_name"].values.tolist())

x_count = 1
y_count = 1

for idx in s_head_df.index:        
    univ_name = s_head_df["university_name"][idx]
    temp = shanghai_df[shanghai_df["university_name"] == univ_name].sort_values(by=["year"], ascending=True)
    temp_year = temp["year"].values.tolist()
    temp_criteria = temp["total_score"].values.tolist()
    
    top5_fig.add_trace(go.Scatter(x=temp_year, y=temp_criteria, name=univ_name, mode='lines', line=dict(color="#EF553B")), row=x_count, col=1)
    
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
            columns = [{"name": i, "id": i} for i in ['world_rank', 'university_name', 'country']],
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

if __name__ == '__main__':
    app.run_server(debug=True) #run server