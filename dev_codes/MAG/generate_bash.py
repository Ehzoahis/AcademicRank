thread_cnt = 20
tot_lines = 1670074311
src_file = './PaperReferences.txt'
dst_dir = './adjlists/'
bash_file = './graph_bash.sh'
form = 'python3 build_adjlist.py --in_file {} --out_file {} --line_start {} --line_end {} {}\n'

with open(bash_file, 'w') as f:
    line_cnt = tot_lines // thread_cnt
    for thread in range(thread_cnt):
        if thread + 1 == thread_cnt:
            line = form.format(src_file, dst_dir+'graph'+str(thread+1)+'.adjlist', thread*line_cnt, tot_lines, '')
        else:
            line = form.format(src_file, dst_dir+'graph'+str(thread+1)+'.adjlist', thread*line_cnt, (thread+1)*line_cnt, '&')
        f.write(line)
