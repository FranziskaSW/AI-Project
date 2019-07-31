import copy
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


# GOAL = "pickups"
GOAL = "Goal"
THRESHOLD = 0.2


class Node:
    def __init__(self, data, choices=None, depth=0):
        self.data = data
        self.choices = choices
        self.children = []
        self.depth = depth

    def __del__(self):
        del self.children

    def add_children(self, children):
        self.children = children


class Tree:
    def __init__(self, records_df):
        """creates the tree based on a dictionary of attributes and options"""
        self.root = self.create_tree(records_df)

    def __del__(self):
        del self.root

    def create_tree(self, records_df):
        """creates the tree and returns the root"""
        attributes = list(records_df.columns)
        return self.recursive_build(records_df, attributes, [], 0)

    def recursive_build(self, records_df, attributes, path, depth):
        """Recursive helper to build the tree"""
        attribute = self.get_next_attribute(attributes, records_df)
        while len(records_df[attribute].value_counts()) == 1 and \
                len(attributes) > 1:
            attributes.remove(attribute)
            attribute = self.get_next_attribute(attributes, records_df)
        if attribute != GOAL:
            if not path:
                node = Node(attribute, depth=depth)
            else:
                node = Node(attribute, path, depth)
            children = []
            for val in records_df[attribute].unique():
                new_data = records_df[records_df[attribute] == val]
                new_path = copy.deepcopy(path + [(attribute, val)])
                records_df = records_df[records_df[attribute] != val]
                remaining = copy.deepcopy(attributes)
                remaining.remove(attribute)
                children.append(self.recursive_build(new_data,
                                                     remaining, new_path,
                                                     depth+1))
            node.add_children(children)
        else:
            node = Node(self.decide_leaf(records_df), path, depth=depth)
        return node

    def get_next_attribute(self, attribute_list, records_df):
        """returns the next attribute"""
        return attribute_list[0]

    def decide_leaf(self, records_df):
        """Decide the value of the leaf based on the records"""
        return records_df[GOAL].value_counts().argmax()

    def pruning(self, threshold):
        """Prunes the tree based on a threshold"""
        pass

    def get_val(self, row):
        """Gets the relevant node based on the row"""
        pass

    def save_tree(self, output_name):
        """Saves the tree"""
        pass

    def load_tree(self, output_name):
        """Saves the tree"""
        pass


class EntropyTree(Tree):
    def get_next_attribute(self, attribute_list, records_df):
        entropy = dict()
        for attribute in attribute_list:
            p = records_df[attribute].value_counts() / len(records_df)
            entropy[attribute] = np.sum(p * np.log2(1 / p))

        return min(entropy, key=entropy.get)


class InformationGainTree(Tree):
    def get_next_attribute(self, attribute_list, records_df):
        pass


def generate_graph(tree):
    """Generate a graph from the tree"""
    G = nx.DiGraph()
    nodes_left = [(tree.root, None)]
    labels = {}
    edge_labels = {}
    pos = dict()
    max_row = dict()
    while nodes_left:
        cur_node, cur_parent = nodes_left.pop()
        if cur_node.choices:
            node_name = ''.join(str(tup[0]) + str(tup[1]) for tup in cur_node.choices)
        else:
            node_name = cur_node.data
        if cur_node.depth in max_row.keys():
            max_row[cur_node.depth] += 1
        else:
            max_row[cur_node.depth] = 0
        pos[node_name] = (cur_node.depth, max_row[cur_node.depth])
        G.add_node(node_name)
        if cur_parent:
            G.add_edge(cur_parent, node_name)
            edge_labels[(cur_parent, node_name)] = cur_node.choices[-1][1]
        labels[node_name] = cur_node.data
        nodes_left.extend([(child, node_name) for child in cur_node.children])

    nx.draw(G, pos)
    nx.draw_networkx_labels(G, pos, labels, font_size=16)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=16)
    plt.axis('off')
    plt.show()
    return G


def draw_tree(G):
    """Draw the tree"""
    pos = nx.spring_layout(G)
    labels = {}
    for node in G.nodes():
        labels[node] = node
    edge_labels = {}
    for edge in G.edges:
        edge_labels[edge] = 0
    nx.draw_networkx_nodes(G, pos, G.nodes)
    nx.draw_networkx_labels(G, pos, labels, font_size=16)
    nx.draw_networkx_edges(G, pos, G.edges)
    nx.draw_networkx_edge_labels(G, pos, edge_labels)
    plt.axis('off')
    plt.show()


if __name__ == "__main__":
    data = pd.read_csv("dataa.csv")
    # data = pd.read_csv("pickups_2019.csv")
    # test = Tree(data)
    test = EntropyTree(data)
    test = InformationGainTree(data)
    G = generate_graph(test)
    # todo: add pruning, information gain
