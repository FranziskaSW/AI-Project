import copy


class Node:
    def __init__(self, data, choice=None):
        self.data = data
        self.choice = choice
        self.children = []

    def __del__(self):
        del self.children

    def add_children(self, children):
        self.children = children


class Tree:
    def __init__(self, nodes_dict, records):
        """creates the tree based on a dictionary of attributes and options"""
        self.root = self.create_tree(nodes_dict, records)

    def __del__(self):
        del self.root

    def create_tree(self, nodes_dict, records):
        """creates the tree and returns the root"""
        order = self.orginize_nodes(nodes_dict, records)
        return self.recursive_build(nodes_dict, records, order, [])

    def recursive_build(self, nodes_dict, records, order, path):
        """Recursive helper to build the tree"""
        if not order:
            return Node(self.decide_leaf(records, path), path[-1])
        else:
            data = order[0]
            if not path:
                node = Node(data)
            else:
                node = Node(data, path[-1])
            children = []
            for val in nodes_dict[data]:
                remaining = copy.deepcopy(order[1:])
                new_path = copy.deepcopy(path + [(data, val)])
                children.append(self.recursive_build(nodes_dict, records,
                                                     remaining, new_path))
            node.add_children(children)
            return node

    def orginize_nodes(self, nodes_dict, records):
        """Orginize the dictionary according to a certain logic"""
        attributes = list(nodes_dict.keys())
        return attributes

    def decide_leaf(self, records, path):
        """Decide the value of the leaf based on the records"""
        for k, v in records.items():
            if path == v:
                return k
        return "None"


if __name__ == "__main__":
    tree_nodes = {"a": [1,2,3,4], "b":[1,2,3], "c":[1,2]}
    records = dict()
    counter = 1
    for i in range(1,5):
        for j in range(1,4):
            for k in range(1,3):
                records["ans_" + str(counter)] = [("a",i), ("b",j), ("c", k)]
                counter += 1
    root = Tree(tree_nodes, records)
    print()
