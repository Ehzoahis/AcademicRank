mid2fid_fname = '/scratch/pritom/mag-2020-09-14/advanced/PaperFieldsOfStudy.txt'
o_fname = './PFoS.txt'

with open(o_fname, 'w') as fw:
    with open(mid2fid_fname, 'r') as fr:
        cnt = 0
        print('file opened')
        for line in fr:
            cnt += 1
            if cnt % 1000 == 0:
                print('\r{} lines read'.format(cnt), end='')
            items = line.split('\t')
            mid = items[0]
            fid = items[1]
            line= '{}\n'.format('\t'.join([mid, fid]))
            fw.write(line)