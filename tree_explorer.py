from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select
from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox
from bokeh_utils.plot.utils import create_plot, get_new_data_source
from bokeh_utils.tree.generate_bokeh_data import get_bokeh_data, tree_2_json
from tree import *
import pandas as pd
from os import listdir
import json

trees_path = './data/Trees/'
files = [f for f in listdir(trees_path)]

tree = Tree(None)
tree.load_tree(''.join([trees_path, files[26]]))

# with open(''.join([trees_path, files[26], '.json']), 'w') as fp:
#     json.dump(tree_2_json(tree), fp, indent=2)

entropy = Select(title="Entropy Trees:")
entropy.options = list(set(['None'] + [' '.join(f.split('.')[0].split('_')[:-1]) for f in files]))

infogain = Select(title="Information Gain Trees:")
infogain.options = list(set(['None'] + [' '.join(f.split('.')[0].split('_')[:-1]) for f in files]))

inforatio = Select(title="Information Ratio Trees:")
inforatio.options = list(set(['None'] + [' '.join(f.split('.')[0].split('_')[:-1]) for f in files]))


def change_tree(_attr, _old, new):
    global selected_root, tree
    tree = Tree(None)
    tree.load_tree(''.join([trees_path, files[27]]))
    print(_attr, _old, new)

    # attribute_checkbox.labels = [attr for attr in tree.attr_list if attr != tree.attr_list[-1]]
    # # attribute_checkbox.active = [i for i, attr in enumerate(tree.attr_list)]
    # # tree_select.options = ['None'] + [attr for attr in tree.attr_list[:-1]]
    #
    # modify_individual_plot(selected_root, p, tree, active_attributes_list)
    # modify_individual_plot("", best_root_plot, tree, active_attributes_list)
    # # p.select(name="arrowLabels").visible = True
    # p.select(name="multi_lines").visible = True
    # apply_changes_button.disabled = False


# tree_select.on_change('value', change_tree)


def create_figure():
    global active_attributes_list, p, best_root_plot

    # active_attributes_list = [attr for attr in tree.attr_list if attr != tree.attr_list[-1]]
    instance = {}

    source, depth, width, level_width, acc, node_list = get_bokeh_data(tree, instance)
    y = [str(i) for i in range(0, depth+1)]
    x = [str(x) for x in range(0, width+2)]

    elements = pd.DataFrame.from_dict(source)
    df = elements.copy()
    get_new_data_source(df)
    data_source = ColumnDataSource(data=df)

    p = create_plot(depth, level_width, acc, x, y, data_source, instance, node_list)

    p.select(name="decision_text").visible = True
    p.select(name="arrowLabels").visible = True
    widgets = widgetbox(entropy, infogain, inforatio, sizing_mode="stretch_both", width=500)

    main_frame = layout([[widgets, p]], sizing_mode="fixed")
    return main_frame


curdoc().add_root(create_figure())
