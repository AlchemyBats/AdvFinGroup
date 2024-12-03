import dash
from dash import dcc, html, Input, Output, State
import logic  # Assuming the logic file is named logic.py and in the same directory

user = None
passw = None
# Initialize Dash app
app = dash.Dash(__name__)

# Define bundles (grouping tickers)
bundles = {
    "Bundle 1": ["DBC", "GSG"],
    "Bundle 2": ["GLD", "DIA"],
    "Bundle 3": ["SPY", "GOVT"]
}

# Initialize pledge tracking
pledge_amounts = {bundle: 0 for bundle in bundles.keys()}
bundle_goals = {bundle: 10000 for bundle in bundles.keys()}  # Fixed pledge goal for all bundles

def calculate_bundle_costs():
    """Calculate the cost of each bundle dynamically with a 5% markup."""
    bundle_costs = {}
    for bundle_name, tickers in bundles.items():
        # Fetch data for the bundle
        data = logic.fetch_data(tickers, logic.benchmark_ticker, "2010-01-01", True, user, passw)

        # Calculate bundle cost as the sum of the last available prices of the ETFs
        bundle_base_cost = data.iloc[-1].sum()
        
        # Add a 5% markup
        bundle_costs[bundle_name] = bundle_base_cost * 1.05

    return bundle_costs

# Dynamically calculate bundle costs
bundle_costs = calculate_bundle_costs()

# Layout
app.layout = html.Div([
    # Hidden storage for the active bundle
    dcc.Store(id="active-bundle", data=""),
    # Page 1: Bundle selection
    html.Div(id="page-1", children=[
        html.H1("Crowdfunding Investment Platform"),
        html.H2("Choose a Bundle"),
        html.Div([
            html.Button(f"Select {bundle}", id=f"btn-{i}", n_clicks=0, className="bundle-btn")
            for i, bundle in enumerate(bundles.keys())
        ]),
        html.Div(id="pledge-summary", children=[
            html.P(f"{bundle}: ${pledge_amounts[bundle]:,.2f} pledged out of ${bundle_goals[bundle]:,.2f} "
                   f"({pledge_amounts[bundle] / bundle_goals[bundle] * 100:.2f}% achieved)")
            for bundle in bundles.keys()
        ])
    ]),

    # Page 2: Bundle details
    html.Div(id="page-2", style={"display": "none"}, children=[
        html.H1("Bundle Details"),
        html.Div(id="bundle-metrics"),
        dcc.Graph(id="bundle-visualization"),
        html.Label("Pledge Amount ($):"),
        dcc.Input(id="pledge-input", type="number", value=0),
        html.Button("Pledge", id="pledge-btn"),
    ])
])

# Callbacks
@app.callback(
    [Output("page-1", "style"),
     Output("page-2", "style"),
     Output("bundle-metrics", "children"),
     Output("bundle-visualization", "figure"),
     Output("active-bundle", "data"),
     Output("pledge-summary", "children")],
    [Input(f"btn-{i}", "n_clicks") for i in range(len(bundles.keys()))] +
    [Input("pledge-btn", "n_clicks")],
    [State("active-bundle", "data"), State("pledge-input", "value")],
    prevent_initial_call=True
)
def handle_page_navigation(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {"display": "block"}, {"display": "none"}, "", {}, "", []

    # Determine which input triggered the callback
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # If a bundle button was clicked
    if trigger_id.startswith("btn"):
        button_index = int(trigger_id.split("-")[1])
        bundle_name = list(bundles.keys())[button_index]
        tickers = bundles[bundle_name]
        global recall_user
        global recall_passw
        # Fetch data and metrics
        data = logic.fetch_data(tickers, logic.benchmark_ticker, "2010-01-01", True, user, passw)
        trailing_returns_df = logic.calculate_trailing_returns(data)
        risk_stats_df = logic.calculate_risk_statistics(data)
        dividends_df = logic.calculate_dividend_info(tickers, data)

        # Prepare metrics to display
        metrics = html.Div([
            html.H3("Trailing Returns"),
            dcc.Markdown(trailing_returns_df.to_markdown()),
            html.H3("Risk Statistics"),
            dcc.Markdown(risk_stats_df.to_markdown()),
            html.H3("Dividend Information"),
            dcc.Markdown(dividends_df.to_markdown())
        ])

        # Prepare visualization
        fig = logic.generate_visualization(trailing_returns_df)

        # Set the active bundle and navigate to the second page
        return {"display": "none"}, {"display": "block"}, metrics, fig, bundle_name, dash.no_update

    # If the pledge button was clicked
    elif trigger_id == "pledge-btn":
        active_bundle = args[-2]
        pledge_amount = args[-1]

        if active_bundle and pledge_amount:
            # Update the pledge amount
            pledge_amounts[active_bundle] += pledge_amount

        # Update the pledge summary
        pledge_summary = [
            html.P(f"{bundle}: ${pledge_amounts[bundle]:,.2f} pledged out of ${bundle_goals[bundle]:,.2f} "
                   f"({pledge_amounts[bundle] / bundle_goals[bundle] * 100:.2f}% achieved)")
            for bundle in bundles.keys()
        ]

        # Redirect back to the first page
        return {"display": "block"}, {"display": "none"}, "", {}, "", pledge_summary


if __name__ == "__main__":
    app.run_server(debug=True)
