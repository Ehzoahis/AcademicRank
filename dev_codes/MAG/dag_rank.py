from gensim.models import Word2Vec
from heapq import nlargest
import requests
import json
import sys

HEADERS = {"Ocp-Apim-Subscription-Key": "c9ed15c311b6478bbf1feea30350432a"} # Specific to Haozhe Si
QUERYSTRING = {"mode":"json%0A"}
PAYLOAD = "{}"
sup_key="c9ed15c311b6478bbf1feea30350432a"
COUNT = str(1) # dummy Count, no effect here
DUMMY_FOS = 'dummy' # dummy fos
word2vec = Word2Vec.load('./word2vec/word2vec.model')
mag_db = './PaperReferences.txt'

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
        if 'F' in entity:
            fdict = entity['F']
            for fn in fdict:
                fos = fn['FN']
                pfos_list.append(fos)
    return set(pfos_list)

def relativity(keyword, Id):
    # calculate the largest similarity between keyword and papers FoS
    keyword = keyword.replace(' ', '_')

    fos = MAG_get_fos(Id)
    if fos == set():
        max_sim = word2vec.wv.similarity(keyword, DUMMY_FOS)
    else:
        max_sim = 0
        for paper_kw in fos:
            paper_kw = paper_kw.replace(' ', '_')
            if paper_kw not in word2vec.wv:
                sim = word2vec.wv.similarity(keyword, DUMMY_FOS)
            else:
                sim = sim = word2vec.wv.similarity(keyword, paper_kw)
            max_sim = max(max_sim, sim)
    return max_sim

def rank(fname, keyword, alpha=0.15):
    R = dict()
    sim = dict()

    print("Read Edges...")
    with open(fname, 'r') as f:
        lines = f.readlines()
    print('Read {} edges.'.format(len(lines)))

    print('Iterate through edges...')
    cnt = 0
    # init buffers
    old_node = ''
    child_set = dict()
    sum_j_child = 1
    for line in lines:
        cnt += 1
        src, dst = line.strip('\n').split('\t')
        # the edge file is in order of citing edge
        # changing src means moving to new citing paper
        if src != old_node:
            # build the rank for the previous src first
            if child_set != set():
                for dst in child_set:
                    R[dst] += sim[dst]*sim[old_node]/sum_j_child
            
            # clear all the buffers
            old_node = src
            child_set = set()
            sum_j_child = 0

            # add src to similarity dict if not in
            if src not in sim.keys():
                sim[src] = relativity(keyword, src)
                # only perform once for each paper
                # PPR E term
                R[src] = alpha * sim[src]

        # add child to the set for the src         
        child_set.add(dst)

        # add dst to similarity dict if not in
        if dst not in sim.keys():
            sim[dst] = relativity(keyword, dst)
            # only perform once for each paper
            # PPR E term
            R[dst] = alpha * sim[dst]
        
        # accumulate normalization factor
        sum_j_child += sim[dst]

        # show progress
        # if cnt % 1000 == 0:
        #     print('\rProcessed {:d} edges, {:.5f}% done'.format(cnt, cnt/len(lines)*100), end='')

    # build the rank for the last paper
    if child_set != set():
        for dst in child_set:
            R[dst] += sim[dst]*sim[old_node]/sum_j_child

    return R

def top_ranks(R, top_k=10):
    key_list = nlargest(top_k, R, key = R.get)
    key_rank = list()
    for key in key_list:
        key_rank.append((key, R[key]))
    return key_rank

def write(fname, key_rank):
    with open(fname, 'w') as f:
        for key, rank in key_rank:
            line = '{}\n'.format('\t'.join([key, str(rank)]))
            f.write(line)

if __name__ == "__main__":
    keyword = sys.argv[1]

    o_fname = keyword+'.txt'

    R = rank(mag_db, keyword)
    top_rank = top_ranks(R)
    write(o_fname, top_rank)

    