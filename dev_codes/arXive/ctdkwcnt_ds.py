import argparse
import sys
import os
import re
import string
from sqlalchemy import create_engine
from nltk import tokenize
from collections import defaultdict

CITE_PATT = re.compile((r'\{\{cite:([0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}'
                         '-[89AB][0-9A-F]{3}-[0-9A-F]{12})\}\}'), re.I)
RE_WHITESPACE = re.compile(r'[\s]+', re.UNICODE)
RE_PUNCT = re.compile('[%s]' % re.escape(string.punctuation), re.UNICODE)
RE_WORD = re.compile('[^\s%s]+' % re.escape(string.punctuation), re.UNICODE)
tokenizer = tokenize.load('tokenizers/punkt/english.pickle')
abbreviation = ['al', 'fig', 'e.g', 'i.e', 'eq', 'cf', 'ref', 'refs']
for abbr in abbreviation:
    tokenizer._params.abbrev_types.add(abbr)

def kw_search(sent, kw_set):
    contained_kw = []
    sent += ' '
    for kw in kw_set: 
        if ' '+kw+' ' in sent:
            contained_kw.append(kw)
    return set(contained_kw)

def generate_kw_set(in_dir, db_uri, min_kw_freq):
#     in_dir = '.\\unarXive-2020\papers'
    if not db_uri:
        db_path = os.path.join(in_dir, 'refs.db')
        db_uri = 'sqlite:///{}'.format(os.path.abspath(db_path))
    print(db_uri)
    engine = create_engine(db_uri)

    print('querying DB')
    q = ('select NORMALIZED_NAME'
         ' from keywords'
         ' where FREQUENCY>{}').format(min_kw_freq-1);

    tuples = engine.execute(q).fetchall()
    
    kw_set = set([kw[0] for kw in tuples if len(kw[0].split())>=2])
    print('{} keywords'.format(len(kw_set)))

    return kw_set

def generate_mag_kw_cnt(in_dir, db_uri, kw_set, output_file):
    if not db_uri:
        db_path = os.path.join(in_dir, 'refs.db')
        db_uri = 'sqlite:///{}'.format(os.path.abspath(db_path))
    print(db_uri)
    engine = create_engine(db_uri)

    print('querying DB')

    q = ('select ctd_mag_id, context'
         ' from ctd_context');

    tuples = engine.execute(q).fetchall()
    print('going through {} papers'.format(len(tuples)))

    tuple_idx = 0
    ctd_kw_cnt = defaultdict(lambda: defaultdict(int))
    
    while tuple_idx < len(tuples):
        if tuple_idx % 1000 == 0:
            print('\r{}/{}'.format(tuple_idx, len(tuples)), end='')
            
        ctd_mag_id = tuples[tuple_idx][0]
        context = tuples[tuple_idx][1]

        kws = kw_search(context, kw_set)
        for kw in kws:
            ctd_kw_cnt[ctd_mag_id][kw]+=1
        tuple_idx += 1

    vals = []
    for mag in ctd_kw_cnt.keys():
        for kw in ctd_kw_cnt[mag].keys():
            vals.append([str(mag), str(kw), str(ctd_kw_cnt[mag][kw])])
    
    print('\nwriting contexts to file {}'.format(output_file))
    with open(output_file, 'w', encoding='utf-8') as f:
        for idx, val in enumerate(vals):
            line = '{}\n'.format('\t'.join(val))
            if idx % 1000 == 0:
                print("\r{}/{}".format(idx, len(vals)), end='')
            f.write(line)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Script for extracting '
        'citation contexts from the unarXive data set.'))
    parser.add_argument(
        'in_dir',
        help='path of the directory in which the plain text files are stored')
    parser.add_argument(
        '-b',
        '--db_uri',
        dest='db_uri',
        default=None,
        help='database URI (defaults to sqlite:///<in_dir>/refs.db)')
    parser.add_argument(
        '-f',
        '--output_file',
        dest='output_file',
        default='items.csv',
        help='name of output file (defaults to items.csv)')
    parser.add_argument(
        '-k',
        '--min_keyword_freq',
        dest='min_kw_freq',
        type=int,
        default=1,
        help=('only use a sample of <sample_size> cited documents (all are '
              'used if argument is not given)'))

    args = parser.parse_args()
    kw_set = generate_kw_set(args.in_dir, args.db_uri, args.min_kw_freq)
    ret = generate_mag_kw_cnt(args.in_dir, args.db_uri, kw_set, args.output_file)
    if not ret:
        sys.exit()



