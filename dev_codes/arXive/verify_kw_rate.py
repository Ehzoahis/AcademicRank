import argparse
import sys
import os
import re
import string
import numpy as np
from sqlalchemy import create_engine
from collections import defaultdict

def generate_from_kw(in_dir, db_uri):
    if not db_uri:
        db_path = os.path.join(in_dir, 'refs.db')
        db_uri = 'sqlite:///{}'.format(os.path.abspath(db_path))
    print(db_uri)
    engine = create_engine(db_uri)

    print('querying DB')
    q = 'select distinct MAG_ID, CTG_AID from ctd_kw_ctg_cnt where Keyword!=\'is a\''

    tuples = engine.execute(q).fetchall()
    
    ctg_cnt = defaultdict(int)
    for pair in tuples:
        ctg_cnt[pair[1]] += 1
    return ctg_cnt

def generate_from_bibitem(in_dir, db_uri):
    if not db_uri:
        db_path = os.path.join(in_dir, 'refs.db')
        db_uri = 'sqlite:///{}'.format(os.path.abspath(db_path))
    print(db_uri)
    engine = create_engine(db_uri)

    print('querying DB')
    q = 'select distinct CTG_AID, CTD_MAG_ID from ctd_context'

    tuples = engine.execute(q).fetchall()
    
    ctg_cnt = defaultdict(int)
    for pair in tuples:
        ctg_cnt[pair[0]] += 1
    return ctg_cnt

def generate_ratio(in_dir, db_uri, output_file):
    kw_count = generate_from_kw(in_dir, db_uri)
    bib_count = generate_from_bibitem(in_dir, db_uri)

    kw_ratio = []
    tot_bib = 0
    tot_kw = 0
    zero_cnt = 0
    for ctg in bib_count.keys():
        tot_bib += bib_count[ctg]
        tot_kw += kw_count[ctg]
        kw_ratio.append(kw_count[ctg]/bib_count[ctg])
        if kw_ratio[-1] > 1:
            kw_ratio[-1] = 1
        if kw_ratio[-1] == 0. and tot_bib >= 3:
            zero_cnt += 1

    total_ratio = tot_kw/tot_bib*100
    min_ratio = np.min(kw_ratio)*100
    max_ratio = np.max(kw_ratio)*100
    mean_ratio = np.mean(kw_ratio)*100
    var_ratio = np.var(kw_ratio)*100

    print('\nwriting contexts to file {}'.format(output_file))
    with open(output_file, 'w', encoding='utf-8') as f:
        tot_line = 'The Total Ratio of Finding Keyword is {:.3f}%.\n'.format(total_ratio)
        min_line = 'The Minimun Ratio of Finding Keyword is {:.3f}%.\n'.format(min_ratio)
        max_line = 'The Maximum Ratio of Finding Keyword is {:.3f}%.\n'.format(max_ratio)
        mean_line = 'The Mean Ratio of Finding Keyword is {:.3f}%.\n'.format(mean_ratio)
        var_line = 'The Variance Ratio of Finding Keyword is {:.3f}%.\n'.format(var_ratio)
        zero_line = '{:.3f}% of the papers find no keywords.\n'.format(zero_cnt/len(bib_count)*100)
        line = tot_line + min_line + max_line + mean_line + var_line + zero_line
        f.write(line)

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
        default='ratio_report.txt',
        help='name of output file (defaults to items.csv)')


    args = parser.parse_args()
    ret = generate_ratio(args.in_dir, args.db_uri, args.output_file)
    if not ret:
        sys.exit()



