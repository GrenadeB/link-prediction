def in_set(u, w, Set):
    return (u + ' ' + w in Set) or (w + ' ' + u in Set)

def read_train(file):
    train_set = set()
    left_nodes = set()
    right_nodes = set()
    FIN = open(file, 'r')
    for line in FIN:
        train_set.add(line.strip())
        u, w = line.strip().split()
        left_nodes.add(int(u))
        right_nodes.add(int(w))
    FIN.close()
    return train_set, left_nodes, right_nodes

def sample_structural_poss(train_set, SIZE_POS):
    import random
    poss_set = set(random.sample(train_set, SIZE_POS))
    return poss_set
    
def sample_structural_neg(train_set, nodes, SIZE_NEG):
    import random
    neg_set = set()
    while len(neg_set) < SIZE_NEG:
        u = str(random.sample(nodes, 1)[0])
        w = str(random.sample(nodes, 1)[0])
        if u == w:
            continue
        if in_set(u, w, train_set):
            continue
        if in_set(u, w, neg_set):
            continue
        neg_set.add(u + ' ' + w)
    return neg_set

def sample_bipartite_neg(train_set, left_nodes, right_nodes, SIZE_NEG):
    import random
    neg_set = set()
    while len(neg_set) < SIZE_NEG:
        u_sample = random.sample(left_nodes, 100)
        w_sample = random.sample(right_nodes, 100)
        for (u, w) in zip(u_sample, w_sample):
            if u == w:
                continue
            u = str(u)
            w = str(w)
            if in_set(u, w, train_set):
                continue
            if in_set(u, w, neg_set):
                continue
            neg_set.add(u + ' ' + w)
    if len(neg_set) > SIZE_NEG:
        neg_set = set(random.sample(neg_set, SIZE_NEG))
    return neg_set

def sample_structural(file, N, method_neg_size=None):
    train_set, left_nodes, right_nodes = read_train(file)
    nodes = left_nodes | right_nodes
    SIZE_POS = int(N * len(train_set) / 100.)
    if method_neg_size == 'sq':
        SIZE_NEG = SIZE_POS * SIZE_POS
    else:
        SIZE_NEG = SIZE_POS
    poss_set = sample_structural_poss(train_set, SIZE_POS)
    neg_set = sample_structural_neg(train_set, nodes, SIZE_NEG)
    return train_set, nodes, poss_set, neg_set

def sample_bipartite(file, N):
    train_set, left_nodes, right_nodes = read_train(file)
    SIZE_POS = int(N * len(train_set) / 100.)
    SIZE_NEG = SIZE_POS
    poss_set = sample_structural_poss(train_set, SIZE_POS)
    neg_set = sample_bipartite_neg(train_set, left_nodes, right_nodes, SIZE_NEG)
    return train_set, left_nodes | right_nodes, poss_set, neg_set

class TopologicalFeatures:
    def __init__(self, graph, pos):
        self.g = graph
        self.pos = pos
        
    def dist(self, u, w):
        u = self.pos[self.g.vertex(u)]
        w = self.pos[self.g.vertex(w)]
        return -((u[0] - w[0])**2 + (u[1] - w[1])**2)**0.5

    def preferential_attachment(self, u, w):
        return self.g.vertex(u).out_degree()*self.g.vertex(w).out_degree()

    def common_neighbors(self, u, w):
        return len(set.intersection(
            set(self.g.vertex(u).out_neighbours()), 
            set(self.g.vertex(w).out_neighbours())))

    def union_neighbors(self, u, w):
        return len(
            set(self.g.vertex(u).out_neighbours()) | set(self.g.vertex(w).out_neighbours()))

    def Jaccards_coefficient(self, u, w):
        if union_neighbors(u, w) == 0:
            return 0
        return 1.0 * self.common_neighbors(u, w) / self.union_neighbors(u, w)

def make_dataset(poss_set, neg_set, functs):
    import numpy
    X = []
    Y = []
    for line in poss_set:
        u, w = map(int, line.split())
        x = []
        for func in functs:
            x.append(func(u, w))
        X.append(x)
        Y.append(1)
    for line in neg_set:
        u, w = map(int, line.split())
        x = []
        for func in functs:
            x.append(func(u, w))
        X.append(x)
        Y.append(0)
    X = numpy.array(X)
    Y = numpy.array(Y)
    return X, Y