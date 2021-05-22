from tqdm import tqdm

EDGE_CNT = 1670074311 # tot edges
PAPER_CNT = 1154324291 # papers about CS

# 83k: 1670074311 -> 1662365938
#                 -> 1094935127
# mag: 1670074311 -> 1460507346

cspaper_db = './cspapers.txt'
mag_db = './PaperReferences.txt'
o_fname = './pruned_PR.txt'

# cs papers intersect edges
def build_cs_set():
    cs_paper = set()
    with open(cspaper_db, 'r') as fr:
        for i, line in tqdm(enumerate(fr), total=PAPER_CNT):
            items = line.strip('\n').split('\t')
            mid = items[0]
            cs_paper.add(mid)
    return cs_paper

def build_new_edge():
    cs_papers = build_cs_set()
    cnt = 0
    with open(o_fname, 'w') as fw:
        with open(mag_db, 'r') as fr:
            for i, line in tqdm(enumerate(fr), total=EDGE_CNT):
                src, dst = line.strip('\n').split('\t')
                if src not in cs_papers or dst not in cs_papers:
                    continue
                else:
                    fw.write(line)
                    cnt += 1
    print('{} edges are relavent to CS'.format(cnt))

if __name__=="__main__":
    build_new_edge()