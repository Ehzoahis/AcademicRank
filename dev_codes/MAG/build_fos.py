from collections import defaultdict

o_fname = './mid2fos.txt'

fid2fos = dict()
mid2fos = defaultdict(list)

print('read FoS.txt')
with open(fid2fos_fname, 'r') as f:
    lines = f.readlines()
    tot = len(lines)
    cnt = 0
    print('{} lines to read'.format(tot))
    for line in lines:
        cnt += 1
        if cnt % 1000 == 0:
            print('\r{}/{} lines read'.format(cnt, tot), end='')
        items = line.split('\t')
        fid = items[0]
        fos = items[2]
        fid2fos[fid] = fos

with open(f_fname, 'r')

#
# print('\nread Paper_FoS.txt')
# with open(mid2fid_fname,'r') as f:
#     lines = f.readlines()
#     tot = len(lines)
#     cnt = 0
#     print('{} lines to read'.format(tot))
#     for line in lines:
#         cnt += 1
#         if cnt % 1000 == 0:
#             print('\r{}/{} lines read'.format(cnt, tot), end='')
#         items = line.split('\t')
#         mid = items[0]
#         fid = items[1]
#         fos = fid2fos[fid]
#         mid2fos[mid].append(fos)

print('\nwrite file')
with open(o_fname, 'w') as f:
    tot = lin(mid2fos)
    cnt = 0
    print('{} lines to write'.format(tot))
    for mid in mid2fos.keys():
        cnt += 1
        if cnt % 1000 == 0:
            print('\r{}/{} lines read'.format(cnt, tot), end='')
        fos = ' '.join(mid2fos[mid])
        line= '{}\n'.format('\t'.join([mid, fos]))
        f.write(line)
'''
