import json

def loadScript():
    with open('script.json') as f:
        return json.load(f)


def saveScript(scriptDict):
    with open('script.json', 'w') as f:
        json.dump(scriptDict, f, indent=2)
