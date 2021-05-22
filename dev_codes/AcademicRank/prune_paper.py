from sqlalchemy import create_engine
from tqdm import tqdm

LINES_CNT = 1403999324

# mag: 1403999324 -> 1154324291
#                 -> 563910034
# 83k: 1403999324 -> 777348548
#                 -> 355977380

# cs_fid intersect fid
mid2fid_fname = './PFoS.txt' # mid -> fid
o_fname = './cspaper.txt' # mid -> fos, fid cs only
db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'
engine = create_engine(db_url)

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

def generate_mid2fos():
    fid_dict = generate_fid_dict()
    cnt = 0
    with open(o_fname, 'w') as fw:
        with open(mid2fid_fname, 'r') as fr:
            print('file opened')
            for i, line in tqdm(enumerate(fr), total=LINES_CNT):
                items = line.strip('\n').split('\t')
                mid = items[0]
                fid = items[1]
                if fid in fid_dict.keys():
                    fos = fid_dict[fid]
                    line= '{}\n'.format('\t'.join([mid, fos, fid]))
                    fw.write(line)
                    cnt += 1
    print('{} papers about CS'.format(cnt))

if __name__ == "__main__":
    generate_mid2fos()