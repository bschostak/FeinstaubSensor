import time

from NeutralinoExtension import NeutralinoExtension


def task_long_run(d):
    for i in range(5):
        ext.sendMessage('pingResult', "Long-running task: %s / %s" % (i + 1, 5))
        time.sleep(1)
    ext.sendMessage("stopPolling")


def ping(d):
    ext.sendMessage('pingResult', f'Python says PONG, in reply to "{d}"')


def test(d):
    ext.sendMessage('testResult', f'test: {d}')


def process_app_event(d):
    if ext.isEvent(d, 'runPython'):
        (f, d) = ext.parseFunctionCall(d)
        if f == 'ping':
            ping(d)
        elif f == 'longRun':
            ext.sendMessage("startPolling")
            ext.runThread(task_long_run, 'taskLongRun', d)
        elif f == 'test':
            ext.sendMessage('test', d)
            ext.runThread(test, 'test', d)


ext = NeutralinoExtension(debug=True)
ext.run(process_app_event)
