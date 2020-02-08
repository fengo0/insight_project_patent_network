#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from colour import Color
from datetime import datetime
from textwrap import dedent as d
import json
import psycopg2
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# import the css template, and pass the css template into dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Patent Network"

# initial data
yearRange = [1970,2020] 
YEAR = [1970,2020]
PATENT_ID = '6319852'
edge = pd.read_csv('edge.csv')
node = pd.read_csv('node.csv')

# query function
def conn_generate(search_id):
    try:
        connection = psycopg2.connect(user="username",
                                  password="password",
                                  host="redshift endpoint",
                                  port="5439",
                                  database="patent")
        cursor = connection.cursor()
    
        postgreSQL_select_Query1 = "select * from patent.patent_info.uspatentcitation where citation_id like "+ str(search_id) +";"   
    
        cursor.execute(postgreSQL_select_Query1)
    
        patent_citations = cursor.fetchall() 
  
        citation_id = []
        patent_id = []
        date = []

        for row in patent_citations:
            citation_id.append(row[2])
            patent_id.append(row[1])
        
            postgreSQL_select_Query2 = "select date from patent.patent_info.patent where id like "+str(row[1])+";"
            cursor.execute(postgreSQL_select_Query2)
            patent_date = cursor.fetchall()
            date.append(patent_date[0][0])
        
        df1 = pd.DataFrame({'citation_id': citation_id,
                            'patent_id': patent_id,
                            'date': date})
#        df1.to_csv('edge.csv',index=False,columns=["citation_id","patent_id","date"])

###############################################################
        id = []
        title = []
        claims = []
        patent_id.insert(0,citation_id[0])
        for id_num in patent_id:
            postgreSQL_select_Query = "select * from patent.patent_info.patent where id like "+str(id_num)+";"
 
            cursor.execute(postgreSQL_select_Query)
            patent = cursor.fetchall() 
       
            for row in patent:
                id.append(row[0])
                title.append(row[6])
                claims.append(row[8])

        df = pd.DataFrame({'id': id,'title': title,'num_claims': claims,'patent_id':id})
         
#       df.to_csv('node.csv',index= False,columns=["id","title","num_claims","patent_id"])
    
#       edge = pd.read_csv('edge.csv')
#       node = pd.read_csv('node.csv')

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
    return df1, df

def network_graph(edge,node):

    #edge1 = pd.read_csv('edge.csv')
    #node1 = pd.read_csv('node.csv')
    
    edge1 = edge
    node1 = node
    # filter the record by datetime, to enable interactive control through the input box
    edge1['Datetime'] = "" # add empty Datetime column to edge1 dataframe
    accountSet=set() # contain unique account
    for index in range(0,len(edge1)):
        edge1['Datetime'][index] = datetime.strptime(edge1['date'][index],'%Y-%m-%d')
        if edge1['Datetime'][index].year<yearRange[0] or edge1['Datetime'][index].year>yearRange[1]:
            edge1.drop(axis=0, index=index, inplace=True)
            continue
        accountSet.add(edge1['citation_id'][index])
        accountSet.add(edge1['patent_id'][index])

    # to define the centric point of the networkx layout
    shells=[]
    shell1=[]
    shell1.append(edge1['citation_id'][0])
    shells.append(shell1)
    shell2=[]
    for ele in accountSet:
        if ele!=edge1['citation_id'][0]:
            shell2.append(ele)
    shells.append(shell2)

    G = nx.from_pandas_edgelist(edge1, 'citation_id', 'patent_id', ['citation_id', 'patent_id','date'], create_using=nx.MultiDiGraph())

    nx.set_node_attributes(G, node1.set_index('id')['title'].to_dict(), 'title')
    nx.set_node_attributes(G, node1.set_index('id')['num_claims'].to_dict(), 'num_claims')
    nx.set_node_attributes(G, node1.set_index('id')['patent_id'].to_dict(), 'patent_id')

    #pos = nx.layout.spring_layout(G)
    #pos = nx.layout.circular_layout(G)
    #nx.layout.shell_layout only works for more than 3 nodes
    if len(shell2)>1:
        pos = nx.layout.shell_layout(G, shells)
    else:
        pos = nx.layout.spring_layout(G)
    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])


    if len(shell2)==0:
        traceRecode = []  # contains edge_trace, node_trace, middle_node_trace
        node_trace = go.Scatter(x=tuple([1]), y=tuple([1]), text=tuple([str(edge1['citation_id'][0])]), textposition="bottom center",
                                mode='markers+text',
                                marker={'size': 50, 'color': 'LightSkyBlue'})


        traceRecode.append(node_trace)

        node_trace1 = go.Scatter(x=tuple([1]), y=tuple([1]),
                                mode='markers',
                                marker={'size': 50, 'color': 'LightSkyBlue'},
                                opacity=0)
        traceRecode.append(node_trace1)

        figure = {
            "data": traceRecode,
            "layout": go.Layout(title='Interactive Transaction Visualization', showlegend=False,
                                margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                                xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                height=600
                                )}
        return figure


    traceRecode = []  # contains edge_trace, node_trace, middle_node_trace
    
