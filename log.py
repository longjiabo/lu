import datetime

logs = []


def debug(s):
    s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " debug " + s
    logs.append(s)
    print(s)


def info(s):
    s = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " info " + s
    logs.append(s)
    print(s)


def flush():
    with open("log.log", 'a') as f:
        for i in logs:
            f.write(i + "\r\n")
    logs.clear()
