from heapq import nlargest
import sys
from tqdm import tqdm
from collections import defaultdict
from sqlalchemy import create_engine

EDGE_CNT = 1094935127 # tot edges
PAPER_CNT = 355977380 # papers about CS

db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'
engine = create_engine(db_url)

mag_db = './pruned_PR_83k.txt'
mid2fos = './cspaper.txt'

def get_fid_dict():
    print('querying DB')
    q = ('select fid, fos'
        ' from fid2fos_83k');
    
    tuples = engine.execute(q).fetchall()
    fos2fid = dict()
    for item in tuples:
        fid = item[0]
        fos = item[1]
        fos2fid[fos] = fid
    return fos2fid

def generate_mid2fid():
    mid2fid = dict()
    with open(mid2fos, 'r') as f:
        for i, line in tqdm(enumerate(f), total=PAPER_CNT):
            item = line.strip('\n').split('\t')
            mid = item[0]
            fid = item[2]
            mid2fid[mid] = fid
    return mid2fid

def rank(mid2fid, fos2fid, fname, keyword):
    R = defaultdict(int)

    print("Read Edges...")
    with open(fname, 'r') as f:
        print('Read {} edges.'.format(EDGE_CNT))

        print('Iterate through edges...')

        for i, line in tqdm(enumerate(f), total=EDGE_CNT):
            _, dst = line.strip('\n').split('\t')

            if mid2fid[dst] == fos2fid[keyword.replace('_', ' ')]:
                R[dst] += 1
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

    mid2fid = generate_mid2fid()
    fos2fid = get_fid_dict()
    for keyword in keywords:
        o_fname = keyword+'_83k_cont.txt'

        R = rank(mid2fid, fos2fid, mag_db, keyword)
        top_rank = top_ranks(R)
        write(o_fname, top_rank)

    