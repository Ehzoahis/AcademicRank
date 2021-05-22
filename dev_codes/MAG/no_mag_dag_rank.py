from gensim.models import Word2Vec
from heapq import nlargest
import requests
import json
import sys
from tqdm import tqdm

mag_db = './PaperReferences.txt'

def rank(fname, alpha=0.15):
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
    for line in tqdm(lines, total=len(lines)):
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
                sim[src] = 1
                # only perform once for each paper
                # PPR E term
                R[src] = alpha * sim[src]

        # add child to the set for the src         
        child_set.add(dst)

        # add dst to similarity dict if not in
        if dst not in sim.keys():
            sim[dst] = 1
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

    R = rank(mag_db)
    top_rank = top_ranks(R)
    write(o_fname, top_rank)