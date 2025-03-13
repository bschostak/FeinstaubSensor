# main.py 1.0.3
#
# Neutralino PythonExtension.
#
# (c)2023-2024 Harald Schneider - marketmix.com

from NeutralinoExtension import *  # noqa: F403
import time
# from app import analyze_sensor, draw_graph
from gui_tests import analyze_sensor

DEBUG = True    # Print incoming event messages to the console

def taskLongRun(d):
    #
    # Simulate a long running task.
    # Progress messages are queued and polled every 500 ms from the fronted.

    for i in range(5):
        ext.sendMessage('pingResult', "Long-running task: %s / %s" % (i + 1, 5))
        time.sleep(1)

    ext.sendMessage("stopPolling")

def ping(d):
    #
    # Send some data to the Neutralino app

    ext.sendMessage('pingResult', f'Python says PONG, in reply to "{d}"')

def processAppEvent(d):
    """
    Handle Neutralino app events.
    :param d: data package as JSON dict.
    :return: ---
    """

#* Registered functions

    if ext.isEvent(d, 'runPython'):
        (f, d) = ext.parseFunctionCall(d)

        # Process incoming function calls:
        # f: function-name, d: data as JSON or string
        #
        if f == 'ping':
            ping(d)
        elif f == 'longRun':
            ext.sendMessage("startPolling")
            ext.runThread(taskLongRun, 'taskLongRun', d)
        elif f == 'analyze_sensor_wrapper':
            ext.runThread(analyze_sensor_wrapper, 'analyze_sensor_wrapper', d)


#* Application Code (wrapper functions)

def analyze_sensor_wrapper(d):
    result = analyze_sensor(d[0], d[1], d[2], d[3])

    ext.sendMessage('analyzeSensorWrapperResult', result)

# Activate extension
#
ext = NeutralinoExtension(DEBUG)
ext.run(processAppEvent)
