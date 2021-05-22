from sqlalchemy import create_engine

CONFIG = './CONFIG' # db-url

def read_config():
    with open(CONFIG, 'r') as f:
        db_url = f.readline()
    return db_url

def kw_search(sent, kw_set):
    contained_kw = []
    sent += ' '
    for kw in kw_set: 
        if ' '+kw+' ' in sent:
            contained_kw.append(kw)
    return set(contained_kw)

def generate_kw_set(min_kw_freq=1):
    db_url = read_config()
    print(db_url)
    engine = create_engine(db_url)

    print('querying DB')
    q = ('select NORMALIZED_NAME'
         ' from keywords'
         ' where FREQUENCY>{}').format(min_kw_freq-1);

    tuples = engine.execute(q).fetchall()
    
    kw_set = set([kw[0] for kw in tuples])
    print('{} keywords'.format(len(kw_set)))

    return kw_set
