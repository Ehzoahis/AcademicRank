import networkx as nx
import sys
import argparse

# can build edge than assign weight (O(E) + nO(V))
def build_graph(src_fname, dst_fname, line_start, line_end):
    with open(src_fname, 'r') as f:
        lines = f.readlines()
    
    print('construct grapgh')
    for line in lines[line_start: line_end]:
        edge = line.split('\t')
        src = edge[0]
        dst = edge[1]

        G.add_edge(src, dst)
    
    nx.write_adjlist(G, dst_fname)
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=('Script for building graph '
    'from mag ds'))
    parser.add_argument(
        '--in_file',
        default='./PaperReferences.txt',
        help='path of the file where mag ds is stored')
    parser.add_argument(
        '--out_file',
        default='./adj_list/out.adjlist',
        help='path of the file where adj file will be saved')
    parser.add_argument(
        '--line_start',
        type=int,
        default=0,
        help='starting line of the source file'
    )
    parser.add_argument(
        '--line_end',
        type=int,
        default=-1,
        help='ending line of the soure file'
    )

    args = parser.parse_args()
    build_graph(args.in_file, args.out_file, args.line_start, args.line_end)
