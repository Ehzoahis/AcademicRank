from collections import defaultdict
import sys
import os
import string
import argparse
import re

csv_type = re.compile(r"*.csv")

def combine_csv(dir_name, file_name):
    total_dict = defaultdict(int)
    for tar in os.listdir(dir_name):
        if csv_type.match(tar):
            print(tar)
            with open(tar, 'r') as s:
                for line in s:
                    s_list = line.split('\t')
                    s_key = ','.join(s_list[:-1])
                    s_cnt = int(s_list[-1])
                    total_dict[s_key] += s_cnt

    with open(file_name, 'w') as f:
        for key in total_dict.keys():
            val = ','.join([key, str(total_dict[key])])
            line = '{}\n'.format(val)
            f.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Script for combining CSV files in a directory'))
    parser.add_argument(
        'dir_path',
        help='the path of the directory')
    parser.add_argument(
        '-f',
        '--fname',
        dest='fname',
        default='result.csv',
        help='name of output file (defaults to result.txt)')

    args = parser.parse_args()
    ret = combine_csv(args.dir_path, args.fname)
    if not ret:
        sys.exit()
