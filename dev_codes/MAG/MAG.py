# This code is created based on Jiaying Li's code for achieving researcher's paper counts
# which is shared on Slack on Feb 9th, 2021. 

import requests
import json
import glob
import csv
from fuzzywuzzy import fuzz

# GLOBAL VARIABLES
HEADERS = {"Ocp-Apim-Subscription-Key": "c9ed15c311b6478bbf1feea30350432a"} # Specific to Haozhe Si
QUERYSTRING = {"mode":"json%0A"}
PAYLOAD = "{}"
COUNT = str(200)

# Input:    affi - affiliation of the researcher 
#           name - name of the researcher
# Output:   author_mag_id - MAG ID of the researcher
def MAG_get_AuID(affi, name):
    # Preprocessing for author's name and affliation
    name = name.strip().replace(', Ph.D.','').replace('Dr. ','')
    name = name.lower().replace('.', '').replace('-', ' ').replace('(', '').replace(')', '').replace(', ', ' ').replace(',',' ')
    affi = affi.lower().replace('--',' ').replace('-', ' ')
    
    # request author information with name and affiliation from MAG
    find_authorID_attr = 'AA.AuN,AA.AuId'
    find_authorID_url = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?&count=100&expr=Composite(AND(AA.AuN='{}',AA.AfN=='{}'))&attributes={}".format(name, affi, find_authorID_attr)
    response = requests.request("GET", find_authorID_url, headers=HEADERS, data=PAYLOAD, params=QUERYSTRING)
    if 'entities' not in json.loads(response.text):
        print(name+' not Found')
        return
    entity_list = json.loads(response.text)['entities']
    if len(entity_list) == 0:
        print('entity list is empty')
        return 

    # Match author name with returned AA.AuN to determine author ID
    max_ratio = 0
    for author in entity_list[0]['AA']:
        curr_ratio = fuzz.token_sort_ratio(name,author['AuN'])
        if(curr_ratio > max_ratio):
            author_mag_id = author['AuId']
            max_ratio = curr_ratio

    return author_mag_id

# Input:    affi - affiliation of the researcher 
#           name - name of the researcher
# Output:   abstract_list - a list of tuples of (abstract, year, citation)
def MAG_get_abstracts(affi,name):
    # get author ID in MAG
    author_mag_id = MAG_get_AuID(affi,name)
    
    # Find all the papers for that author ID
    find_paper_attr = 'DN,Id,RId,CitCon'
    find_paper_url = "https://api.labs.cognitive.microsoft.com/academic/v1.0/evaluate?&count={}&expr=Composite(AND(AA.AuId={}))&attributes={}".format(COUNT, str(author_mag_id), find_paper_attr)
    response = requests.request("GET", find_paper_url, headers=HEADERS, data=PAYLOAD, params=QUERYSTRING)
    try:
        entity_list = json.loads(response.text)['entities']
    except:
        return []

    #Get paper information
    abstract_list = []
    for entity_idx, entity in enumerate(entity_list):
        print('[MAG_get_abstracts] Getting the abstract {} of {}'.format(entity_idx, len(entity_list)))
        if 'RId' not in entity or 'CitCon' not in entity:
            continue
        title = entity['DN']
        mag_id = entity['Id']
        ctd_mag_id = entity['RId']
        cit_context = entity['CitCon']
        abstract_list.append((title,mag_id,ctd_mag_id,cit_context))
    return abstract_list


if __name__ == '__main__':
    abstract_list = MAG_get_abstracts('University of Illinois at Urbana Champaign','Kevin Chenchuan Chang')
    print(len(abstract_list))
    with open('./toymag.txt', 'w', encoding='utf-8') as f:
        for ab in abstract_list:
            mag_id = str(ab[1])
            ctd_mag_id = ab[2]
            ctd_context = ab[3]
            for ctd_mag in ctd_mag_id:
                ctd_mag = str(ctd_mag)
                if ctd_mag in ctd_context.keys():
                    context_list = ctd_context[ctd_mag]
                    for context in context_list:
                        val = [mag_id, ctd_mag, context]
                        line = '{}\n'.format('\t'.join(val))
                        f.write(line)
    f.close()
