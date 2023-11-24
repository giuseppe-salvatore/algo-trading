from datetime import datetime
from lib.util.logger import log

entries = {}


def start(name):
    entries[name] = {"start": datetime.now()}
    log.debug("Timer {} started".format(name))


def stop(name):
    if name in entries.keys():
        entries[name]["stop"] = datetime.now()
        log.debug("Timer {} stopped".format(name))
    else:
        log.warn("Timer {} does not exist".format(name))


def get_elapsed(name):
    if name in entries.keys():
        return entries[name]["stop"] - entries[name]["start"]
    else:
        log.warn("Timer {} does not exist".format(name))


def print_elapsed(name):
    log.debug("Timer: " + str(name) + " = " + str(get_elapsed(name)))
