import matplotlib.pyplot as plt
import base64
import datetime

def get_image_base64(image_path) -> str:
    with open(image_path, "rb") as image_file:
        encoded_string: str = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def draw_graph(analysed_data: list[tuple[datetime.datetime, float, float, float, float]]) -> str:
    #d.strftime("%d/%m/%y") //TODO: Add it later.
    dates = [data[0].timestamp() for data in analysed_data]
    avg_temps = [data[1] for data in analysed_data]
    high_temps = [data[2] for data in analysed_data]
    low_temps = [data[3] for data in analysed_data]
    temp_diffs = [data[4] for data in analysed_data]

    plt.figure(figsize=(10, 6))

    plt.plot(dates, avg_temps, label='Ø', color='blue')
    plt.plot(dates, high_temps, label='max', color='red')
    plt.plot(dates, low_temps, label='min', color='green')
    plt.plot(dates, temp_diffs, label='diff', color='orange')

    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature Analysis')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    #TODO: Save the plot as an SVG file, when it is not clearly visible, use plotly html embed.
    plt.savefig('temperaturanalyse.png')

    base64_image: str = get_image_base64('temperaturanalyse.png')

    return base64_image