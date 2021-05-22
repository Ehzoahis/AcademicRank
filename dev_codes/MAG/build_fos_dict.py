from collections import defaultdict
from sqlalchemy import create_engine

fid2fos_fname = '/scratch/pritom/mag-2020-09-14/advanced/FieldsOfStudy.txt'
mid2fid_fname = '/scratch/pritom/mag-2020-09-14/advanced/PaperFieldsOfStudy.txt'
o_fname = './mid2fos.txt'

db_url = 'mysql+mysqlconnector://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'

fid2fos = dict()
mid2fos = defaultdict(list)

def query_fos(db_url, fid):
    engine = create_engine(db_url)

    q = ('select fos'
         ' from fid2fos'
         ' where fid={}').format(fid);

    tuples = engine.execute(q).fetchall()
    return tuples[0]

def query_fid(db_url, mid):
    engine = create_engine(db_url)

    q = ('select fid'
         ' from mid2fid'
         ' where mid={}').format(mid);

    tuples = engine.execute(q).fetchall()
    return tuples[0]

if __name__ == "__main__":
    print('\nread Paper_FoS.txt')
    with open(o_fname, 'w') as fw:
        with open(mid2fid_fname,'r') as fr:
            lines = fr.readlines()
            tot = len(lines)
            cnt = 0
            print('{} lines to read'.format(tot))
            for line in lines:
                cnt += 1
                if cnt % 1000 == 0:
                    print('\r{}/{} lines read'.format(cnt, tot), end='')
                items = line.split('\t')
                mid = items[0]
                fid = items[1]
                fos = fid2fos[fid]
                line= '{}\n'.format('\t'.join([mid, fos]))
                fw.write(line)


