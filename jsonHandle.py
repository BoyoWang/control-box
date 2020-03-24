import json

def loadScript():
    with open('script.json') as f:
        return json.load(f)

# print(impoortedSteps)

# impoortedSteps = {
#     "totalCycles": 2,
#     "steps" : [
#         [0.5, "EPB_apply", "SB_apply"],
#         [0.5, "EPB_release", "SB_release"],
#         [0.5, "EPB_off", "SB_apply"],
#         [0.5, "EPB_apply", "SB_release"],
#         [0.5, "EPB_release", "SB_apply"]
#     ]
# }

def saveScript(scriptDict):
    with open('script.json', 'w') as f:
        json.dump(scriptDict, f, indent=2)
