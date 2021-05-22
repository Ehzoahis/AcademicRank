import networkx as nx
import gensim
from heapq import nlargest
from sqlalchemy import create_engine
import requests
import json
import sys

CONFIG = './CONFIG'

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

def read_config():
    with open(CONFIG, 'r') as f:
        lines = f.readlines()
        line = iter(lines)
        db_url = next(line).strip('\n')
        mag_ds = next(line).strip('\n')
        wv_model = next(line).strip('\n')
        
    return db_url, mag_ds, wv_model

def kw_search(sent, kw_set):
    contained_kw = []
    sent += ' '
    for kw in kw_set: 
        if ' '+kw+' ' in sent:
            contained_kw.append(kw)
    return set(contained_kw)

def generate_kw_set(db_url, min_kw_freq=1):
    print(db_url)
    engine = create_engine(db_url)

    print('querying DB')
    q = ('select NORMALIZED_NAME'
         ' from keywords'
         ' where FREQUENCY>{}').format(min_kw_freq-1);

    tuples = engine.execute(q).fetchall()
    
    kw_set = set([kw[0] for kw in tuples])
    print('{} keywords'.format(len(kw_set)))

    return kw_set

# can build edge than assign weight (O(E) + nO(V))
def build_graph(fname, keyword, kws, word2vec):
    keyword = keyword.replace(' ', '_')
    G = nx.Graph()
    personalize = dict()
    with open(fname, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        edge = line.split('\t')
        src = edge[0]
        dst = edge[1]
        try:
            src_kw = MAG_get_fos(src).union(kws)
        except:
            continue
        try:
            dst_kw = MAG_get_fos(dst).union(kws)
        except:
            continue

        if src_kw and (src not in personalize.keys()):
            s_sim = [word2vec.wv.similarity(kw_p.replace(' ', '_'), keyword) for kw_p in src_kw if kw_p in word2vec.wv]
            personalize[src] = max(s_sim)

        if dst_kw and (dst not in personalize.keys()):
            d_sim = [word2vec.wv.similarity(kw_d.replace(' ', '_'), keyword) for kw_d in dst_kw if kw_d in word2vec.wv]
            personalize[dst] = max(d_sim)

        if src_kw and dst_kw:
            G.add_weighted_edges_from([(src, dst, personalize[dst])])
    
    return G, personalize

# O(E)
def normalize_graph(G, personalize):
    raw_tot = sum(personalize.values())
    for key in personalize.keys():
        personalize[key] /= raw_tot
    
    for node in G.nodes:
        edges = G.out_edges(node)
        out_tot = sum([G.edges[src, dst]['weight'] for src, dst in edges])
        for src, dst in edges:
            G.edges[src, dst]['weight'] /= out_tot
    
    return G, personalize

def pagerank(G, personalize, N=10):
    pr_dict = nx.pagerank(G, alpha=1.0, personalization=personalize, nstart=personalize, dangling=personalize)
    key_list = nlargest(N, pr_dict, key = pr_dict.get)
    key_rank = list()
    for key in key_list:
        key_rank.append((key, pr_dict[key]))
    return key_rank

def write(fname, key_rank):
    with open(fname, 'w') as f:
        for key, rank in key_rank:
            line = '{}\n'.format('\t'.join([key, str(rank)]))
            f.write(line)

if __name__ == "__main__":
    keyword = sys.argv[1]
    
    db_url, mag_ds, wv_model = read_config()
    word2vec = gensim.models.Word2Vec.load(wv_model)
    o_fname = keyword+'.txt'

    kws = generate_kw_set(db_url)
    G, personalize = build_graph(mag_ds, keyword, kws, word2vec)
    G, personalize = normalize_graph(G, personalize)
    pr = pagerank(G, personalize)
    write(o_fname, pr)


