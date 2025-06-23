import plotly.graph_objects as go
import base64
from modules.data_operations import AnalyzedSensor
from modules.data_operations import AnalyzedSensorData

def draw_interactive_graph(analysed_data: AnalyzedSensor) -> str:
    """
    Generate an interactive HTML graph of temperature and humidity data and return it as a base64-encoded string.

    Args:
        analysed_data (AnalyzedSensor): Sensor data with temperature and humidity.

    Returns:
        str: Base64-encoded HTML visualization of temperature and humidity data with interactive Plotly graph.
    """

    dates = [data.timestamp for data in analysed_data.temperature_data]
    avg_temps = [data.avg for data in analysed_data.temperature_data]
    high_temps = [data.max for data in analysed_data.temperature_data]
    low_temps = [data.min for data in analysed_data.temperature_data]
    temp_diffs = [data.diff for data in analysed_data.temperature_data]

    avg_humidity = [data.avg for data in analysed_data.humidity_data]
    high_humidity = [data.max for data in analysed_data.humidity_data]
    low_humidity = [data.min for data in analysed_data.humidity_data]
    diff_humidity = [data.diff for data in analysed_data.humidity_data]

    fig = go.Figure()

    # Temperatur-Traces (linke Y-Achse)
    fig.add_trace(go.Scatter(x=dates, y=avg_temps, mode='lines', name='Temp Ø', line=dict(color='blue'), yaxis='y1'))
    fig.add_trace(go.Scatter(x=dates, y=high_temps, mode='lines', name='Temp max', line=dict(color='red'), yaxis='y1'))
    fig.add_trace(go.Scatter(x=dates, y=low_temps, mode='lines', name='Temp min', line=dict(color='green'), yaxis='y1'))
    fig.add_trace(go.Scatter(x=dates, y=temp_diffs, mode='lines', name='Temp diff', line=dict(color='orange'), yaxis='y1'))

    # Feuchtigkeits-Traces (rechte Y-Achse)
    fig.add_trace(go.Scatter(x=dates, y=avg_humidity, mode='lines', name='Humidity Ø', line=dict(color='purple', dash='dot'), yaxis='y2'))
    fig.add_trace(go.Scatter(x=dates, y=high_humidity, mode='lines', name='Humidity max', line=dict(color='magenta', dash='dot'), yaxis='y2'))
    fig.add_trace(go.Scatter(x=dates, y=low_humidity, mode='lines', name='Humidity min', line=dict(color='teal', dash='dot'), yaxis='y2'))
    fig.add_trace(go.Scatter(x=dates, y=diff_humidity, mode='lines', name='Humidity diff', line=dict(color='brown', dash='dot'), yaxis='y2'))

    fig.update_layout(
        title='Temperature and Humidity Analysis',
        xaxis_title='Date',
        yaxis=dict(
            title='Temperature (°C)',
            side='left',
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGrey'
        ),
        yaxis2=dict(
            title='Humidity (%)',
            side='right',
            overlaying='y',
            showgrid=False
        ),
        legend=dict(x=0, y=1, traceorder='normal'),
        hovermode='x unified',
        template='plotly_white',
        autosize=True,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')

    html_path = 'temperaturanalyse.html'
    fig.write_html(html_path)

    # Read the HTML file and convert to base64
    with open(html_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')

    return encoded_html