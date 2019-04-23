import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import datetime as dt
import numpy as np 
import pandas as pd
import plotly.graph_objs as go

# ToDo
# design data structure? xarray?? need to access individual profiles
# user specified alias data? 
# line between dropdowns and filters
# average table via pd.describe 
# change profile plot to single yo?
# link hover on all axes
# linear/log functionaility


def matlab2datetime(matlab_datenum):
    day = dt.datetime.fromordinal(int(matlab_datenum))
    dayfrac = dt.timedelta(days=matlab_datenum%1) - dt.timedelta(days = 366)
    return day + dayfrac

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() #* 1000.0

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

mapbox_access_token = 'pk.eyJ1IjoiZmlvbmFlbGxpb3R0IiwiYSI6ImNqbjVxZDc4ejBiYWczcXBpbjJ4amw3angifQ.OYGcYmvD4feyhZ51wKvubw'

app = dash.Dash(external_stylesheets=external_stylesheets)
app.title = 'NIWA Glider Data Explorer'

# read in glider data
df = pd.read_csv(
    'betty_combineData.csv')
pd.set_option('precision',2)

# convert time to date_time
newtime = []
for index, row in df.iterrows():
    newtime.append(matlab2datetime(row[0]))
df['time'] = newtime 
df.set_index('time', inplace=True)

# for slider objects
epoch = dt.datetime.utcfromtimestamp(0)
timeMin = df.index[0]
timeMax = df.index[-1]
timeRange = pd.date_range(timeMin, timeMax, periods=10).to_pydatetime()
depthMin = int(np.floor(df['depth'].min() / 10) * 10)
depthMax = int(np.ceil(df['depth'].max() / 10) * 10)

glider_sensors = list(df.columns.values)

