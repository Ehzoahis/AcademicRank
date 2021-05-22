import requests
import json

HEADERS = {"Ocp-Apim-Subscription-Key": "c9ed15c311b6478bbf1feea30350432a"} # Specific to Haozhe Si
QUERYSTRING = {"mode":"json%0A"}
PAYLOAD = "{}"
sup_key="c9ed15c311b6478bbf1feea30350432a"
COUNT = str(1) # dummy Count, no effect here

def MAG_get_fos(Id):
    # Find all the field of study for given paper ID
    find_field_attr = 'F.FN'
    find_field_url = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?&count={}&expr=AND(Id={})&attributes={}".format(COUNT, str(Id), find_field_attr)
    response = requests.request("GET", find_field_url, headers=HEADERS, data=PAYLOAD, params=QUERYSTRING)
    try:
        entity_list = json.loads(response.text)['entities']
    except:
        return []

    #Get FoS information
    pfos_list = []
    for entity in entity_list:
        fdict = entity['F']
        for fn in fdict:
            fos = fn['FN']
            pfos_list.append(fos)
    return set(pfos_list)

