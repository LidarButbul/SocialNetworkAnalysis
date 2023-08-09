import networkx as nx
import random
import numpy as np
from scipy.stats import binom_test
import pickle
import powerlaw
import matplotlib.pyplot as plt
from scipy.stats import probplot

with open('rand_nets.p', 'rb') as f:
    rand_nets_networks = pickle.load(f)

with open('scalefree_nets.p', 'rb') as f:
    scalefree_nets_networks = pickle.load(f)

with open('mixed_nets.p', 'rb') as f:
    mixed_nets_networks = pickle.load(f)

def random_networks_generator(n, p, num_networks=1, directed=False, seed=209505593):
    """
    Generate random networks using the G(n,p) model.

    :param: n: Number of nodes in each network.
            p: Probability for a pair of nodes to be connected.
            num_netwroks: Number of networks to generate.
            directed: Whether the network is directed or not.
    :return: List of NetworkX objects, each element is a random network.
    """
    networks = []
    random.seed(seed)
    for i in range(num_networks):
        G = nx.gnp_random_graph(n, p, seed+i, directed)
        networks.append(G)
    return networks

def network_stats(G):
    """
    Calculates basic statistics for a given network.

    :param: G: networkX object, the network to analyze
    :return: dict, a dictionary with statistics about the network
    """
    degrees = [d for n, d in G.degree()]
    degrees_avg = np.mean(degrees)
    degrees_std = np.std(degrees)
    degrees_min = min(degrees)
    degrees_max = max(degrees)
    spl = nx.average_shortest_path_length(G)
    diameter = nx.diameter(G)

    dict_stats = {
                'degrees_avg': degrees_avg,
                'degrees_std': degrees_std,
                'degrees_min': degrees_min,
                'degrees_max': degrees_max,
                'spl': spl,
                'diameter': diameter}
    return dict_stats

def networks_avg_stats(networks):
    """
    Calculates basic statistics for a given list of networks.

    :param: networks: a list of networkX objects
    :return: a dictionary with some statistics about the list of networks.
    """
    degrees = []
    spls = []
    diameters = []
    for G in networks:
        degrees += [d for n, d in G.degree()]
        spls.append(nx.average_shortest_path_length(G))
        diameters.append(nx.diameter(G))
    degrees_avg = np.mean(degrees)
    degrees_std = np.std(degrees)
    degrees_min = np.min(degrees)
    degrees_max = np.max(degrees)
    spl_avg = np.mean(spls)
    diameter_avg = np.mean(diameters)
    dict_avg_stats = {
                    'degrees_avg': degrees_avg,
                    'degrees_std': degrees_std,
                    'degrees_min': degrees_min,
                    'degrees_max': degrees_max,
                    'spl_avg': spl_avg,
                    'diameter_avg': diameter_avg}
    return dict_avg_stats

def rand_net_hypothesis_testing(network, theoretical_p, alpha=0.05):
    """
    Performs hypothesis testing for a random network’s ‘p’ parameter.
    The hypothesis test is as follows:
    𝐻0: 𝑝 = 𝑡h𝑒𝑜𝑟𝑒𝑡𝑖𝑐𝑎𝑙_𝑝
    𝐻1: 𝑝 ≠ 𝑡h𝑒𝑜𝑟𝑒𝑡𝑖𝑐𝑎𝑙_𝑝

    :param: network: a random network to test the hypothesis against.
            theoretical_p: the H0 ‘p’ value assumption
            alpha: the significance level of the test
    :return: a tuple of size two.
            The first element is the p-value of the test.
            The second element is a string of ‘accept’ or ‘reject’
            (‘accept’ means that 𝐻0 was accepted, ‘reject’ means 𝐻0was rejected).
    """
    n = len(network.nodes)
    m = len(network.edges)
    p_value = binom_test(m, ((n * (n - 1)) / 2), theoretical_p)
    if p_value < alpha:
        return (p_value, 'reject')
    else:
        return (p_value, 'accept')

def most_probable_p(network):
    """
    Find the most probable 'p' parameter of a given network.

    :param: network: The network to analyze
    :return: The most probable 'p' parameter.
    """
    theoretical_p = [0.01, 0.1, 0.3, 0.6]
    for p in theoretical_p:
        res_hypothesis = rand_net_hypothesis_testing(network, p)
        if res_hypothesis[1] == 'accept':
            return p
    return -1


def find_opt_gamma(network, treat_as_social_network=True):
    """
    Finds the optimal gamma parameter for a given network using the powerlaw package.

    :param: network: A random network.
            treat_as_social_network: Whether to treat the specified network as a social network.
    :return: The optimal gamma parameter found.
    """
    degrees = [d for n, d in network.degree()]
    if treat_as_social_network:
        fit = powerlaw.Fit(degrees, discrete=True, verbose=False)
    else:
        fit = powerlaw.Fit(degrees, discrete=False, verbose=False)
    gamma = fit.power_law.alpha
    return gamma

def netwrok_classifier(network):
    """
    Classify a network as random or scale-free.

    :param: network: A networkx Graph object representing the network.
    :return: 1 if the network is classified as random, 2 if it is classified as scale-free.
    """
    gamma = find_opt_gamma(network)
    if gamma > 3:
        return 1
    elif gamma > 2 and gamma < 3:
        return 2
    return -1 #not scale free and not random

# Generate a random network with the same number of nodes and edges as the given network
given_network = rand_nets_networks[0]
random_network = nx.gnm_random_graph(given_network.number_of_nodes(), given_network.number_of_edges())

# Calculate the degree distribution for the given network and the random network
given_degrees = list(dict(given_network.degree()).values())
random_degrees = list(dict(random_network.degree()).values())

# Plot the QQ plot
fig, ax = plt.subplots()
probplot(np.array(given_degrees), dist="norm", plot=ax)
probplot(np.array(random_degrees), dist="norm", plot=ax)
ax.legend(["Given network", "Random network"])
ax.set_title("QQ plot")
plt.show()

