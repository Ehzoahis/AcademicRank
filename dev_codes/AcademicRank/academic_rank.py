from heapq import nlargest
import sys
from tqdm import tqdm
from kw_sim_dict import *
from collections import defaultdict

EDGE_CNT = 1094935127 # tot edges
PAPER_CNT = 355977380 # papers about CS

mag_db = './pruned_PR_83k.txt'
mid2fos = './cspaper.txt'

def generate_mid2fid(fid_sim):
    mid2fid = dict()
    max_sim = defaultdict(lambda:-1)
    with open(mid2fos, 'r') as f:
        for i, line in tqdm(enumerate(f), total=PAPER_CNT):
            item = line.strip('\n').split('\t')
            mid = item[0]
            fid = item[2]
            if fid_sim[fid] > max_sim[mid]:
                mid2fid[mid] = fid
                max_sim[mid] = fid_sim[fid]
    return mid2fid

def rank(fname, keyword, kw_fid, alpha=0.15):
    R = dict()
    fid_sim = cal_sim(keyword)
    mid2fid = generate_mid2fid(fid_sim)

    print("Read Edges...")
    with open(fname, 'r') as f:
        print('Read {} edges.'.format(EDGE_CNT))

        print('Iterate through edges...')
        cnt = 0
        # init buffers
        old_node = ''
        child_set = set()
        sum_j_child = 0
        for i, line in tqdm(enumerate(f), total=EDGE_CNT):
            cnt += 1
            src, dst = line.strip('\n').split('\t')
            # the edge file is in order of citing edge
            # changing src means moving to new citing paper
            if src != old_node:
                # build the rank for the previous src first
                # TODO: zero prob means even dist or no dist?
                if child_set != set():
                    for dst in child_set:
                        if kw_fid in mid2fid[dst]:
                            R[dst] += fid_sim[mid2fid[dst]]*fid_sim[mid2fid[old_node]]/sum_j_child

                # clear all the buffers
                old_node = src
                child_set = set()
                sum_j_child = 0

                # only perform once for each paper 
                if src not in R.keys() and mid2fid[src] == kw_fid:
                    R[src] = 0

            # add child to the set for the src         
            child_set.add(dst)

            # only perform once for each paper
            if dst not in R.keys() and mid2fid[dst] == kw_fid:
                R[dst] = 0
            
            # accumulate normalization factor
            sum_j_child += fid_sim[mid2fid[dst]]

        # build the rank for the last paper
        if child_set != set():
            for dst in child_set:
                R[dst] += fid_sim[mid2fid[dst]]*fid_sim[mid2fid[old_node]]/sum_j_child

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
    keywords = sys.argv[1]
    keywords = keywords.split(',')

    for keyword in keywords:
        o_fname = keyword+'_83k_cs.txt'
        kw_fid = get_fid(keyword)
        R = rank(mag_db, keyword, kw_fid)
        top_rank = top_ranks(R)
        write(o_fname, top_rank)

    
