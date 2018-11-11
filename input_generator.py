import random
import sys
import networkx as nx
import numpy as np

def generate_input(output_path):
    with open("output/"+output_path+".out",'r') as file:
        l = [line for line in file]
    buses = np.array(l)
    comms = buses.T
    all_nodes = np.ndarray.flatten(buses)
    edge_prob_comm = 0.7
    edge_prob_bus = 0.3
    edge_prob_across = 0.05
    G = nx.Graph()
    G.add_nodes_from(all_nodes)

    for bus in buses:
        for i, person1 in enumerate(bus):
            for person2 in bus[i:]:
                if person1 != person2:
                    if random.random() < edge_prob_bus:
                        G.add_edge(person1, person2)
    
    for i, comm1 in enumerate(comms):
        for comm2 in comms[i:]:
            if comm1 == comm2:
                for person1 in comm1:
                    for person2 in comm2:
                        if random.random() < edge_prob_across:
                            G.add_edge(person1, person2)
            else:
                for person1 in comm1:
                    for person2 in comm2:
                        if random.random() < edge_prob_across:
                            G.add_edge(person1,person2)

    nx.write_gml(G, "inputs/"+output_path+".gml")

if __name__ == "__main__":
    output_path = sys.argv[1]
    generate_input(output_path)
