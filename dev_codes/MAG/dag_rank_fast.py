from gensim.models import Word2Vec
from heapq import nlargest
from sqlalchemy import create_engine
import sys
from tqdm import tqdm

LINE_CNT = 1670074311 # tot edges

word2vec = Word2Vec.load('./word2vec/word2vec.model')
mag_db = './PaperReferences.txt'

db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'
engine = create_engine(db_url)

def query_fos(db_url, fid):
    q = ('select fos'
         ' from fid2fos_cs'
         ' where fid={}').format(fid);

    tuples = engine.execute(q).fetchall()
    return tuples[0]

def query_fid(db_url, mid):
    q = ('select fid'
         ' from mid2fid'
         ' where mid={}').format(mid);

    tuples = engine.execute(q).fetchall()
    return tuples[0]

def MAG_get_fos(Id):
    print(Id)
    # Find all the field of study for given paper ID
    fid = query_fid(db_url, Id)
    fos = query_fos(db_url, fid)
    return set(fos)

def relativity(keyword, Id):
    # calculate the largest similarity between keyword and papers FoS
    # if paper has no fos provided or fos not in vocab, set similarity to 0
    # equivalent to ignore the paper.
    keyword = keyword.replace(' ', '_')

    fos = MAG_get_fos(Id)
    if fos == set():
        max_sim = 0
    else:
        max_sim = 0
        for paper_kw in fos:
            paper_kw = paper_kw.replace(' ', '_')
            if paper_kw not in word2vec.wv:
                sim = 0
            else:
                sim = word2vec.wv.similarity(keyword, paper_kw)
            max_sim = max(max_sim, sim)
    return max_sim

def rank(fname, keyword, alpha=0.15):
    R = dict()
    sim = dict()

    print("Read Edges...")
    with open(fname, 'r') as f:
        print('Read {} edges.'.format(LINE_CNT))

        print('Iterate through edges...')
        cnt = 0
        # init buffers
        old_node = ''
        child_set = dict()
        sum_j_child = 1
        for line in tqdm(f, total=LINE_CNT):
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
            if cnt % 1000 == 0:
                print('\rProcessed {:d} edges, {:.5f}% done'.format(cnt, cnt/LINE_CNT*100), end='')

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

    