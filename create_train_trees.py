from tree import *
import pandas as pd
import math
from multiprocessing import Pool
from os import listdir
from os.path import isfile, join


INPUT_PATH = "data/training_data_1.csv"
TEST_PATH = "data/test_data_1.csv"
TRAINING_SET = "1"
# INPUT_PATH = "dataa.csv"
GOAL = "demand"
# GOAL = "Goal"
TRAIN_LEVEL = 0.5
POOL_SIZE = 2
TREE = "Tree"
ENTROPY = "EntropyTree"
INFORMATION_GAIN = "InformationGainTree"
INFORMATION_RATIO = "InformationRatioTree"


BASIC_ATTRIBUTES = ["L1", "L2", "time"]
IGNORE_LIST = BASIC_ATTRIBUTES + ["Unnamed: 0", "Unnamed: 0.1", "cluster_id",
                                  "thunderstorm", "foggy", "humidity", "demand"]


def tree_creation(type, records_df, limit=0, attributes=None, goal=GOAL, name=""):
    """This function creates the trees"""
    if type == TREE:
        return Tree(records_df, limit, attributes, goal, name)
    elif type == ENTROPY:
        return EntropyTree(records_df, limit, attributes, goal, name)
    elif type == INFORMATION_GAIN:
        return InformationGainTree(records_df, limit, attributes, goal, name)
    elif type == INFORMATION_RATIO:
        return InformationRatioTree(records_df, limit, attributes, goal, name)
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
        print(lst[-1])
        trees = [(TREE, training_data, 0, lst, goal, TREE + "_" + lst[-1] +
                  "_" + TRAINING_SET)]
        trees.append((ENTROPY, training_data, 0, lst, goal,
                      ENTROPY + "_" + lst[-1] + "_" + TRAINING_SET))
        trees.append((INFORMATION_GAIN, training_data, 0, lst, goal,
                      INFORMATION_GAIN + "_" + lst[-1] + "_" + TRAINING_SET))
        trees.append((INFORMATION_RATIO, training_data, 0, lst, goal,
                      INFORMATION_RATIO + "_" + lst[-1] + "_" + TRAINING_SET))
        res = p.starmap(tree_creation, trees)
        for t in res:
            t.save_tree("trees/" + t.name + ".txt")
    p.close()
    p.join()


def create_file(test_data, all_trees, goal):
    """This function generates a file with the results of each tree and the
    actual result per line in the test data"""
    columns = [t.name for t in all_trees]
    columns.append(goal)
    output = pd.DataFrame(columns=columns)
    for i in range(len(test_data)):
        print(i / len(test_data))
        row_dict = dict()
        row = test_data.iloc[i, :]
        for t in all_trees:
            row_dict[t.name] = t.get_val(row)
        row_dict[goal] = row[goal]
        output = output.append(pd.DataFrame.from_dict([row_dict]))
    output.to_csv("testing_by_tree_" + TRAINING_SET + ".csv")


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


def additional_trees(training_data, goal):
    """"""
    p = Pool(POOL_SIZE)
    # every tree we want to create has to come in the format of
    # (type, df, limit, attributes, goal)
    new_basic = BASIC_ATTRIBUTES + ["weekday"]
    attr_list = [new_basic + ["month"]]
    attr_list.append(new_basic + ["clear_sky"])
    attr_list.append(new_basic + ["extreme_weather"])
    attr_list.append(new_basic + ["clear_sky", "extreme_weather"])
    for lst in attr_list:
        filename = "_".join(list(set(lst) - set(BASIC_ATTRIBUTES)))
        trees = [(TREE, training_data, 0, lst, goal,
                  TREE + "_" + filename + "_" + TRAINING_SET)]
        trees.append((ENTROPY, training_data, 0, lst, goal,
                      ENTROPY + "_" + filename + "_" + TRAINING_SET))
        trees.append((INFORMATION_GAIN, training_data, 0, lst, goal,
                      INFORMATION_GAIN + "_" + filename + "_" + TRAINING_SET))
        trees.append((INFORMATION_RATIO, training_data, 0, lst, goal,
                      INFORMATION_RATIO + "_" + filename + "_" + TRAINING_SET))
        res = p.starmap(tree_creation, trees)
        for t in res:
            t.save_tree("trees/" + t.name + ".txt")
    p.close()
    p.join()


def get_tree_files():
    onlyfiles = [f for f in listdir("trees") if
             isfile(join("trees", f)) and TRAINING_SET in f]
    return onlyfiles


def load_all_trees():
    files = get_tree_files()
    trees = []
    for file in files:
        new_tree = Tree(None)
        new_tree.load_tree("trees/" + file)
        trees.append(new_tree)
    return trees


if __name__ == "__main__":
    # data = pd.read_csv(INPUT_PATH)
    # training_data = data.sample(math.ceil(len(data) * TRAIN_LEVEL))
    #
    # test_data = data[~data.isin(training_data)].dropna()
    # training_data = load_data("data/training_data_1.csv")
    # training_data = pd.read_csv(INPUT_PATH)
    # create trees based on training data
    # create_trees(training_data, GOAL)
    # additional_trees(training_data, GOAL)
    # export_trees(all_trees)

    # create file
    # create_file(test_data, all_trees, GOAL)
    # test = Tree(None)
    # test.load_tree("trees/" + "EntropyTree_extreme_weather_clear_sky_weekday_1.txt")
    # generate_graph(test)
    # print(test.name)
    all_trees = load_all_trees()
    test_data = pd.read_csv(TEST_PATH)
    create_file(test_data, all_trees, GOAL)

