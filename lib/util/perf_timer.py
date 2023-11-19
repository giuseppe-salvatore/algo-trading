from datetime import datetime

entries = {}

def start(name):
    entries[name] = {
        "start" : datetime.now()
    }

def stop(name):
    if name in entries.keys():
        entries[name]["stop"] = datetime.now()

def get_elapsed(name):
    if name in entries.keys():
        return entries[name]["stop"] - entries[name]["start"];
    
def print_elapsed(name):
    print("Timer: " + str(name) + " = " + str(get_elapsed(name)))