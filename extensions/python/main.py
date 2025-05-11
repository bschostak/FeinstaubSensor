# main.py 1.0.3
#
# Neutralino PythonExtension.
#
# (c)2023-2024 Harald Schneider - marketmix.com

from NeutralinoExtension import *  # noqa: F403
import time
import sensor_app as app
import modules.year_fetcher as year_fetcher

DEBUG = True  # Print incoming event messages to the console


def taskLongRun(d):
    #
    # Simulate a long running task.
    # Progress messages are queued and polled every 500 ms from the fronted.

    for i in range(5):
        ext.sendMessage("pingResult", "Long-running task: %s / %s" % (i + 1, 5))
        time.sleep(1)

    ext.sendMessage("stopPolling")

def ping(d):
    #
    # Send some data to the Neutralino app

    ext.sendMessage("pingResult", f'Python says PONG, in reply to "{d}"')


def processAppEvent(d):
    """
    Handle Neutralino app events.
    :param d: data package as JSON dict.
    :return: ---
    """

    # * Registered functions

    if ext.isEvent(d, "runPython"):
        (f, d) = ext.parseFunctionCall(d)

        # Process incoming function calls:
        # f: function-name, d: data as JSON or string
        #
        if f == "ping":
            ping(d)
        elif f == "longRun":
            ext.sendMessage("startPolling")
            ext.runThread(taskLongRun, "taskLongRun", d)
        elif f == "analyze_sensor_wrapper":
            ext.runThread(analyze_sensor_wrapper, "analyze_sensor_wrapper", d)
        elif f == "delete_sensor_data_files_wrapper":
            ext.runThread(delete_sensor_data_files_wrapper, "delete_sensor_data_files_wrapper", d)
        elif f == "stop_download_wrapper":
            ext.runThread(stop_download_wrapper, "stop_download_wrapper", d)
        elif f == "fetch_available_years_wrapper":
            ext.runThread(fetch_available_years_wrapper, "fetch_available_years_wrapper", d)


# * Application Code (wrapper functions)
def analyze_sensor_wrapper(d) -> None:
    """
    Wrapper function to analyze sensor data and generate a graph.
    
    Calls app.analyze_sensor with provided data, then draws a graph from the analyzed data.
    Sends the resulting base64 encoded graph image to the frontend via Neutralino message.
    
    :param d: List containing sensor data parameters [param1, param2, param3, param4]
    """

    analyzed_sensor_data = app.analyze_sensor(d[0], d[1], d[2], d[3], extension=ext)

    if analyzed_sensor_data is None:
        return

    base64_html_data: str = app.draw_interactive_graph(analyzed_sensor_data)

    ext.sendMessage("displaySensorHtml", base64_html_data)


def delete_sensor_data_files_wrapper(d) -> None:
    """
    Wrapper function to delete sensor data files.
    
    Calls app.delete_sensor_data_files with the current extension context.
    
    :param d: Unused parameter to maintain consistent wrapper function signature
    """
    
    app.delete_sensor_data_files(extension=ext)


def stop_download_wrapper(d) -> None:
    """
    Wrapper function to trigger the download cancellation.

    This function calls `app.stop_download()` to stop an ongoing download process.
    It is intended to be used as a callback or intermediary function for UI elements 
    such as buttons or event handlers.

    :param d: Unused parameter to maintain consistent wrapper function signature
    """

    app.stop_download()


def fetch_available_years_wrapper(d) -> None:
    """
    Wrapper function to fetch and populate available years data.
    
    Calls available_years.fetch_available_years() to retrieve available years,
    then sends the data to the frontend to populate year dropdown menus.
    
    :param d: Unused parameter to maintain consistent wrapper function signature
    """
    
    fetched_years_data = year_fetcher.fetch_available_years()
    ext.sendMessage("populateYearDropdowns", fetched_years_data)


# Activate extension
#
ext = NeutralinoExtension(DEBUG)  # noqa: F405
ext.run(processAppEvent)
