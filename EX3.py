import networkx as nx

def centrality_measures(network, node, iterations=100):
    dc = nx.degree_centrality(network)[node]
    cs = nx.closeness_centrality(network)[node]
    nbc = nx.betweenness_centrality(network, normalized=True)[node]
    pr = nx.pagerank(network, alpha=0.85, max_iter=iterations)[node]
    hits = nx.hits(network, max_iter=iterations)
    auth = hits[1][node]
    return {'dc': dc, 'cs': cs, 'nbc': nbc, 'pr': pr, 'auth': auth}


def single_step_voucher(network):
    degree_centrality = nx.degree_centrality(network)
    best_node = max(degree_centrality, key=degree_centrality.get)
    return best_node


def multiple_steps_voucher(network):
    closeness_centrality = nx.closeness_centrality(network)
    best_node = max(closeness_centrality, key=closeness_centrality.get)
    return best_node


def multiple_steps_diminished_voucher(network):
    shortest_path_dict = dict(nx.shortest_path_length(network))
    node_benefit_dict = {}
    for node in network.nodes():
        benefit = 0
        for length in shortest_path_dict[node].values():
            if length <= 4:
                benefit += 1 - 0.025 * length
        node_benefit_dict[node] = benefit
    best_node = max(node_benefit_dict, key=node_benefit_dict.get)
    return best_node


def find_most_valuable(network):
    betweenness_centrality = nx.betweenness_centrality(network)
    best_node = max(betweenness_centrality, key=betweenness_centrality.get)
    return best_node


def generic_multiple_steps_diminished_voucher(network, r=0.025, max_steps=4):
    shortest_path_dict = dict(nx.shortest_path_length(network))
    node_benefit_dict = {}
    for node in network.nodes():
        benefit = 0
        for path_length in shortest_path_dict[node].values():
            if path_length <= max_steps:
                benefit += 1 - r * path_length
        node_benefit_dict[node] = benefit
    best_node = max(node_benefit_dict, key=node_benefit_dict.get)
    return best_node


if __name__ == "__main__":

    friendships_network = nx.read_gml('friendships.gml')

    node_1_centrality = centrality_measures(friendships_network, 1)
    node_50_centrality = centrality_measures(friendships_network, 50)
    node_100_centrality = centrality_measures(friendships_network, 100)

    print(f'centrality measures of node 1:\n{node_1_centrality}')
    print(f'centrality measures of node 50:\n{node_50_centrality}')
    print(f'centrality measures of node 100:\n{node_100_centrality}')
    print('\n')

    best_candidate_single_step = single_step_voucher(friendships_network)
    print(f'Best candidate for sending the voucher using ‘single_step_voucher’: {best_candidate_single_step}')
    print('\n')

    best_candidate_multiple_step = multiple_steps_voucher(friendships_network)
    print(f'Best candidate for sending the voucher using ‘multiple_steps_voucher’: {best_candidate_multiple_step}')
    print('\n')

    best_candidate_diminished = multiple_steps_voucher(friendships_network)
    print(f'Best candidate for sending the voucher using ‘multiple_steps_diminished_voucher’: {best_candidate_diminished}')
    print('\n')

    best_candidate_valuable = find_most_valuable(friendships_network)
    print(f'Most valuable node for marketing strategy using ‘find_most_valuable’: {best_candidate_valuable}')
    print('\n')

    best_candidate_generic1 = generic_multiple_steps_diminished_voucher(friendships_network, r=0.025, max_steps=2)
    print(f'Best candidate for sending the voucher using ‘generic_multiple_steps_diminished_voucher’ with r=0.025, max_steps=2: {best_candidate_generic1}')
    print('\n')

    best_candidate_generic2 = generic_multiple_steps_diminished_voucher(friendships_network, r=0.01, max_steps=2)
    print(f'Best candidate for sending the voucher using ‘generic_multiple_steps_diminished_voucher’ with r=0.01, max_steps=2: {best_candidate_generic2}')
    print('\n')

    best_candidate_generic3 = generic_multiple_steps_diminished_voucher(friendships_network, r=0.01, max_steps=10)
    print(f'Best candidate for sending the voucher using ‘generic_multiple_steps_diminished_voucher’ with r=0.01, max_steps=10: {best_candidate_generic3}')
    print('\n')


