import os
import json
import requests

# def SearchSnomed(query:str, mode:str = 'partialMatching', results:int = 5 , semanticfilter:str = 'disorder' ):
#     response = requests.get(
#         'http://browser.ihtsdotools.org/api/v2/snomed/en-edition/v20180131/descriptions',
#         params = {
#             'query' : query,
#             'searchMode': mode,
#             'returnLimit': results,
#             'semanticFilter': semanticfilter 
#         }
#     )

LOOKUPLIST_LOCATION = os.path.join(
    "data", "lookuplists", "condition2.json"
)

with open(LOOKUPLIST_LOCATION, 'r') as fp:

    listcontent = json.load(fp)

for i in listcontent["condition"]:
    if "coding" in i:
        #coding already done
        pass
    else:
        i["coding"] = {
                "code": "0000000",
                "system": "http://snomed.info/sct"
            }

with open(LOOKUPLIST_LOCATION, 'w') as fp:
    json.dump(listcontent, fp, indent=2)