app.layout = html.Div([
    
        # HEADING
        html.Div([
            html.H1(
                children='Glider Data Explorer',
                className='nine columns',
                style={'margin': '0px'
                },
            ),
            html.Img(
                src = 'https://www.niwa.co.nz/sites/niwa.co.nz/files/niwa-2018-horizontal-final-400_0.png',
                className = 'one columns',
                style = {
                    'height': '14%',
                    'width': '14%',
                    'float': 'right',
                    'position': 'relative',
                    'margin-top': 1,
                    'margin-right': 1
                },
            ),
            html.H5(
                children="Explore data collected by NIWA's fleet of underwater gliders.", 
                className='nine columns',
                style={'margin': '0px'
                },
            )
        ], className='row',
        style={'margin-bottom': '15px'
        }
        ), # <--- HEADING

        # SELECT
        html.Div([
            html.Div([ 
                html.Div([
                    html.P(
                    children='select deployment:'
                    ),
                    dcc.Dropdown(
                        id='deployment-column',
                        options=[{'label': i, 'value': i} for i in ['001 Greater Cook Strait', '002 Greater Cook Strait', '003 North East Shelf', '004 Greater Cook Strait', '005 North East Shelf', '006 Greater Cook Strait', '007 North East Shelf', '008 Hawkes Bay', '009 Greater Cook Strait']],
                        value='001 Greater Cook Strait'
                    ),
                ],className='two columns'),

                # html.Div([   # SELECT param
                html.Div([
                    html.P(
                    children='first variable:'
                    ),
                    dcc.Dropdown(
                        id='first_variable',
                        options=[{'label': i, 'value': i} for i in glider_sensors],
                        value='temperature'
                    ),
                    dcc.RadioItems(
                        id='first_variable_type',
                        options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                        value='Linear',
                        labelStyle={'display': 'inline-block'}
                    )
                ],style={'margin-left': '7px'},
                className='two columns'),

                html.Div([
                    html.P(
                    children='second variable:'
                    ),
                    dcc.Dropdown(
                        id='second_variable',
                        options=[{'label': i, 'value': i} for i in glider_sensors],
                        value='salinity'
                    ),
                    dcc.RadioItems(
                        id='second_variable_type',
                        options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                        value='Linear',
                        labelStyle={'display': 'inline-block'}
                    )
                ],style={'margin-left': '7px'},
                 className='two columns'),

                html.Div([
                    html.P(
                    children='third variable:'
                    ),
                    dcc.Dropdown(
                        id='third_variable',
                        options=[{'label': i, 'value': i} for i in glider_sensors],
                        value='density'
                    ),
                    dcc.RadioItems(
                        id='third_variable_type',
                        options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                        value='Linear',
                        labelStyle={'display': 'inline-block'}
                    )
                ], className='two columns',
                style={'margin-left': '7px'}),


                # ],style={'display': 'inline-block', 'margin-top': '10px', 'margin-left': '0px'},
                # className='six columns'), # <-- SELECT PARAM 
            
                html.Div([
                    html.Button('Display', id='button')
                ], className='two columns',
                style={'margin-top': '30px', 'display': 'inline-block'}),


            ],className='twelve columns',
            style={'display': 'inline-block', 'margin-bottom': '12px'}), 

            html.Div([
                html.Div([
                    html.P('filter by depth (m):'), 
                    dcc.RangeSlider(
                        id='depth--slider',
                        min=depthMin, #df['dep'].min(),
                        max=depthMax, #df['dep'].max(),
                        value=[depthMin, depthMax], #[df['depth'].min(), df['depth'].max()],
                        marks={str(depth): str(depth) for depth in range(depthMin,depthMax,10)} #{str(depth): str(depth) for depth in range(int(np.floor(df['dep'].min() / 10) * 10),int(np.ceil(df['dep'].max() / 10) * 10+10),10)}
                    ),
                ], style={'display': 'inline-block', 'margin-bottom': '25px', 'margin-top': '8px', 'margin-right': '15px', 'margin-left': '5px', 'width': '48%'},
                ),

                html.Div([
                    html.P('filter by time:'),  # noqa: E501
                    dcc.RangeSlider(
                        id='time--slider',
                        min=unix_time_millis(timeMin),
                        max=unix_time_millis(timeMax),
                        value= [unix_time_millis(timeMin), unix_time_millis(timeMax)], #[timeMin, timeMax], #
                        marks={unix_time_millis(time): str(time.strftime('%b-%d')) for time in timeRange} 
                    ),
                ],style={'display': 'inline-block', 'margin-bottom': '25px', 'margin-top': '10px','margin-right': '5px', 'margin-left': '15px', 'width': '48%'}, 
                ), 

            ],style={'borderTop': 'thin lightgrey solid'}, 
            className='nine columns'), 

        ], style={'borderBottom': 'thin lightgrey solid',
        'borderTop': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '5px'},
        className='twelve columns'), # <-- SELECT

        # PLOTS
        html.Div([
            html.Div([
                dcc.Graph(
                    id='map-plot') 
                ],
                className='four columns'
            ),

            html.Div([
                # html.P('Single profile:'),  # noqa: E501
                dcc.Graph(id='variable-plot')
                ],
                className='four columns'
            ),

            html.Div([
                # html.P('Single profile:'),  # noqa: E501
                dcc.Graph(id='profile-plot')
                ],
                className='four columns'
            ),
        ],style={'margin-top': '30px'},
        className='twelve columns'),    

        html.Div([
            dcc.Graph(id='time-series-plot')
        ],
        style={'margin-top': '30px', 'margin-bottom': '30px', 'margin-left': '0px', 'margin-right': '0px'},
        className='twelve columns'
        ) # <-- PLOTS
])

# Time series plot callback
@app.callback(
    Output('time-series-plot', 'figure'),
    [Input('first_variable', 'value'),
     Input('first_variable_type', 'value'),
     Input('depth--slider', 'value'),
     Input('time--slider', 'value')])
def update_graph(color_column_name,
                 color_type,
                 depth_value,
                 time_value):

    # filter by date
    dff = df[((df.index > dt.datetime.fromtimestamp(time_value[0])) & (df.index <= dt.datetime.fromtimestamp(time_value[1])))]
    # filter by time
    dff = dff[(dff['depth'] >= depth_value[0]) & (dff['depth'] <= depth_value[1] )]

    return {
        'data': [go.Scatter(
            x=dff.index,
            y=dff['depth'],
            #text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            mode='markers',
            marker={
                'size': 10,
                'opacity': 0.5,
                # 'line': {'width': 0.5, 'color': 'white'}
                'color': dff[color_column_name], #set color equal to a variable
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar':{
                    'title':color_column_name}
            }
        )],
        'layout': go.Layout(
            title=color_column_name + ' time series',
            xaxis={
                'title': 'time',
                'range': [dff.index[0],dff.index[-1]]
            },
            yaxis={
                'title': 'depth (m)',
                'type': 'linear',
                'autorange': 'reversed'
            },
            margin={'l': 35, 'b': 30, 't': 25, 'r': 0},
            hovermode='closest'
        )
    }


    # xaxis = dict(
    #     range = ['2016-07-01','2016-12-31'])

