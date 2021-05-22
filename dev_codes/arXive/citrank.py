import argparse
import sys
import os
from sqlalchemy import create_engine
from collections import defaultdict
import numpy as np

def query_db(db_url, keyword):
    print(db_url)
    engine = create_engine(db_url)

    print('querying DB')
    q = ('select CTD_MAG_ID, CTD_AID, CTG_AID, COUNT'
         ' from citation_keyword_net'
         ' where KEYWORD=\'{}\'').format(keyword);
    tuples = engine.execute(q).fetchall()
    return tuples

def build_rank_matrix(table, random_prob):
    aid2mid = dict()
    mid2aid = dict()
    aid_unique = set()
    cit_dict = defaultdict(lambda: defaultdict(int))
    dummy_aid = 0

    for item in table:
        ctd_mid = item[0]
        ctd_aid = item[1]
        ctg_aid = item[2]
        cnt = item[3]
        # if CTD_AID is empty, assign a dummy id to it
        if ctd_aid == 'None':
            if ctd_mid in mid2aid.keys():
                ctd_aid = mid2aid[ctd_mid]
            else:
                ctd_aid = str(dummy_aid)
                dummy_aid += 1
        if ctd_aid not in aid2mid.keys():
            aid2mid[ctd_aid] = ctd_mid
            mid2aid[ctd_mid] = ctd_aid
        aid_unique.add(ctd_aid)
        aid_unique.add(ctg_aid)
        cit_dict[ctg_aid][ctd_aid] = cnt

    aid_unique = list(aid_unique)
    len_unqie_aid = len(aid_unique)
    matrix = np.zeros((len_unqie_aid, len_unqie_aid))

    for i, ctg in enumerate(aid_unique):
        for j, ctd in enumerate(aid_unique):
            matrix[i,j] = cit_dict[ctg][ctd]
    norm_cnt = np.sum(matrix, axis=0)

    for idx, col in enumerate(norm_cnt):
        if col != 0:
            matrix[:,idx] = matrix[:, idx] / col
        else:
            matrix[:,idx] = 1/len_unqie_aid
    one = np.ones(matrix.shape)
    matrix = (1-random_prob) * matrix + (random_prob / len_unqie_aid) * one 

    return matrix, aid2mid, aid_unique

def citrank(matrix, thres):
    len_entry, _ = matrix.shape
    rank = np.random.rand(len_entry,1)
    rank = rank / np.sum(rank)
    rank_p = 0
    while np.linalg.norm(rank-rank_p) > thres:
        rank_p = rank
        rank = np.dot(matrix, rank)
        rank = rank / np.sum(rank)
    return rank.flatten()

def find_classical(rank, aid2mid, aid_unique):
    indices = np.argsort(rank)
    id_rank = []
    for idx in indices[::-1]:
        if aid_unique[idx] not in aid2mid.keys():
            id_rank.append([aid_unique[idx], rank[idx]])
        else:
            id_rank.append([aid2mid[aid_unique[idx]], rank[idx]])
    return id_rank
        
def write(fname, mid_rank):
    print('\nWriting result to file {}'.format(fname))
    with open(fname, 'w', encoding='utf-8') as f:
        for paper in mid_rank:
            mid = paper[0]
            rank = '{:.5f}'.format(paper[1])
            line = '{}\n'.format('\t'.join([mid, rank]))
            f.write(line)

def cal_rank(db_url, keyword, thres, random_prob, fname):
    table = query_db(db_url, keyword)
    matrix, aid2mid, aid_unique = build_rank_matrix(table, random_prob)
    rank = citrank(matrix, thres)
    mid_rank = find_classical(rank, aid2mid, aid_unique)
    write(fname, mid_rank)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Script for performing citation rank given a keyword.'))
    parser.add_argument(
        'db_url',
        help='database URL')
    parser.add_argument(
        'keyword',
        help='keyword to calculate rank on')
    parser.add_argument(
        '-f',
        '--fname',
        dest='fname',
        default='rank.txt',
        help='name of output file (defaults to rank.txt)')
    parser.add_argument(
        '-e',
        '--threshold',
        dest='thres',
        type=int,
        default=0.01,
        help='stop criteria for ranking algorithm')
    parser.add_argument(
        '-r',
        '--random_prob',
        dest='random_prob',
        type=int,
        default=0.1,
        help='probability of random surf')

    args = parser.parse_args()
    keyword = (args.keyword).replace('_', ' ')
    ret = cal_rank(args.db_url, keyword, args.thres, args.random_prob, args.fname)
    if not ret:
        sys.exit()