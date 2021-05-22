from sqlalchemy import create_engine
from tqdm import tqdm
from gensim.models import Word2Vec
import sys
import numpy as np

# FoS uniintersecton cs_keywords
o_fname = './kw_sim_set.txt' # fid -> sim
db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'
engine = create_engine(db_url)

word2vec = Word2Vec.load('./word2vec/word2vec.model')

def get_fid(kw):
    print('querying DB')
    q = ('select fid, fos'
        ' from fid2fos_83k'
        ' where fos=\'{}\'').format(kw.replace('_', ' '));
    
    tuples = engine.execute(q).fetchall()
    return tuples[0][0]

def generate_fid_dict():
    fid_dict = dict()

    print('querying DB')
    q = ('select fid, fos'
        ' from fid2fos_83k');

    tuples = engine.execute(q).fetchall()
    for item in tuples:
        fid = item[0]
        fos = item[1]
        fid_dict[fid] = fos
    print('{} keywords'.format(len(fid_dict)))
    return fid_dict

def cal_sim(kw):
    fid_dict = generate_fid_dict()
    if ' '.join(kw.split('_')) not in fid_dict.values():
        print('BAD KEYWORD')
    fid_sim_dict = dict()
    good_cnt = 0
    bad_cnt = 0
    with open(o_fname, 'w') as f:
        for i, fid in tqdm(enumerate(fid_dict.keys()), total=len(fid_dict)):
            fos = fid_dict[fid]
            fos = '_'.join(fos.split(' '))
            if fos in word2vec.wv:
                sim = word2vec.wv.similarity(kw, fos)
                good_cnt += 1
            else:
                sim = 0.001
                # sub_fos = fos.split('_')
                # sub_sim = list()
                # for word in sub_fos:
                #     if word in word2vec.wv:
                #         sub_sim.append(word2vec.wv.similarity(kw, word))
                #     else:
                #         sub_sim.append(0)
                # sim = np.mean(sub_sim)
                # if sim != 0:
                #     bad_cnt += 1
            fid_sim_dict[fid] = sim
            line = '{}\n'.format('\t'.join([fid, str(sim)]))
            f.write(line)
    print('{}/{} valid keywords similarity calculated.'.format(good_cnt, len(fid_dict)))
    print('{}/{} decomposited keywords similarity calculated.'.format(bad_cnt, len(fid_dict)))

    return fid_sim_dict

if __name__=="__main__":
    kw = sys.argv[1]
    _ = cal_sim(kw)