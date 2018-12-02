import networkx as nx
import os
import matplotlib.pyplot as plt
from networkx.algorithms import approximation as apxa
from networkx.algorithms.community import greedy_modularity_communities
import community
import itertools

###########################################
# Change this variable to the path to 
# the folder containing all three input
# size category folders
###########################################
path_to_inputs = "./all_inputs"

###########################################
# Change this variable if you want
# your outputs to be put in a 
# different folder
###########################################
path_to_outputs = "./outputs"

def findRowdyStudent(bus, rowdy_groups):
    bus_rowdy_groups = []
    
    for group in rowdy_groups:
        if set(group).issubset(bus):
            bus_rowdy_groups.append(group)   
    
    student_to_groups = {s : 0 for s in bus}
    for student in bus:
        for group in bus_rowdy_groups:
            if student in group:
                student_to_groups[student] += 1   

    most_rowdy = max(student_to_groups)
    return most_rowdy

def rawToPartition(partition):
    communities = set(partition.values())
    dictionary = {}
    for community in communities:
        dictionary[community] = []
        for key in partition.keys():
            if partition[key] == community:
                dictionary[community] += [key]
    return dictionary

def decreaseWeightForRowdy(G,rowdy_groups):
    for (u,v) in G.edges():
        for group in rowdy_groups:
            if (u in group) and (v in group):
                G[u][v]['weight'] -= 1

def getPartition(G, res):
    """ 
    Uses networkX partition method to create realtively even 
    partition  
  
    Parameters: 
    G : networkX graph
    res : some weird feature that toggles community size
  
    Returns: 
    d : dictionary with keys representing the communities and 
        values reprenting a list of nodes in each community 
    """
    p = community.best_partition(G, resolution=res)
    comms = set(p.values())
    d = {}
    for c in comms:
        d[c] = []
        for k in p.keys():
            if p[k] == c:
                d[c] += [k]
    return d

def fixPartition(G, partition, num_buses, bus_capacity, rowdy_groups):
    """ 
    Modifies the partition so that num_buses and bus_capacity constraints 
    are satisfied
    
    ***NOTE: should incorporate min degree students in buses when reassigning*** 
    
    Parameters: 
    G : networkX graph
    partition : original partition of graph
    num_buses : number of buses needed (from parameters.txt)
    bust_capacity : max number of students on a bus (from parameters.txt)
  
    Returns: 
    partition : updated partition with num_buses partitions, each with
    no more than bus_capacity students
    """ 
    
    og_partition_len = len(partition)
    
    if len(partition) > num_buses:
        while len(partition) > num_buses:
            min_comm_key = minCommKey(partition)
            min_comm = partition[min_comm_key]
            del partition[min_comm_key]
            for comm_key in partition.keys():
                if len(partition[comm_key]) < bus_capacity:
                    while len(min_comm) > 0 and len(partition[comm_key]) < bus_capacity:
                        partition[comm_key].append(min_comm.pop())
                if len(min_comm) == 0:
                    break;
        
    
    if len(partition) < num_buses:
        original_keys = list(partition.keys())
        for bus in range(og_partition_len, num_buses):
            partition[bus] = []
        
        while [] in partition.values():
            students_to_move = []
            while len(students_to_move) < num_buses - og_partition_len:
                for bus in range(og_partition_len):
                    if len(students_to_move) == num_buses - og_partition_len:
                        break;
                    if len(partition[bus]) > 1:
                        students_to_move.append(partition[bus].pop())
            
            for bus in range(og_partition_len, num_buses):
                partition[bus].append(students_to_move.pop())                 
               
    fixBusOverflow(partition, num_buses, bus_capacity, rowdy_groups)
    return partition

def fixBusOverflow(partition, num_buses, bus_capacity, rowdy_groups):
    """ 
    Reassigns students in partitions so that bus_capacity 
    constraint is satisfied
    
    ***NOTE: should incorporate min degree students in buses when reassigning*** 
  
    Parameters: 
    partition : some weird feature that toggles community size
  
    Returns: 
    d : dictionary with keys representing the communities and 
        values reprenting a list of nodes in each community 
    """
    overflow = []
    for bus in partition.keys():
        if len(partition[bus]) > bus_capacity:
            while len(partition[bus]) > bus_capacity:
                overflow.append(partition[bus].pop())
            
    for bus in partition.keys():
        if len(overflow) == 0:
            break;
        if len(partition[bus]) < bus_capacity:
            while len(partition[bus]) < bus_capacity and len(overflow) > 0:
                partition[bus].append(overflow.pop(partition[bus].indexOf(findRowdyStudent(partition[bus],rowdy_groups))))
                    
                
