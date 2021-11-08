import math

import networkx as nx

from math import inf
import pandas as pd

MAX_ITERATIONS = 40


def is_directly_connected(node1, node2):
    nei = nx.neighbors(graph, node1)
    if node2 in nei:
        return True
    return False


def get_min_distance_df(node1, node2, dataframe):
    if nx.is_path(graph, [node1, node2]):
        short = nx.shortest_path(graph, source=node1, target=node2, weight="weight")
        if len(short) == 2:
            return graph.get_edge_data(node1, node2)["weight"]
    """             If here needs calc          """

    print(dataframe)
    print(f"checking paths between:  node_0: {node1}   n: {node2}\n")
    all_paths = nx.all_simple_paths(graph, node1, node2)
    to_ret = inf
    for path in all_paths:
        print(path)
        length = 0
        for count in range(len(path) - 1):
            path_length = dataframe.loc[path[0 + count], path[1 + count]]
            print(path_length)
            if isinstance(path_length, int):
                length = length + path_length
            else:
                length = math.inf
        print(f"Path length: {length}\n")
        if length < to_ret:
            to_ret = length
    return to_ret


def print_iteration(i):
    print_iteration2(i)
    '''
    if i > MAX_ITERATIONS or iterations[i] is None:
        return

    print(f"ITERATION {i}")
    print("-" * 25)
    print(dict(iterations)[i]["A"])
    print("\n")
    print(dict(iterations)[i]["B"])
    print("\n")
    print(dict(iterations)[i]["C"])
    print("\n")
    print(dict(iterations)[i]["D"])
    print("-" * 25)
    print("\n\n")
    '''


def print_iteration2(i):
    if i > MAX_ITERATIONS or iterations[i] is None:
        return

    print(f"ITERATION {i}")
    print("-" * 25)
    for m in range(0,len(sorted_nodes)):
        print(f"Node {sorted_nodes[m]}")
        print(dict(iterations)[i][sorted_nodes[m]])
        print("\n")
    print("-" * 25)
    print("\n\n")


def is_settled(i):

    if i <= 1:
        return False
    if (
            dict(iterations)[i - 1]["A"].equals(dict(iterations)[i]["A"]) &
            dict(iterations)[i - 1]["B"].equals(dict(iterations)[i]["B"]) &
            dict(iterations)[i - 1]["C"].equals(dict(iterations)[i]["C"]) &
            dict(iterations)[i - 1]["D"].equals(dict(iterations)[i]["D"])
    ):
        return True
    else:
        return False


def draw_graph():
    import matplotlib.pyplot as plt
    # explicitly set positions
    pos = {"A": (0, 0.5), "B": (1, 1), "C": (1, 0), "D": (2, 0.5)}
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True)
    labels = {e: graph.edges[e]['weight'] for e in graph.edges}

    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    # Set margins for the axes so that nodes aren't clipped
    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")

    plt.show(block=True)
    plt.pause(0.001)


def read_graph_outline():
    with open("graphoutline.txt") as F:
        s, t, w = [],[],[]

        for line in F.readlines():
            if "#" in line:
                break
            if line == "\n":
                continue
            try:
                node1, node2, weight = line.strip().split(",")
            except:
                print("Check input file!")
                quit()
            if node1.isalpha() and node1.isalpha() and weight.isdigit():
                s.append(node1)
                t.append(node2)
                w.append(weight)
            else:
                print("Check input file!")
                quit()
    return s, t, [int(x) for x in w]


s, t, w = read_graph_outline()

df = pd.DataFrame({'f1': s, 'f2': t, 'weight': w})
print(df)
graph = nx.from_pandas_edgelist(df=df, source="f1", target="f2", edge_attr="weight")
print(f"Received above {graph}\n")
""" Graph config complete """
""" Start implementation of distance vector """

sorted_nodes = sorted(list(dict.fromkeys(s + t)))
""" If matplotlib installed draw graph """


""" Object to store each iteration """
iterations = {x: dict.fromkeys(sorted_nodes) for x in range(1, MAX_ITERATIONS)}

print("FIRST ITERATION STARTING\n")
"""             First Iteration            """
i = 1
for node_label in sorted_nodes:
    df2 = pd.DataFrame(columns=sorted_nodes, index=sorted_nodes)
    for n in df2.columns:
        if is_directly_connected(node_label, n):
            data = graph.get_edge_data(node_label, n)
            df2[n][node_label] = data["weight"]
        elif n == node_label:        # If connecting to self
            df2[n][node_label] = 0
        else:                        # Else no direct connection exists
            df2[n][node_label] = inf
    iterations[i][node_label] = df2  # Store run in iteration dict
print_iteration(1)
print("FIRST ITERATION DONE\n")
"""     Second Iteration and Beyond        """
i = 2

while not is_settled(i-1):
    print(f"ITERATION {i} STARTING\n")
    """             Get Neighbor Data            """
    for node_label in sorted_nodes:
        df2 = pd.DataFrame(columns=sorted_nodes, index=sorted_nodes)
        for n in df2.index:
            if is_directly_connected(node_label, n):
                """    update node_0 with neighbors data    """
                di = dict(dict(iterations)[i - 1])[n]
                di = di.iloc[[sorted_nodes.index(n)]]
                df2.update(di)
                dict(iterations)[i][node_label] = df2

    """             Update Self with new Neighbor data           """

    for node_label in sorted_nodes:
        df2 = dict(iterations)[i][node_label]
        di = dict(dict(iterations)[i - 1])[node_label]
        di = di.iloc[[sorted_nodes.index(node_label)]]
        df2.update(di)
        for n in sorted_nodes:
            if n == node_label:
                df2.loc[node_label][n] = 0
            else:
                df2.loc[node_label][n] = get_min_distance_df(node_label, n, df2)
    print(f"ITERATION {i} DONE\n")
    i = i+1

print(is_settled(i))

for n in range(1, i-1):
    print_iteration(n)

try:
    draw_graph()
except ModuleNotFoundError:
    print("Install matplotlib for graph display]\n")
else:
    pass
