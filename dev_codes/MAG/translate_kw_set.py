from sqlalchemy import create_engine
from tqdm import tqdm
import sys

db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'
engine = create_engine(db_url)

def generate_kw_set(start_row=0, row_num=-1):
    print('querying DB')
    if row_num < 0:
        q = ('select NORMALIZED_NAME'
            ' from keywords');
    else:
        q = ('select NORMALIZED_NAME'
            ' from keywords'
            ' limit {}, {}').format(start_row, row_num);

    tuples = engine.execute(q).fetchall()
    kw_set = set([kw[0] for kw in tuples])
    print('{} keywords'.format(len(kw_set)))
    return kw_set

def query_fid(fos):
    q = ('select fid'
         ' from fid2fos'
         ' where fos=\'{}\'').format(fos);
    tuples = engine.execute(q).fetchall()
    if tuples != list():
        return tuples[0][0]
    else:
        return None

if __name__=="__main__":
    start_row = int(sys.argv[1])
    row_num = int(sys.argv[2])
    idx = sys.argv[3]

    o_fname = './fos2fid/fos2fid/fos2fid_{}.txt'.format(idx)
    non_exits_fnmae = './fos2fid/failed/failed_{}.txt'.format(idx)

    kw_set = generate_kw_set(start_row=start_row, row_num=row_num)
    cnt = 0
    with open(o_fname, 'w') as f:
        with open(non_exits_fnmae, 'w') as ff:
            for i, kw in tqdm(enumerate(kw_set), total=len(kw_set)):
                fid = query_fid(kw)
                if not fid:
                    ff.write('{}\n'.format(kw))
                    continue
                line = '{}\n'.format('\t'.join([kw, fid]))
                f.write(line)
                cnt += 1
    print('{} FId translated'.format(cnt))