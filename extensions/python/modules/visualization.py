import plotly.graph_objects as go
import base64
import datetime

def draw_interactive_graph(analysed_data: list[tuple[datetime.datetime, float, float, float, float]]) -> str:
    """
    Generate an interactive HTML graph of temperature data and return it as a base64-encoded string.

    Args:
        analysed_data (list[tuple[datetime.datetime, float, float, float, float]]): A list of temperature data tuples
            containing datetime, average temperature, high temperature, low temperature, and temperature difference.

    Returns:
        str: Base64-encoded HTML visualization of temperature data with interactive Plotly graph.
    """

    dates = [data[0] for data in analysed_data]
    avg_temps = [data[1] for data in analysed_data]
    high_temps = [data[2] for data in analysed_data]
    low_temps = [data[3] for data in analysed_data]
    temp_diffs = [data[4] for data in analysed_data]

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=dates, y=avg_temps, mode='lines', name='Ø', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates, y=high_temps, mode='lines', name='max', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=dates, y=low_temps, mode='lines', name='min', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=dates, y=temp_diffs, mode='lines', name='diff', line=dict(color='orange')))
    
    fig.update_layout(
        title='Temperature Analysis',
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        legend=dict(x=0, y=1, traceorder='normal'),
        hovermode='x unified',
        template='plotly_white',
        autosize=True,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')

    html_path = 'temperaturanalyse.html'
    fig.write_html(html_path)
    
    # Read the HTML file and convert to base64
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    
    return encoded_html