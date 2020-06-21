import os
import json


LOOKUPLIST_LOCATION = os.path.join(
    "data", "lookuplists", "condition.json"
)

with open(LOOKUPLIST_LOCATION, 'r') as fp:

    listcontent = json.load(fp)

for i in listcontent["condition"]:
    if "coding" in i:
        #coding already done
        pass
    else:
        print(i["name"])