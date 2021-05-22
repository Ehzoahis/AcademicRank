import numpy as np 
from sqlalchemy import create_engine
from collections import defaultdict

class Edge:
    def __init__(self, src, dst, kw, cnt):
        self.src = src
        self.dst = dst
        self.kw = kw
        self.cnt = cnt
        self.sim = 1.0
        self.target = False
        self.similar = False
    
    def set_sim(self, sim):
        self.similar = True
        self.sim = sim
    
    def mark_target(self):
        self.target = True

class Graph:
    def __init__(self):
        self.node_list = set()
        self.edge_list = set()
        self.edge_dict = defaultdict(list)
        self.edge_map = defaultdict(lambda: defaultdict(list))
        self.aid2mid = dict()
        self.mid2aid = dict()

    def insert_node(self, aid):
        self.node_list.add(aid)

    def assign_mid(self, aid, mid):
        self.aid2mid[aid] = mid
        self.mid2aid[mid] = aid

    def insert_edge(self, edge):
        self.edge_list.add(edge)
        self.edge_dict[edge.src].append(edge.dst)
        self.edge_map[edge.src][edge.dst].append(edge)

    def get_dst_list(self, src):
        return self.edge_dict[src]

    def has_node(self, aid=None, mid=None):
        if mid and mid in self.mid2aid.keys():
            return True
        elif aid and aid in self.node_list:
            return True
        else:
            return False

    def get_aid(self, mid):
        return self.mid2aid[mid]

    def get_mid(self, aid):
        return self.aid2mid[aid]

    def get_edge(self, src, dst):
        return self.edge_map[src][dst]


def get_similar_kw(keyword):
    dtype = [('kw', object), ('sim', float)]
    sim_kw = list()
    pass
    return np.array(sim_kw, dtype=dtype)

def query_db(db_url, keyword):
    print(db_url)
    engine = create_engine(db_url)

    print('querying DB')
    q = ('select CTD_MAG_ID, CTD_AID, KEYWORD, CTG_AID, COUNT'
         ' from citation_keyword_net'
         ' where KEYWORD=\'{}\'').format(keyword);
    tuples = engine.execute(q).fetchall()
    return tuples

def build_init_graph(db_url, sim_kw):
    kws_list = sim_kw['kw']
    sim_list = sim_kw['sim']
    graph = Graph()
    dummy_aid = 0
    for kw, sim in zip(kws_list, sim_list):
        table = query_db(db_url, str(kw))
        for item in table:
            # unpack table
            ctd_mid = item[0] 
            ctd_aid = item[1]
            kwd = item[2]
            ctg_aid = item[3]
            cnt = item[4]
            # assign dummy aid to dangling nodes
            if ctd_aid == 'None':
                if graph.has_node(mid=ctd_mid):
                    ctd_aid = graph.get_aid(ctd_mid)
                else:
                    ctd_aid = str(dummy_aid)
                    dummy_aid += 1
            # insert node for dst
            if not graph.has_node(aid=ctd_aid):
                graph.insert_node(ctd_aid)
                graph.assign_mid(ctd_aid, ctd_mid)
            # insert node for src
            if not graph.has_node(aid=ctg_aid):
                graph.insert_node(ctg_aid)
            # insert edge
            edge = Edge(ctg_aid, ctd_aid, kwd, cnt)
            edge.set_sim(sim)
            if sim == 1.0:
                edge.mark_target()
            graph.insert_edge(edge)
    return graph


