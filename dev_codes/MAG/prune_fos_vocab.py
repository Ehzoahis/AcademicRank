from sqlalchemy import create_engine
from tqdm import tqdm
from gensim.models import Word2Vec
import sys
import numpy as np

LINE_CNT = 741671

db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'
engine = create_engine(db_url)

# FoS intersect cs_keywords
fos_fn = './FieldsOfStudy.txt' # fid -> fos 
tar_fn = './pruned_FoS_vocab.txt' # fid -> fos, cs only
word2vec = Word2Vec.load('./word2vec/word2vec.model')

def generate_kw_set(min_kw_freq=1):
    print('querying DB')
    q = ('select NORMALIZED_NAME'
         ' from keywords'
         ' where FREQUENCY>{}').format(min_kw_freq-1);

    tuples = engine.execute(q).fetchall()
    
    kw_set = set([kw[0] for kw in tuples if len(kw[0].split())>=2])
    print('{} keywords'.format(len(kw_set)))

    return kw_set

if __name__=="__main__":
    kw_set = generate_kw_set()
    cnt = 0
    with open(fos_fn, 'r') as fr:
        with open(tar_fn, 'w') as fw:
            for i, line in tqdm(enumerate(fr), total=LINE_CNT):
                items = line.strip('\n').split('\t')
                fid = items[0]
                fn = items[2]
                if '_'.join(fn.split()) not in word2vec.wv:
                    continue
                if fn in kw_set:
                    line = '{}\n'.format('\t'.join([fid, fn]))
                    fw.write(line)
                    cnt += 1
    print('{} CS keywords'.format(cnt))