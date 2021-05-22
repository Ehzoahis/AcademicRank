import numpy as np
import argparse

def generate_bash(process_cnt, total_file, in_dir, url):
    intv = np.floor(total_file/process_cnt)

    with open('mag{}.sh'.format(process_cnt), 'w') as f:
        for i in range(1, process_cnt+1):
            if i != process_cnt:
                line = 'python3 citkwcnt_ds_batch.py {} -b {} -s {} -r {} -f item{}.csv -t {} &\n'.format(in_dir, url, int((i-1)*intv), int(intv), process_cnt+i, i)
            else:
                line = 'python3 citkwcnt_ds_batch.py {} -b {} -s {} -r {} -f item{}.csv -t {} &\n'.format(in_dir, url, int((i-1)*intv), (total_file-int((i-1)*intv)), process_cnt+i, i)
            f.write(line)
        f.close()

def extract_ds_log(fname):
    with open(fname, 'r') as f:
        lines = f.readlines()
    info = []
    for line in lines:
        tup = line.split(' ')
        info.append(str(tup[1]))
    info[0] = int(info[0])
    info[1] = int(info[1])
    return info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Script for generating the bash file for running citkwcnt_ds_batch.py in parallel'))
    parser.add_argument(
        'fname',
        help='file that saves the dataset and database information')
    
    args = parser.parse_args()
    info = extract_ds_log(args.fname)
    ret = generate_bash(info[0], info[1], info[2], info[3])
    if not ret:
        sys.exit()
