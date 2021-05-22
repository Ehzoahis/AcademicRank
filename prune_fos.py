# Filter out the FoS that are in CS keywords dataset

from sqlalchemy import create_engine
from tqdm import tqdm
from config import db_url, fos_fname, FOS_CNT

engine = create_engine(db_url)

tar_fn = './pruned_FoS.txt' # output file path

# Build the set of CS keywords with multiple words
def generate_kw_set(min_kw_freq=1):
    print('querying DB')
    q = ('select NORMALIZED_NAME'
         ' from keywords'
         ' where FREQUENCY>{}').format(min_kw_freq-1);

    tuples = engine.execute(q).fetchall()
    
    kw_set = set([kw[0] for kw in tuples if len(kw[0].split())>=2])
    print('{} keywords'.format(len(kw_set)))

    return kw_set

# For all the FOS in dataset, keep if and only if it is also in CS keyword dataset
if __name__=="__main__":
    kw_set = generate_kw_set()
    cnt = 0
    with open(fos_fname, 'r') as fr:
        with open(tar_fn, 'w') as fw:
            for i, line in tqdm(enumerate(fr), total=FOS_CNT):
                items = line.strip('\n').split('\t')
                fid = items[0]
                fn = items[2]
                if fn in kw_set:
                    line = '{}\n'.format('\t'.join([fid, fn]))
                    fw.write(line)
                    cnt += 1
    print('{} CS keywords'.format(cnt))