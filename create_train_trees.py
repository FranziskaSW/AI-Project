from tree import *
import pandas as pd
import math
from multiprocessing import Pool


INPUT_PATH = "data/results_all.csv"
# INPUT_PATH = "dataa.csv"
GOAL = "demand"
# GOAL = "Goal"
TRAIN_LEVEL = 0.5
POOL_SIZE = 2
TREE = "tree"
ENTROPY = "entropy"
INFORMATION_GAIN = "information_gain"
INFORMATION_RATIO = "information_ratio"

BASIC_ATTRIBUTES = ["L1", "L2", "time", "demand"]
IGNORE_LIST = BASIC_ATTRIBUTES + ["Unnamed: 0", "Unnamed: 0.1", "cluster_id",
                                  "thunderstorm", "foggy", "humidity"]


def tree_creation(type, records_df, limit=0, attributes=None, goal=GOAL):
    """This function creates the trees"""
    if type == TREE:
        return Tree(records_df, limit, attributes, goal)
    elif type == ENTROPY:
        return EntropyTree(records_df, limit, attributes, goal)
    elif type == INFORMATION_GAIN:
        return InformationGainTree(records_df, limit, attributes, goal)
    elif type == INFORMATION_RATIO:
        return InformationRatioTree(records_df, limit, attributes, goal)
    else:
        return


def create_attributes_list(data):
    """Creates a list of attributes in order to build th trees"""
    attributes_list = []
    for column in data.columns:
        if column not in IGNORE_LIST:
            attributes_list.append(BASIC_ATTRIBUTES + [column])
    return attributes_list


def get_type(tree):
    """Gets the type of the tree"""
    return str(type(tree)).split('.')[1].split('\'')[0]


def create_trees(training_data, goal):
    """This function creates the trees using multi-threading"""
    p = Pool(POOL_SIZE)
    # every tree we want to create has to come in the format of
    # (type, df, limit, attributes, goal)
    attr_list = create_attributes_list(training_data)
    for lst in attr_list:
        res = []
        trees = [(TREE, training_data, 0, None, goal)]
        trees.append((ENTROPY, training_data, 0, None, goal))
        trees.append((INFORMATION_GAIN, training_data, 0, None, goal))
        trees.append((INFORMATION_RATIO, training_data, 0, None, goal))
        res = p.starmap(tree_creation, trees)
        for t in res:
            t.save_tree("trees/" + get_type(t) + "_" + lst[-1] + ".txt")
    p.close()
    p.join()


def create_file(test_data, all_trees, goal):
    """This function generates a file with the results of each tree and the
    actual result per line in the test data"""
    columns = ["tree" + str(i) for i in range(len(all_trees))]
    columns.append(goal)
    output = pd.DataFrame(columns=columns)
    for i in range(len(test_data)):
        row_dict = dict()
        row = test_data.iloc[i, :]
        for t in all_trees:
            row_dict["tree" + str(all_trees.index(t))] = t.get_val(row)
        row_dict[goal] = row[goal]
        output = output.append(pd.DataFrame.from_dict([row_dict]))
    output.to_csv("testing_by_tree.csv")


def export_trees(all_trees):
    """This function saves all the trees to files"""
    for t in all_trees:
        t.save_tree("trees/tree" + str(all_trees.index(t)) + ".txt")


def export_training_and_test(training_data, test_data):
    """This functino saves the training data and the testing data"""
    training_data.to_csv("training_data.csv")
    test_data.to_csv("test_data.csv")


def load_data(path):
    """"""
    return pd.read_csv(path)


if __name__ == "__main__":
    # data = pd.read_csv(INPUT_PATH)
    # training_data = data.sample(math.ceil(len(data) * TRAIN_LEVEL))
    #
    # test_data = data[~data.isin(training_data)].dropna()
    # training_data = load_data("data/training_data_1.csv")
    training_data = pd.read_csv("dataa.csv")
    # create trees based on training data
    create_trees(training_data, GOAL)
    # export_trees(all_trees)

    # create file
    # create_file(test_data, all_trees, GOAL)


