# importing libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# reading our data into df
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# initializing dash app
app = dash.Dash(__name__)

# defining layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        # dropdown list for Launch Site selection
        html.Div(
            [
                dcc.Dropdown(
                    id="site-dropdown",
                    options=[
                        {"label": "All Sites", "value": "ALL"},
                        {"label": "CCAFS LC-40", "value": "CCAFS LC-40"},
                        {"label": "VAFB SLC-4E", "value": "VAFB SLC-4E"},
                        {"label": "KSC LC-39A", "value": "KSC LC-39A"},
                        {"label": "CCAFS SLC-40", "value": "CCAFS SLC-40"},
                    ],
                    value="ALL",
                    placeholder="All Sites",
                    searchable=True,
                )
            ]
        ),
        html.Br(),
        # defining pie chart for succes/fail visualizations
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        html.Div(
            [  # defining range slider for payload range
                dcc.RangeSlider(
                    id="payload-slider",
                    min=0,
                    max=10000,
                    step=1000,
                    value=[min_payload, max_payload],
                ),
                # defining scatter plot for payload and launch outcome
                dcc.Graph(id="success-payload-scatter-plot"),
            ]
        ),
    ]
)


# adding callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        fig = px.pie(spacex_df, values="class", names="Launch Site", title="All Sites")
        return fig
    else:
        # filtering dataset
        site_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        # creating new df with class counts
        site_df = (
            site_df.groupby(["Launch Site", "class"])
            .size()
            .reset_index(name="class count")
        )
        fig = px.pie(site_df, values="class count", names="class", title=entered_site)
        return fig


# adding a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-plot", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_plot(entered_site, entered_range):
    print("RANGE:", entered_range)
    if entered_site == "ALL":
        # filtering dataset for payload range
        filtered_df = spacex_df[
            spacex_df["Payload Mass (kg)"].between(entered_range[0], entered_range[1])
        ]
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
        )
        return fig
    else:
        # filtering dataset for site
        site_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        # filtering dataset for payload range
        filtered_df = site_df[
            site_df["Payload Mass (kg)"].between(entered_range[0], entered_range[1])
        ]
        fig = px.scatter(
            filtered_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
        )
        return fig


# Run the app
if __name__ == "__main__":
    app.run_server()
