# main.py 1.0.3
#
# Neutralino PythonExtension.
#
# (c)2023-2024 Harald Schneider - marketmix.com

from NeutralinoExtension import *  # noqa: F403
import time
import gui_tests
import available_years

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


# * Application Code (wrapper functions)
def analyze_sensor_wrapper(d):
    analyzed_sensor_data = gui_tests.analyze_sensor(
        d[0], d[1], d[2], d[3], extension=ext
    )

    base64_data: str = gui_tests.draw_graph(analyzed_sensor_data)

    ext.sendMessage("displaySensorImage", base64_data)


def delete_sensor_data_files_wrapper(d):
    gui_tests.delete_sensor_data_files(extension=ext)

#TODO: add function call in js.
def fetch_available_years_wrapper(d):
    available_years_data = available_years.fetch_available_years()
    ext.sendMessage("getAvailableYears", available_years_data)


# Activate extension
#
ext = NeutralinoExtension(DEBUG)
ext.run(processAppEvent)