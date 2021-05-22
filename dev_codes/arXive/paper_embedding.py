import argparse
import sys
import os
from sqlalchemy import create_engine
from collections import defaultdict
import numpy as np

def query_db_aid(db_url, ctd_aid):
    print(db_url)
    engine = create_engine(db_url)

    print('querying DB')
    q = ('select KEYWORD, COUNT'
         ' from citation_keyword_net'
         ' where CTG_AID=\'{}\'').format(ctd_aid);
    tuples = engine.execute(q).fetchall()
    return tuples

def query_db_kw(db_url, keyword):
    print(db_url)
    engine = create_engine(db_url)

    print('querying DB')
    q = ('select CTG_AID, COUNT'
         ' from citation_keyword_net'
         ' where KEYWORD=\'{}\'').format(keyword);
    tuples = engine.execute(q).fetchall()
    return tuples

def find_top_aid(table, top_n=4):
    aid_cnt = defaultdict(int)
    dtype = [('cnt', int), ('aid', object)]
    ordered_aid = []
    for item in table:
        aid = item[0]
        cnt = item[1]
        aid_cnt[aid] += cnt

    for aid in aid_cnt.keys():
        ordered_aid.append((aid_cnt[aid], aid))
    
    ordered_aid = np.array(ordered_aid, dtype=dtype)
    vector = np.sort(ordered_aid, order='cnt')
    return np.flip(vector[-top_n:])

def generate_kw_cnt(table):
    kw_cnt = defaultdict(int)
    for item in table:
        kw = item[0]
        cnt = item[1]
        kw_cnt[kw] += cnt
    return kw_cnt
    
def cal_correlation(tar, obj):
    # other way of measure similarity?
    # e.g. cosine
    tar = np.array(tar)
    obj = np.array(obj)
    tar_cent = tar - np.mean(tar)
    obj_cent = obj - np.mean(obj)
    numer = np.sum(tar_cent*obj_cent)
    denom = np.sqrt(np.sum(tar_cent**2))*np.sqrt(np.sum(obj_cent**2))
    return numer/denom

def cal_cosine_sim(tar, obj):
    tar = np.array(tar)
    obj = np.array(obj)
    numer = np.sum(np.dot(tar, obj))
    denom = np.linalg.norm(tar)*np.linalg.norm(obj)
    return numer/denom

def find_similar(db_url, keyword, top_n_paper, sim_measure='correlation'):
    assert sim_measure in {'correlation', 'cosine'}
    tar_keyword_table = query_db_kw(db_url, keyword)
    paper_embed = find_top_aid(tar_keyword_table, top_n_paper)
    paper_kw_cnt = defaultdict(lambda: defaultdict(int))
    keyword_list = set()
    kw_sim = dict()

    print('Embed th the keywords in {} papers'.format(len(paper_embed)))

    for paper_tup in paper_embed:
        paper = str(paper_tup[1])
        keyword_table = query_db_aid(db_url, paper)
        kw_cnt = generate_kw_cnt(keyword_table)
        paper_kw_cnt[paper] = kw_cnt
        kw = set(kw_cnt.keys())
        keyword_list = keyword_list.union(kw)
    keyword_list = list(keyword_list)

    # F
    embed = np.zeros((len(keyword_list), len(paper_embed)))
    kw2idx = dict()

    for i, k in enumerate(keyword_list):
        kw2idx[k] = i
        for j, a_tup in enumerate(paper_embed):
            a = str(a_tup[1])
            embed[i, j] = paper_kw_cnt[a][k]

    tar_vec = embed[kw2idx[keyword]]
    for candi_kw in keyword_list:
        candi_idx = kw2idx[candi_kw]
        obj_vec = embed[candi_idx]
        if sim_measure == 'correlation':
            kw_sim[candi_kw] = cal_correlation(tar_vec, obj_vec)
        elif sim_measure == 'cosine':
            kw_sim[candi_kw] = cal_cosine_sim(tar_vec, obj_vec)

    return kw_sim

def order_kw(kw_sim, top_n=10):
    # top_n = -1 for all kws
    dtype = [('kw', object), ('sim', float)]
    kw_rank = []
    for kw in kw_sim.keys():
        kw_rank.append((kw, kw_sim[kw]))

    kw_rank = np.array(kw_rank, dtype=dtype)
    sim_kws = np.sort(kw_rank, order='sim')[-(top_n+1):]
    return np.flip(sim_kws)

def write(fname, sim_kws):
    print('\nWriting result to file {}'.format(fname))
    with open(fname, 'w', encoding='utf-8') as f:
        for tup in sim_kws:
            kw = str(tup[0])
            sim = '{:.5f}'.format(tup[1])
            line = '{}\n'.format('\t'.join([kw, sim]))
            f.write(line)

def keyword_similarity(db_url, keyword, top_n_paper, top_n_kw, fname, sim_measure='correlation'):
    assert sim_measure in {'correlation', 'cosine'}
    kw_sim_dict = find_similar(db_url, keyword, top_n_paper, sim_measure)
    kw_sim_list = order_kw(kw_sim_dict, top_n_kw)
    write(fname, kw_sim_list)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Script for performing calculating the similarity of the keywords.'))
    parser.add_argument(
        'db_url',
        help='database URL')
    parser.add_argument(
        'keyword',
        help='keyword to calculate similarity on')
    parser.add_argument(
        '-f',
        '--fname',
        dest='fname',
        default='similarity.txt',
        help='name of output file (defaults to similarity.txt)')
    parser.add_argument(
        '-p',
        '--paper_num',
        dest='top_n_paper',
        type=int,
        default=0,
        help='using the top n papers as embedding space')
    parser.add_argument(
        '-n',
        '--kw_num',
        dest='top_n_kw',
        type=int,
        default=-1,
        help='return the top n similar keywords')
    parser.add_argument(
        '-s',
        '--similarity',
        dest='sim',
        type=str,
        default='correlation',
        help='pick method of calculation similarity')

    args = parser.parse_args()
    keyword = (args.keyword).replace('_', ' ')
    ret = keyword_similarity(args.db_url, keyword, args.top_n_paper, args.top_n_kw, args.fname, args.sim)
    if not ret:
        sys.exit()
    

