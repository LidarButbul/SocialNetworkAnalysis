import gzip
import itertools
import networkx as nx
import os
import csv
import json

def community_detector(algorithm_name, network, most_valuable_edge=None):
    partition = None
    modularity_value = -1
    if algorithm_name == 'girvin_newman':
        communities = list(nx.community.girvan_newman(network, most_valuable_edge))
        for community in communities:
            modularity = nx.algorithms.community.modularity(network, community)
            if modularity > modularity_value:
                partition = list(community)
                modularity_value = modularity
        partition = [list(part) for part in partition]
        num_partitions = len(partition)
    elif algorithm_name == 'louvain':
        community = list(nx.community.louvain_communities(network))
        partition = [list(c) for c in community]
        num_partitions = len(community)
        modularity_value = nx.community.modularity(network, community)
    elif algorithm_name == 'clique_percolation':
        for k in range(3, max(len(c) for c in nx.find_cliques(network))):
            community = nx.community.k_clique_communities(network, k)
            optional_partition = [list(c) for c in community]
            all_partition_nodes = set(node for c in optional_partition for node in c)
            for pair in itertools.combinations(optional_partition, 2):
                shared_node = list(set(pair[0]).intersection(set(pair[1])))
                if bool(shared_node):
                    sub_graph0 = network.subgraph(pair[0])
                    sub_graph1 = network.subgraph(pair[1])
                    for node in shared_node:
                        degree_node_0 = sub_graph0.degree(node)
                        degree_node_1 = sub_graph1.degree(node)
                        if degree_node_0 <= degree_node_1:
                            pair[0].remove(node)
                        else:
                            pair[1].remove(node)
            for node in network.nodes():
                if node not in all_partition_nodes:
                    optional_partition.append([node])
            modularity = nx.community.modularity(network, optional_partition)
            if modularity > modularity_value:
                modularity_value = modularity
                partition = optional_partition
        num_partitions = len(partition)
    else:
        raise ValueError('Unknown algorithm name')
    return {'num_partitions': num_partitions, 'modularity': modularity_value, 'partition': partition}


def edge_selector_optimizer(G):
    edge_betweenness = nx.edge_betweenness_centrality(G, weight='weight')
    sorted_edges = sorted(edge_betweenness.items(), key=lambda x: x[1], reverse=True)
    max_edge = sorted_edges[0][0]
    return max_edge


