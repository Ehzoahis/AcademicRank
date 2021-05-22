# Prune the number of papers given the pruned keyword set.
# Prune the number of edges if both citing and cited paper are
# in the pruned paper set.

from sqlalchemy import create_engine
from tqdm import tqdm
from config import db_url, mid2fid_fname, mag_db
from config import cspaper_fname, csedges_fname
from config import PAPERFID_CNT, EDGE_CNT

engine = create_engine(db_url)

# Build the dictionary for translating FOS to FId
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

# Prune the papers if not exists in the pruned keyword dataset
# Output the pruned paper-FId pair set to target file
# Return a set of unique cs papers
def generate_mid2fos():
    fid_dict = generate_fid_dict()
    cs_papers = set()
    cnt = 0
    with open(cspaper_fname, 'w') as fw:
        with open(mid2fid_fname, 'r') as fr:
            print('file opened')
            for i, line in tqdm(enumerate(fr), total=PAPERFID_CNT):
                items = line.strip('\n').split('\t')
                mid = items[0]
                fid = items[1]
                if fid in fid_dict.keys():
                    fos = fid_dict[fid]
                    line= '{}\n'.format('\t'.join([mid, fos, fid]))
                    fw.write(line)
                    cs_papers.add(mid)
    print('{} papers about CS'.format(cnt))
    return cs_papers

# Prune the edges if either node is not in the pruned paper set
def build_new_edge(cs_papers):
    cnt = 0
    with open(csedges_fname, 'w') as fw:
        with open(mag_db, 'r') as fr:
            for i, line in tqdm(enumerate(fr), total=EDGE_CNT):
                src, dst = line.strip('\n').split('\t')
                if src not in cs_papers or dst not in cs_papers:
                    continue
                else:
                    fw.write(line)
                    cnt += 1
    print('{} edges are relavent to CS'.format(cnt))

if __name__ == "__main__":
    cs_papers = generate_mid2fos()
    build_new_edge(cs_papers)