##################################################################################################
    colors = list(Color('lightcoral').range_to(Color('darkred'), len(G.edges())))
    colors = ['rgb' + str(x.rgb) for x in colors]

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        trace = go.Scatter(x=tuple([x0, x1, None]), y=tuple([y0, y1, None]),
                           mode='lines',
            #               line={'width': weight},
                           marker=dict(color=colors[index]),
                           line_shape='spline',
                           opacity=1)
        traceRecode.append(trace)
        index = index + 1
####################################################################################################
    node_trace = go.Scatter(x=[], y=[], hovertext=[], text=[], mode='markers+text', textposition="bottom center",
                            hoverinfo="text", marker={'size': 50, 'color': 'LightSkyBlue'})

    index = 0
    for node in G.nodes: 
        x, y = G.nodes[node]['pos']
        hovertext = "Title: " + str(G.nodes[node]['title']) + "<br>" + "#claims: " + str(G.nodes[node]['num_claims'])
        text = str(G.nodes[node]['patent_id'])
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['hovertext'] += tuple([hovertext])
        node_trace['text'] += tuple([text])
        index = index + 1

    traceRecode.append(node_trace)
#####################################################################################################
    middle_hover_trace = go.Scatter(x=[], y=[], hovertext=[], mode='markers', hoverinfo="text",
                                    marker={'size': 20, 'color': 'LightSkyBlue'},
                                    opacity=0)

    index = 0
    for edge in G.edges:
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        hovertext = "From: " + str(G.edges[edge]['citation_id']) + "<br>" + "To: " + str(G.edges[edge]['patent_id']) + "<br>" + "Date: " + str(G.edges[edge]['date'])
        middle_hover_trace['x'] += tuple([(x0 + x1) / 2])
        middle_hover_trace['y'] += tuple([(y0 + y1) / 2])
        middle_hover_trace['hovertext'] += tuple([hovertext])
        index = index + 1

    traceRecode.append(middle_hover_trace)

#####################################################################################################
    figure = {
        "data": traceRecode,
        "layout": go.Layout(title='Patent Visualization', showlegend=False, hovermode='closest',
                            margin={'b': 40, 'l': 40, 'r': 40, 't': 40},
                            xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                            height=600,
                            clickmode='event+select',
                            annotations=[
                                dict(
                                    ax=(G.nodes[edge[0]]['pos'][0] + G.nodes[edge[1]]['pos'][0]) / 2,
                                    ay=(G.nodes[edge[0]]['pos'][1] + G.nodes[edge[1]]['pos'][1]) / 2, axref='x', ayref='y',
                                    x=(G.nodes[edge[1]]['pos'][0] * 3 + G.nodes[edge[0]]['pos'][0]) / 4,
                                    y=(G.nodes[edge[1]]['pos'][1] * 3 + G.nodes[edge[0]]['pos'][1]) / 4, xref='x', yref='y',
                                    showarrow=True,
                                    arrowhead=3,
                                    arrowsize=4,
                                    arrowwidth=1,
                                    opacity=1
                                ) for edge in G.edges]
                            )}
    return figure
##############################################title####################################################
app.layout = html.Div([
    html.Div([html.H1("Patent Network Graph")],
        className="row",
        style={'textAlign': "center"}),
    html.Div(
        className="row",
        children=[
##############################################left side two input components###########################
            html.Div(
                className="two columns",
                children=[
                    dcc.Markdown(d("""
                            **Time Range To Visualize**
                            Slide the bar to define year range.
                            """)),
                    html.Div(
                        className="twelve columns",
                        children=[
                            dcc.RangeSlider(
                                id='my-range-slider',
                                min=1970,
                                max=2020,
                                step=1,
                                value=[1970, 2020],
                                marks={
                                    1970: {'label': '70'},
                                    1980: {'label': '80'},
                                    1990: {'label': '90'},
                                    2000: {'label': '00'},
                                    2010: {'label': '10'},
                                    2020: {'label': '20'}
                                }
                            ),
                            html.Br(),
                            html.Div(id='output-container-range-slider')
                        ],
                        style={'height': '300px'}
                    ),
                    
                    html.Div(
                        className="twelve columns",
                        children=[dcc.Markdown(d("""
                                  **Patent To Search**
                              
                                  Input the patent id to visualize.
                                  """)),
                            dcc.Input(id="input-box", type="value"),
                            html.Div(id="output")],
                        style={'height': '400px'}),
             ]),
################################middle graph component###################################
           html.Div(
               className="eight columns",
               children=[dcc.Graph(id="my-graph",figure=network_graph(edge,node))])
      ])
])

###################################callback for left side components
@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('input-box', 'value')])
def update_output(value):
    PATENT_ID = value
    edge1, node1 = conn_generate(PATENT_ID)
    return network_graph(edge1,node1)
# to update the global variable of YEAR and ACCOUNT
################################callback for right side components
#@app.callback(
#    dash.dependencies.Output('hover-data', 'children'),
#    [dash.dependencies.Input('my-graph', 'hoverData')])
#def display_hover_data(hoverData):
#    return json.dumps(hoverData, indent=2)

#@app.callback(
#    dash.dependencies.Output('click-data', 'children'),
#    [dash.dependencies.Input('my-graph', 'clickData')])
#def display_click_data(clickData):
#    return json.dumps(clickData, indent=2)

if __name__ == '__main__':
    app.run_server(port=8050,host='ec2-18-210-64-34.compute-1.amazonaws.com')