def construct_heb_edges(files_path, start_date='2019-03-15', end_date='2019-04-15', non_parliamentarians_nodes=0):
    if '2019' in start_date:
        central_players_file = os.path.join(files_path, 'central_political_players_2019.csv')
    else:
        central_players_file = os.path.join(files_path, 'central_political_players_2022.csv')
    central_players = []
    with open(central_players_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # skip header row
        for row in csvreader:
            central_players.append(row[0])

    edges_dict = {}
    for filename in os.listdir(files_path):
        if filename.endswith('.txt'):
            try:
                date_str = filename.split('.')[2]
                if start_date <= date_str <= end_date:
                    with open(os.path.join(files_path, filename), 'r', encoding='utf-8') as file:
                        for line in file:
                            tweet = json.loads(line)
                            if 'retweeted_status' in tweet:
                                original_tweeter_id = tweet['retweeted_status']['user']['id_str'] #who is tweeted the original post
                                retweeted_id = tweet['user']['id_str']  #who is retweet the post
                                if retweeted_id in central_players and original_tweeter_id in central_players:
                                    edge = (retweeted_id, original_tweeter_id)
                                    edges_dict[edge] = edges_dict.get(edge, 0) + 1
                                else:
                                    if non_parliamentarians_nodes > 0:
                                        all_node = []
                                        for key in edges_dict.keys():
                                            all_node.append(key[0])
                                            all_node.append(key[1])
                                        if retweeted_id in central_players and original_tweeter_id not in central_players:
                                            if original_tweeter_id not in all_node and retweeted_id in all_node:
                                                edge = (retweeted_id, original_tweeter_id)
                                                edges_dict[edge] = edges_dict.get(edge, 0) + 1
                                                non_parliamentarians_nodes -= 1
                                        else:
                                            continue
            except:
                continue
        elif filename.endswith('.gz'):
            try:
                date_str = filename.split('.')[2]
                if start_date <= date_str <= end_date:
                    with gzip.open(os.path.join(files_path, filename), 'rt', encoding='utf-8') as file:
                        for line in file:
                            tweet = json.loads(line)
                            if 'retweeted_status' in tweet:
                                original_tweeter_id = tweet['retweeted_status']['user']['id_str'] #who is tweeted the original post
                                retweeted_id = tweet['user']['id_str']  #who is retweet the post
                                if 'user' not in tweet:
                                    continue
                                if retweeted_id in central_players and original_tweeter_id in central_players:
                                    edge = (retweeted_id, original_tweeter_id)
                                    edges_dict[edge] = edges_dict.get(edge, 0) + 1
                                else:
                                    if non_parliamentarians_nodes > 0:
                                        all_node = []
                                        for key in edges_dict.keys():
                                            all_node.append(key[0])
                                            all_node.append(key[1])
                                        if retweeted_id in central_players and original_tweeter_id not in central_players:
                                            if original_tweeter_id not in all_node and retweeted_id in all_node:
                                                edge = (retweeted_id, original_tweeter_id)
                                                edges_dict[edge] = edges_dict.get(edge, 0) + 1
                                                non_parliamentarians_nodes -= 1
                                        else:
                                            continue
            except:
                continue
    return edges_dict


def construct_heb_network(edge_dict):
    G_tweet = nx.DiGraph()
    for edge, weight in edge_dict.items():
        G_tweet.add_edge(edge[1], edge[0], weight=weight)
    return G_tweet


if __name__ == '__main__':
    # question 1
    print('//question 1//')
    G1 = nx.les_miserables_graph()
    result_girvin_newman = community_detector('girvin_newman', G1)
    result_girvin_newman_with_optimizer = community_detector('girvin_newman', G1, edge_selector_optimizer)
    result_louvain = community_detector('louvain', G1)
    result_clique_percolation = community_detector('clique_percolation', G1)
    print('Girvan-Newman: ', result_girvin_newman)
    print('Girvan-Newman with edge_selector_optimizer: ', result_girvin_newman_with_optimizer)
    print('Louvain: ', result_louvain)
    print('Clique Percolation: ', result_clique_percolation)

    # question 2
    print('//question 2//')
    files_path = '/Users/lidarbut/PycharmProjects/HW2/all_data'
    central_players_2019 = os.path.join(files_path, 'central_political_players_2019.csv')
    dict_central_players_2019 = {}
    with open(central_players_2019, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # skip header row
        for row in csvreader:
            dict_central_players_2019[row[0]] = row[1]
    print('network1')
    edges_network1 = construct_heb_edges(files_path)
    network1 = construct_heb_network(edges_network1)
    print('without more nodes', network1.number_of_nodes())
    dict_result_network1 = community_detector('girvin_newman', network1, edge_selector_optimizer)
    print('Number of partition: ', dict_result_network1['num_partitions'])
    print('Modularity: ', dict_result_network1['modularity'])
    for partition in dict_result_network1['partition']:
        for i in range(len(partition)):
            partition[i] = dict_central_players_2019[partition[i]]
    for partition in dict_result_network1['partition']:
        print(partition)
    print('network2 - with 50 non_parliamentarians_nodes')
    edges_network2 = construct_heb_edges(files_path, non_parliamentarians_nodes=50)
    network2 = construct_heb_network(edges_network2)
    dict_result_network2 = community_detector('girvin_newman', network2, edge_selector_optimizer)
    print('Number of partition: ', dict_result_network2['num_partitions'])
    print('Modularity: ', dict_result_network2['modularity'])
    print('Number of node with non_parliamentarians_nodes=0: ', network1.number_of_nodes())
    print('Number of node with non_parliamentarians_nodes=50: ', network2.number_of_nodes())

    # question 3
    print('//question 3//')
    central_players_2022 = os.path.join(files_path, 'central_political_players_2022.csv')
    dict_central_players_2022 = {}
    with open(central_players_2022, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # skip header row
        for row in csvreader:
            dict_central_players_2022[row[0]] = row[1]
    print('network1')
    edges_network_2022 = construct_heb_edges(files_path, start_date='2022-10-01', end_date='2022-10-31')
    network_2022 = construct_heb_network(edges_network_2022)
    dict_result_network_2022 = community_detector('girvin_newman', network_2022, edge_selector_optimizer)
    print('Number of partition: ', dict_result_network_2022['num_partitions'])
    print('Modularity: ', dict_result_network_2022['modularity'])
    for partition in dict_result_network_2022['partition']:
        for i in range(len(partition)):
            partition[i] = dict_central_players_2022[partition[i]]
    for partition in dict_result_network_2022['partition']:
        print(partition)
    print('network2 - with 50 non_parliamentarians_nodes')
    edges_network_2022_extra = construct_heb_edges(files_path, start_date='2022-10-01', end_date='2022-10-31', non_parliamentarians_nodes=50)
    network_2022_extra = construct_heb_network(edges_network_2022_extra)
    dict_result_network_2022_extra = community_detector('girvin_newman', network_2022_extra,edge_selector_optimizer)
    print('Number of partition: ', dict_result_network_2022_extra['num_partitions'])
    print('Modularity: ', dict_result_network_2022_extra['modularity'])
    print('Number of node with non_parliamentarians_nodes=0: ', network_2022.number_of_nodes())
    print('Number of node with non_parliamentarians_nodes=50: ', network_2022_extra.number_of_nodes())







