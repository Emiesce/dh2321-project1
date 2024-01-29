from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

external_script = ["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}] # enable TailwindCSS

app = Dash(
    __name__,
    external_scripts=external_script,
)
app.scripts.config.serve_locally = True

df = pd.read_csv('./Self-Introduction to IVIS24 (Responses).csv')

# Remove rows with missing values in the "ALIAS" column
df = df.dropna(subset=['ALIAS'])

df_num = df[['viz','stats', 'math', 'art', 'ui', 'code', 'graph', 'hci', 'eval', 'comm', 'collab', 'GIT', 'avg']]

# Remove columns that do not help determine the best groups
df.drop(columns=["Timestamp", 
    "If you are studying at a university other than KTH, which is it?",
    "In what year did you start your university degree ?",
    "What year and month you expect to graduate?",
    "Do you use KTH Canvas?",
    "If you are working towards a master's degree, what is the status of your thesis? You:",
    "Unnamed: 23"], inplace=True)

# V2 for displaying Table for User
df_v2 = df[['ALIAS', 'MAJOR', "What degree are you pursuing?",
 'viz','stats', 'math', 'art', 'ui', 'code', 'graph', 'hci', 'eval', 'comm', 'collab', 'GIT', 'avg']]

app.layout = html.Div([
    html.Div([
        # Website Title
        html.Div([
                'DH2321 - Group Visualisation Tool'
                ], className="text-center text-[28px] bg-gray-light h-[80px] px-4 flex justify-between items-center border-b border-gray-medium text-gray-medium"),
            ], className="flex gap-8 items-center font-medium ml-4, p-5"),

    html.H1('Overview', className='text-center text-[28px] mb-4'),

    # Dropdown for selecting column to display histogram
    dcc.Dropdown(
        id='column-selector',
        options=[{'label': col, 'value': col} for col in df_v2.columns[1:]],
        value=df_v2.columns[1],
        multi=False,
        style={'width': '50%', 'margin': 'auto', 'align-items': 'center'}
    ),
    dcc.Graph(id='histogram-chart'),

    # Group Member Details
    html.H1('Group Members Details', className='text-center text-[28px] mt-4'),
    html.H2('Select Users in the Table below to compare their skills and interests.', className='text-center'),
    html.H2(' Each column can be sorted in ascending/descending order, as well as filtered by typing in the box below the column name', className='text-center mb-4'),

    # Table for User Selection and Details
    dash_table.DataTable(data = df_v2.to_dict('records'),
        columns=[
            {"name": i, "id": i, "selectable": True} for i in df_v2.columns
        ],
        row_selectable = "multi",
        id ='user-selector',
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
    ),

    # Info Card for each User
    html.Div(id='infocard-container', className="mt-4 flex gap-8 justify-center ml-4, p-5"),
    
    # Radar and Heatmap Chart
    html.Div([
        dcc.Graph(id='radar-chart'),
        dcc.Graph(id='heatmap-chart')
    ], className="flex gap-8 items-center font-medium ml-4, p-5"),
])

# Define callback to update the Radar Chart based on user selection
@app.callback(
    Output('radar-chart', 'figure'),
    [Input('user-selector', 'derived_virtual_selected_rows')],
)
def update_radar_chart(selected_user_indices):

    if selected_user_indices is None or len(selected_user_indices) == 0:
        # Return an empty figure if no users are selected
        return px.line_polar(
            r = [0 for _ in df_num.columns],
            theta=['viz','stats', 'math', 'art', 'ui', 'code', 'graph', 'hci', 'eval', 'comm', 'collab', 'GIT', 'avg'],
            height=700,
            width=700
        )

    fig = go.Figure()

    # For each selected user, add a trace to the figure
    for i in selected_user_indices:
        fig.add_trace(go.Scatterpolar(
            r=df_num.iloc[i],
            theta=df_num.columns,
            fill='toself',
            name=df['ALIAS'].iloc[i]
        ))

    fig.update_layout(
        polar = dict(
            radialaxis=dict(
            visible=True,
            range=[0, 10]
        )),
        showlegend=True,
        height=700,
        width=700
    )

    return fig

# Callback to update Piechart
@app.callback(
    Output('histogram-chart', 'figure'),
    [Input('column-selector', 'value')]
)
def update_pie_chart(selected_column):
    fig = px.histogram(df, x = selected_column, hover_data=df.columns, title=f'Histogram for {selected_column}')
    return fig

# Callback to update Heatmap
@app.callback(
    Output('heatmap-chart', 'figure'),
    [Input('user-selector', 'derived_virtual_selected_rows')]
)
def update_heatmap(selected_user_indices):
    if selected_user_indices is None or len(selected_user_indices) == 0:
        # Return an empty figure if no users are selected
        return px.imshow(
            [[0 for _ in df_num.columns]],
            labels=dict(x="Skills", y="Users"),
            x=['viz','stats', 'math', 'art', 'ui', 'code', 'graph', 'hci', 'eval', 'comm', 'collab', 'GIT', 'avg'],
            height=700,
            width=700
        )

    fig = px.imshow(
        [df_num.iloc[i] for i in selected_user_indices],
        labels=dict(x="Skills", y="Users", color="Rating"),
        x=['viz','stats', 'math', 'art', 'ui', 'code', 'graph', 'hci', 'eval', 'comm', 'collab', 'GIT', 'avg'],
        y = [df['ALIAS'].iloc[i] for i in selected_user_indices],
        height=700,
        width=700
    )

    return fig

# Callback to update Info Card
@app.callback(
    Output('infocard-container', 'children'),
    [Input('user-selector', 'derived_virtual_selected_rows')]
)
def update_infocard(selected_user_indices):
    # Infocard contains Alias and Interests
    if selected_user_indices is None or len(selected_user_indices) == 0:
        return html.Div([
            html.H1('No User Selected', className='text-center text-[28px] mb-4')
        ])
    
    infocard_list = []

    # For each selected user, add an infocard to the list
    for i in selected_user_indices:
        infocard_list.append(
            html.Div([
                html.H1(f'Member: {df["ALIAS"].iloc[i]}', className='text-center text-[28px] mb-4'),
                html.H2(f'Major: {df["MAJOR"].iloc[i]}', className='text-center text-14px mb-4'),

                html.P(f'Interests: {df["Interests"].iloc[i]}', className='text-center text-14px mb-4'),
                html.P(f'Previous Courses: {df["What courses have you completed that are relevant to Information Visualization, where and when?"].iloc[i]}', className='text-center text-14px mb-4'),
        ], className="items-center p-3 bg-gray-100"))

    return infocard_list

if __name__ == '__main__':
    app.run(debug=True)