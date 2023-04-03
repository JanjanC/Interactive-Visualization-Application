import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date

times_df = pd.read_csv('datasets/times_2011_2023.csv')
times_columns = ['teaching', 'international', 'research', 'citations', 'income']

shanghai_df = pd.read_csv('datasets/shanghai_2012_2022.csv')
shanghai_columns = ['alumni', 'award', 'hici', 'ns', 'pub', 'pcp']

cwur_df = pd.read_csv('datasets/cwur_2012_2022.csv')

cwur_2012_df = cwur_df[cwur_df['year'] == 2012]
cwur_2012_columns = ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'patents']

rank_columns = ['quality_of_education', 'alumni_employment', 'quality_of_faculty', 'publications', 'influence', 'citations', 'patents', 'broad_impact', 'research_output']
for column in rank_columns:
    if column in cwur_df[cwur_df['year'] == 2012].columns:
        column_min = cwur_2012_df[column].min()
        column_max = cwur_2012_df[column].max()
        cwur_2012_df[column] = (column_max - cwur_2012_df[column]) / (column_max - column_min) * 100

#Main Dashboard
#TODO: load your dashboards here



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

cwur_radar_fig = px.line_polar(cwur_university, r=cwur_university[cwur_2012_columns], theta=cwur_2012_columns, line_close=True)
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

#initialize application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([ #we can access html components through html.xxx
    html.H1('Main Dashboard'), #automatically placed inside the HTML body
    
    html.Div([
        html.Button('Times Higher Education Rankings', id='btn-times-home'),
        html.Button('Academic Ranking of World Universities', id='btn-shanghai-home'),
        html.Button('Center for World University Rankings', id='btn-cwur-home'),
    ]),

    html.H1('University Home Page'),

    html.Div([
        html.Button('Times Higher Education Rankings', id='btn-times-university'),
        html.Button('Academic Ranking of World Universities', id='btn-shanghai-university'),
        html.Button('Center for World University Rankings', id='btn-cwur-university'),
    ]),

    html.Div([
        html.Div([dcc.Graph(id='radar-times', figure=times_radar_fig)], className='col-4'),
        html.Div([dcc.Graph(id='radar-shanghai', figure=shanghai_radar_fig)], className='col-4'),
        html.Div([dcc.Graph(id='radaw-cwur', figure=cwur_radar_fig)], className='col-4')
    ], className='row'),

    html.Div([
        html.Div([dcc.Graph(id='specific-times', figure=specific_fig)], className='col-12'),        
    ], className='row'),
])

if __name__ == '__main__':
    app.run_server(debug=True) #run server