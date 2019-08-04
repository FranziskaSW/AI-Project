from tree import *
import pandas as pd
import math


# INPUT_PATH = "data/results_2018.csv"
INPUT_PATH = "dataa.csv"
TRAIN_LEVEL = 0.5


def create_trees(training_data, goal="pickups"):
    """"""
    all_trees = []
    all_trees.append(Tree(training_data, goal=goal))
    all_trees.append(EntropyTree(training_data, goal=goal))
    all_trees.append(InformationGainTree(training_data, goal=goal))
    all_trees.append(InformationRatioTree(training_data, goal=goal))
    return all_trees


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
    all_trees = create_trees(training_data, "Goal")

    # create file
    create_file(test_data, all_trees, "Goal")

    # Save data
    # export_trees(all_trees)
    # export_training_and_test(training_data, test_data)