# Mapbox plot callback
@app.callback(
    Output('map-plot', 'figure'),
    [Input('first_variable', 'value'),
     Input('first_variable_type', 'value'),
     Input('depth--slider', 'value'),
     Input('time--slider', 'value')])
def update_map(color_column_name,
                 color_type,
                 depth_value,
                 time_value):

    # filter by date
    dff = df[((df.index > dt.datetime.fromtimestamp(time_value[0])) & (df.index <= dt.datetime.fromtimestamp(time_value[1])))]
    # filter by time
    dff = dff[(dff['depth'] >= depth_value[0]) & (dff['depth'] <= depth_value[1] )]

    return {
        'data': [go.Scattermapbox(
                lat=dff['latitude'],
                lon=dff['longitude'],
                mode='markers',
                marker={
                    'size':10,
                    'opacity': 0.5,
                    'color':dff[color_column_name], #set color equal to a variable
                    'colorscale':'Viridis',
                    'showscale':True,
                    'colorbar':{
                        'title':color_column_name}
                }       
        )],
        'layout': go.Layout(
                title='satellite overview',
                margin={'r': 0, 't': 30, 'b': 0, 'l': 0},
                autosize=True,
                hovermode='closest',
                mapbox=go.layout.Mapbox(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    center=go.layout.mapbox.Center(
                        lat=-39.4,
                        lon=177.5
                    ),
                    pitch=0,
                    zoom=8,
                    style='light'
                ),
            )
        }


# Variable plot callback
@app.callback(
    Output('variable-plot', 'figure'),
    [Input('first_variable', 'value'),
     Input('second_variable', 'value'),
     Input('first_variable_type', 'value'),
     Input('second_variable_type', 'value'),
     Input('third_variable', 'value'),
     Input('depth--slider', 'value'),
     Input('time--slider', 'value')])
def update_plot_param(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 color_column_name,
                 depth_value,
                 time_value):

    # filter by date
    dff = df[((df.index > dt.datetime.fromtimestamp(time_value[0])) & (df.index <= dt.datetime.fromtimestamp(time_value[1])))]
    # filter by time
    dff = dff[(dff['depth'] >= depth_value[0]) & (dff['depth'] <= depth_value[1] )]

    return {
        'data': [go.Scatter(
            x=dff[xaxis_column_name],
            y=dff[yaxis_column_name],
            #text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            mode='markers',
            marker={
                'size': 10,
                'opacity': 0.5,
                # 'line': {'width': 0.5, 'color': 'white'}
                'color': dff[color_column_name], #set color equal to a variable
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar':{
                    'title':color_column_name
                }
            }
        )],
        'layout': go.Layout(
            height=480,
            title=xaxis_column_name + ' v ' + yaxis_column_name + ' v ' + color_column_name,
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_name,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            margin={'l': 35, 'b': 30, 't': 25, 'r': 10},
            hovermode='closest'
        )
    }

# Profile plot callback
@app.callback(
    Output('profile-plot', 'figure'),
    [Input('first_variable', 'value'),
     Input('first_variable_type', 'value'),
     Input('third_variable', 'value'),
     Input('depth--slider', 'value'),
     Input('time--slider', 'value')])
def update_plot_profile(xaxis_column_name,
                 xaxis_type,
                 color_column_name,
                 depth_value,
                 time_value):

    # filter by date
    dff = df[((df.index > dt.datetime.fromtimestamp(time_value[0])) & (df.index <= dt.datetime.fromtimestamp(time_value[1])))]
    # filter by time
    dff = dff[(dff['depth'] >= depth_value[0]) & (dff['depth'] <= depth_value[1] )]
    
    return {
        'data': [go.Scatter(
            x=dff[xaxis_column_name],
            y=dff['depth'],
            #text=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'],
            mode='markers',
            marker={
                'size': 10,
                'opacity': 0.5,
                # 'line': {'width': 0.5, 'color': 'white'}
                'color': dff[color_column_name], #set color equal to a variable
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar':{
                    'title':color_column_name
                    }
            }
        )],
        'layout': go.Layout(
            height=480,
            title=xaxis_column_name + ' profile',
            xaxis={
                'title': xaxis_column_name,
                'type': 'linear' if xaxis_column_name == 'Linear' else 'log'
            },
            yaxis={
                'title': 'depth (m)',
                'type': 'linear',
                'autorange': 'reversed'
            },
            margin={'l': 35, 'b': 30, 't': 25, 'r': 10},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)