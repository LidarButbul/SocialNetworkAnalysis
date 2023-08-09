import networkx as nx
import random

def epidemic_analysis(network, model_type='SIS', infection_time=2, p=0.05, epochs=20, seed=209505593):
    random.seed(seed)

    infections_total = 0
    infectious_current = 0
    mortality_total = 0

    nodes_status = {}
    infected_nodes_time = {}

    for node in network.nodes:
        nodes_status[node] = network.nodes[node]['status'].upper()
        if nodes_status[node] == 'I':
            infected_nodes_time[node] = infection_time
            infections_total += 1
            infectious_current += 1

    for epoch in range(epochs):
        infected_nodes = list(infected_nodes_time.keys())
        for node in infected_nodes:
            if infected_nodes_time[node] > 0:
                infected_nodes_time[node] -= 1
                for neighbor in network.neighbors(node):
                    if nodes_status[neighbor] == 'S':
                        for i in range(network.edges[node, neighbor].get('contacts', 1)):
                            if random.random() < p:
                                nodes_status[neighbor] = 'I'
                                infections_total += 1
                                infectious_current += 1
                                infected_nodes_time[neighbor] = infection_time
                                break
                if random.random() < network.nodes[node]['mortalitylikelihood']:
                    mortality_total += 1
                    infectious_current -= 1
                    nodes_status[node] = 'R'
                    del infected_nodes_time[node]
            else:
                infectious_current -= 1
                del infected_nodes_time[node]
                if model_type == 'SIR':
                    nodes_status[node] = 'R'
                else:
                    if random.random() < network.nodes[node]['mortalitylikelihood']:
                        mortality_total += 1
                        nodes_status[node] = 'R'
                    else:
                        nodes_status[node] = 'S'
    r_0 = 0
    for node, status in nodes_status.items():
        if nodes_status[node] == 'I':
            for neighbor in network.neighbors(node):
                if nodes_status[neighbor] == 'S':
                    contacts = network.edges[node, neighbor].get('contacts', 1)
                    r_0 += 1 - (1 - p) ** contacts

    r_0 = r_0 / infectious_current if infectious_current > 0 else 0

    return {'infections_total': infections_total,
            'infectious_current': infectious_current,
            'mortality_total': mortality_total,
            'r_0': r_0}


def vaccination_analysis(network, model_type='SIR', infection_time=2, p=0.05, epochs=10, seed=209505593, vaccines=1, policy='rand'):
    if policy == 'rand':
        nodes_to_vaccinate = random.sample(list(network.nodes()), vaccines)
    elif policy == 'betweenness':
        betweenness_centrality = nx.betweenness_centrality(network)
        nodes_to_vaccinate = sorted(betweenness_centrality, key=betweenness_centrality.get, reverse=True)[:vaccines]
    elif policy == 'degree':
        degrees = dict(network.degree())
        nodes_to_vaccinate = sorted(degrees, key=degrees.get, reverse=True)[:vaccines]
    elif policy == 'mortality':
        mortalities = dict(network.nodes(data='mortalitylikelihood'))
        nodes_to_vaccinate = sorted(mortalities, key=mortalities.get, reverse=True)[:vaccines]
    else:
        raise ValueError("Invalid vaccination policy")

    for node in nodes_to_vaccinate:
        network.nodes[node]['status'] = 'R'
    return epidemic_analysis(network=network, model_type=model_type, infection_time=infection_time, p=p, epochs=epochs, seed=seed)

if __name__ == "__main__":
    network1 = nx.read_gml('epidemic1.gml')
    network2 = nx.read_gml('epidemic2.gml')
    networks = [network1, network2]

    num_simulations_part1 = 10
    num_simulations_part2 = 20


    def simulations_part1(networkk, setting, num_simulations=10, seed=209505593):
        total_infections = 0
        total_infectious_current = 0
        total_mortality = 0
        total_r0 = 0
        for _ in range(num_simulations):
            seed += 1
            simulation_result = epidemic_analysis(networkk, **setting, seed=seed)
            total_infections += simulation_result['infections_total']
            total_infectious_current += simulation_result['infectious_current']
            total_mortality += simulation_result['mortality_total']
            total_r0 += simulation_result['r_0']

        average_infections = total_infections / num_simulations
        average_infectious_current = total_infectious_current / num_simulations
        average_mortality = total_mortality / num_simulations
        average_r0 = total_r0 / num_simulations

        return {'Average_infections': average_infections,
                'Average_infectious_current': average_infectious_current,
                'Average_mortality': average_mortality,
                'Average_r0': average_r0}


    def simulations_part2(networkk, setting, num_simulations=10, seed=209505593):
        total_infections = 0
        total_infectious_current = 0
        total_mortality = 0
        total_r0 = 0
        for _ in range(num_simulations):
            simulation_result = vaccination_analysis(networkk, **setting, seed=seed)
            seed += 1
            total_infections += simulation_result['infections_total']
            total_infectious_current += simulation_result['infectious_current']
            total_mortality += simulation_result['mortality_total']
            total_r0 += simulation_result['r_0']

        average_infections = total_infections / num_simulations
        average_infectious_current = total_infectious_current / num_simulations
        average_mortality = total_mortality / num_simulations
        average_r0 = total_r0 / num_simulations

        return {'Average_infections': average_infections,
                'Average_infectious_current': average_infectious_current,
                'Average_mortality': average_mortality,
                'Average_r0': average_r0}

    print("Part 1", "\n")

    settings_part1 = [{'model_type': 'SIS', 'infection_time': 2, 'p': 0.05, 'epochs': 20},
                    {'model_type': 'SIS', 'infection_time': 5, 'p': 0.1, 'epochs': 20},
                    {'model_type': 'SIR', 'infection_time': 2, 'p': 0.05, 'epochs': 20},
                    {'model_type': 'SIR', 'infection_time': 5, 'p': 0.1, 'epochs': 20}]

    for network in networks:
        print('Network:', network, "\n")
        for setting in settings_part1:
            print('Setting', setting)
            result = simulations_part1(network, setting, num_simulations=num_simulations_part1)
            print(f'The average results after {num_simulations_part1} simulations:')
            print(result, "\n")

    print("Part 2", "\n")

    settings_part2 = [{'model_type': 'SIS', 'infection_time': 3, 'p': 0.1, 'epochs': 30, 'vaccines': 20, 'policy': "rand"},
                    {'model_type': 'SIS', 'infection_time': 3, 'p': 0.1, 'epochs': 30, 'vaccines': 20, 'policy': "betweenness"},
                    {'model_type': 'SIS', 'infection_time': 3, 'p': 0.1, 'epochs': 30, 'vaccines': 20, 'policy': "degree"},
                    {'model_type': 'SIS', 'infection_time': 3, 'p': 0.1, 'epochs': 30, 'vaccines': 20, 'policy': "mortality"}]

    for network in networks:
        print('Network:', network, "\n")
        for setting in settings_part2:
            print('Setting', setting)
            result = simulations_part2(network, setting, num_simulations=num_simulations_part2)
            print(f'The average results after {num_simulations_part2} simulations:')
            print(result, "\n")

