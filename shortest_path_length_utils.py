import igraph

def load_graph(fname):
    G = igraph.Graph.Read_Pajek(fname)
    return G

def get_vertex_seq_id(G, original_id):
    """gets the igraph vertex sequence id for a given node id"""
    try:
        return G.vs.find(id=str(original_id)).index
    except ValueError:
        return None

def get_shortest_path_length_for_one_pair(G, source_id, target_id):
    """source_id and target_id are the id in the original network"""
    source_igraph_id = get_vertex_seq_id(G, source_id)
    target_igraph_id = get_vertex_seq_id(G, target_id)
    if ( source_igraph_id is None ) or ( target_igraph_id is None ):
        return None
    else:
        sp_length = G.shortest_paths(source=source_igraph_id, target=target_igraph_id, mode='ALL')
        return sp_length[0][0]
