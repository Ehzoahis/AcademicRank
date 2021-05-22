# Calculate the similarity of target keyword and all the filted CS FoS

from sqlalchemy import create_engine
from tqdm import tqdm
from gensim.models import Word2Vec
import sys
from config import db_url

o_fname = './kw_sim_set.txt' # fid -> sim

engine = create_engine(db_url)
word2vec = Word2Vec.load('./word2vec/word2vec.model')

# Translate FoS into FId
def get_fid(kw):
    print('querying DB')
    q = ('select fid, fos'
        ' from fid2fos_cs'
        ' where fos=\'{}\'').format(kw.replace('_', ' '));
    
    tuples = engine.execute(q).fetchall()
    return tuples[0][0]

# Build a dictionary that can translate FId to FoS
def generate_fid_dict():
    fid_dict = dict()

    print('querying DB')
    q = ('select fid, fos'
        ' from fid2fos_cs');

    tuples = engine.execute(q).fetchall()
    for item in tuples:
        fid = item[0]
        fos = item[1]
        fid_dict[fid] = fos
    print('{} keywords'.format(len(fid_dict)))
    return fid_dict

# Calculate the similarity between the serching keyword with all the CS keywords in dataset
def cal_sim(kw):
    fid_dict = generate_fid_dict()
    # If the target keyword is not in word2vec vocab and thus similarity cannot be calculated, halt the program
    if ' '.join(kw.split('_')) not in fid_dict.values():
        print('BAD KEYWORD')
        sys.exit()
    fid_sim_dict = dict()
    good_cnt = 0
    with open(o_fname, 'w') as f:
        for i, fid in tqdm(enumerate(fid_dict.keys()), total=len(fid_dict)):
            fos = fid_dict[fid]
            fos = '_'.join(fos.split(' '))
            if fos in word2vec.wv:
                sim = word2vec.wv.similarity(kw, fos)
                good_cnt += 1
            else:
                # TODO: Better simiarity calculation is needed here
                sim = 0.001 # dummy similarity
            fid_sim_dict[fid] = sim
            line = '{}\n'.format('\t'.join([fid, str(sim)]))
            f.write(line)
    print('{}/{} valid keywords similarity calculated.'.format(good_cnt, len(fid_dict)))
    return fid_sim_dict

if __name__=="__main__":
    kw = sys.argv[1]
    _ = cal_sim(kw)