def minCommKey(partition):
    min_key, min_val = list(partition.items())[0]   
    for key, val in partition.items():
        if len(val) < len(min_val):
            min_key, min_val = key, val
    return min_key   
            
def sortBuses(G, partition):
    for bus, students in partition.items():
        unsorted_bus = dict((student, G.degree(student)) for student in students)
        sorted_bus_dict = dict(sorted(unsorted_bus.items(), key=operator.itemgetter(1)))
        sorted_bus = [student for student, degree in sorted_bus_dict.items()]
        sorted_bus.reverse()
        partition[bus] = sorted_bus       


def parse_input(folder_name):
    '''
        Parses an input and returns the corresponding graph and parameters

        Inputs:
            folder_name - a string representing the path to the input folder

        Outputs:
            (graph, num_buses, size_bus, constraints)
            graph - the graph as a NetworkX object
            num_buses - an integer representing the number of buses you can allocate to
            size_buses - an integer representing the number of students that can fit on a bus
            constraints - a list where each element is a list vertices which represents a single rowdy group
    '''
    graph = nx.read_gml(folder_name + "/graph.gml")
    parameters = open(folder_name + "/parameters.txt")
    num_buses = int(parameters.readline())
    size_bus = int(parameters.readline())
    constraints = []
    
    for line in parameters:
        line = line[1: -2]
        curr_constraint = [num.replace("'", "") for num in line.split(", ")]
        constraints.append(curr_constraint)

    return graph, num_buses, size_bus, constraints

def solve(graph, num_buses, size_bus, constraints):
    #TODO: Write this method as you like. We'd recommend changing the arguments here as well
    G = graph
    G.remove_edges_from(nx.selfloop_edges(G))
    
    #Remove duplicates
    rowdy_groups = constraints
    rowdy_groups.sort()
    rowdy_groups = list(rowdy_groups for rowdy_groups,_ in itertools.groupby(rowdy_groups))

    #Set initial edge weights
    nx.set_edge_attributes(G,len(rowdy_groups)+1,'weight')
    
    #Remove edges  between nodes that are in size-2 rowdy groups [u,v]
    for group in rowdy_groups:
        if len(group) == 2:
            if G.has_edge(group[0],group[1]):
                G.remove_edge(group[0],group[1])
    
    #Initial community detection
    partition = community.best_partition(G,resolution=1,weight='weight')
    partition = rawToPartition(partition)
    
    #Fix group sizes
    
    fixPartition(G,partition,num_buses,size_bus, rowdy_groups)
    
    #Adjust weight according to constraints
    decreaseWeightForRowdy(G,rowdy_groups)
    
    #Repartition with new weights
    partition = community.best_partition(G,resolution=1,weight='weight')
    partition = rawToPartition(partition)

    fixPartition(G,partition,num_buses,size_bus, rowdy_groups)

    return partition

def main():
    '''
        Main method which iterates over all inputs and calls `solve` on each.
        The student should modify `solve` to return their solution and modify
        the portion which writes it to a file to make sure their output is
        formatted correctly.
    '''
    size_categories = ["small", "medium", "large"]
    if not os.path.isdir(path_to_outputs):
        os.mkdir(path_to_outputs)

    for size in size_categories:
        category_path = path_to_inputs + "/" + size
        output_category_path = path_to_outputs + "/" + size
        category_dir = os.fsencode(category_path)
        
        if not os.path.isdir(output_category_path):
            os.mkdir(output_category_path)

        for input_folder in os.listdir(category_dir):
            print(input_folder)
            input_name = os.fsdecode(input_folder) 
            graph, num_buses, size_bus, constraints = parse_input(category_path + "/" + input_name)
            solution = solve(graph, num_buses, size_bus, constraints)
            output_file = open(output_category_path + "/" + input_name + ".out", "w")

            #TODO: modify this to write your solution to your 
            #      file properly as it might not be correct to 
            #      just write the variable solution to a file
            for line in solution.values():
                output_file.write(str(line))
                output_file.write("\n")

            output_file.close()

if __name__ == '__main__':
    main()


