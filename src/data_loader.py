import numpy as np
import os


def load_data(args):
    user_num, train_data, eval_data, test_data = load_rating(args)
    entity_num, relation_num, adj_entity, adj_relation = load_kg(args)
    print('data loaded.')

    return user_num, entity_num, relation_num, train_data, eval_data, test_data, adj_entity, adj_relation


def load_rating(args):
    print('reading rating file ...')

    # reading rating file
    rating_file = '../data/' + args.dataset + '/ratings_final'
    if os.path.exists(rating_file + '.npy'):
        rating_np = np.load(rating_file + '.npy')
    else:
        rating_np = np.loadtxt(rating_file + '.txt', dtype=np.int32)
        np.save(rating_file + '.npy', rating_np)

    user_num = len(set(rating_np[:, 0]))
    train_data, eval_data, test_data = dataset_split(rating_np)

    return user_num, train_data, eval_data, test_data


def dataset_split(rating_np):
    print('splitting dataset ...')

    # train:eval:test = 6:2:2
    train_ratio = 0.6
    eval_ratio = 0.2
    n_ratings = rating_np.shape[0]

    train_indices = np.random.choice(list(range(n_ratings)), size=int(n_ratings * train_ratio), replace=False)
    left = set(range(n_ratings)) - set(train_indices)
    eval_indices = np.random.choice(list(left), size=int(n_ratings * eval_ratio), replace=False)
    test_indices = list(left - set(eval_indices))

    train_data = rating_np[train_indices]
    eval_data = rating_np[eval_indices]
    test_data = rating_np[test_indices]

    return train_data, eval_data, test_data


def load_kg(args):
    print('reading KG file ...')

    # reading kg file
    kg_file = '../data/' + args.dataset + '/kg_final'
    if os.path.exists(kg_file + '.npy'):
        kg_np = np.load(kg_file + '.npy')
    else:
        kg_np = np.loadtxt(kg_file + '.txt', dtype=np.int32)
        np.save(kg_file + '.npy', kg_np)

    entity_num = len(set(kg_np[:, 0]) | set(kg_np[:, 2]))
    relation_num = len(set(kg_np[:, 1]))

    kg = construct_kg(kg_np)
    adj_entity, adj_relation = construct_adj(args, kg, entity_num)

    return entity_num, relation_num, adj_entity, adj_relation


def construct_kg(kg_np):
    print('constructing knowledge graph ...')
    kg = dict()
    for triple in kg_np:
        head = triple[0]
        relation = triple[1]
        tail = triple[2]
        # treat the KG as an undirected graph
        if head not in kg:
            kg[head] = []
        kg[head].append((tail, relation))
        if tail not in kg:
            kg[tail] = []
        kg[tail].append((head, relation))
    return kg


def construct_adj(args, kg, entity_num):
    print('constructing adjacency matrix ...')
    # each line of adj_entity stores the sampled neighbor entities for a given entity
    # each line of adj_relation stores the corresponding sampled neighbor relations
    adj_entity = np.zeros([entity_num, args.neighbor_sample_size], dtype=np.int32)
    adj_relation = np.zeros([entity_num, args.neighbor_sample_size], dtype=np.int32)
    for entity in range(entity_num):
        neighbors = kg[entity]
        n_neighbors = len(neighbors)
        if n_neighbors >= args.neighbor_sample_size:
            sampled_indices = np.random.choice(list(range(n_neighbors)), size=args.neighbor_sample_size, replace=False)
        else:
            sampled_indices = np.random.choice(list(range(n_neighbors)), size=args.neighbor_sample_size, replace=True)
        adj_entity[entity] = np.array([neighbors[i][0] for i in sampled_indices])
        adj_relation[entity] = np.array([neighbors[i][1] for i in sampled_indices])

    return adj_entity, adj_relation
