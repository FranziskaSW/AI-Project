from tree import *
import pandas as pd
import math
from multiprocessing import Pool


# INPUT_PATH = "data/results_2018.csv"
INPUT_PATH = "dataa.csv"
GOAL = "Goal"
TRAIN_LEVEL = 0.5
TREE = "tree"
ENTROPY = "entropy"
INFORMATION_GAIN = "information_gain"
INFORMATION_RATIO = "information_ratio"


def tree_creation(type, records_df, limit=0, attributes=None, goal=GOAL):
    """"""
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


def create_trees(training_data, goal="pickups"):
    """"""
    p = Pool(2)
    res = p.starmap(tree_creation, [(TREE, training_data, 0, None, goal),
                                    (INFORMATION_GAIN, training_data, 0, None, goal),
                                    (ENTROPY, training_data, 0, None,
                                     goal)])
    p.close()
    p.join()

    for t in res:
        generate_graph(t)
    return res


def create_file(test_data, all_trees, goal):
    """"""
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
    """"""
    for t in all_trees:
        t.save_tree("trees/tree" + str(all_trees.index(t)) + ".txt")


def export_training_and_test(training_data, test_data):
    """"""
    training_data.to_csv("training_data.csv")
    test_data.to_csv("test_data.csv")


if __name__ == "__main__":
    """"""
    data = pd.read_csv(INPUT_PATH)
    training_data = data.sample(math.ceil(len(data) * TRAIN_LEVEL))
    test_data = data[~data.isin(training_data)].dropna()

    # create trees based on training data
    all_trees = create_trees(training_data, GOAL)

    # create file
    create_file(test_data, all_trees, GOAL)

    # Save data
    export_trees(all_trees)
    export_training_and_test(training_data, test_data)
