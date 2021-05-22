mag_db = './PaperReferences.txt'
fos_db = './PFoS.txt'

db_url = 'mysql+pymysql://haozhes3:hank20si@owl2.cs.illinois.edu/haozhes3_refs?charset=utf8'

def query_fos(db_url, fid):
    engine = create_engine(db_url)

    q = ('select fos'
         ' from fid2fos'
         ' where fid={}').format(fid);

    tuples = engine.execute(q).fetchall()
    return tuples[0]
