from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select, Dropdown
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
tree.load_tree(''.join([trees_path, files[25]]))

tree_names_map = {
    'EntropyTree': {},
    'InformationGainTree': {},
    'InformationRatioTree': {},
    'Tree': {}
}


def map_manes(path):
    f = path.split('.')[0].split('_')
    tree_names_map[f[0]][' '.join(f[1:])] = path


list(map(map_manes, files))

entropy = Dropdown(label="Entropy Trees", button_type="success", menu=list(tree_names_map['EntropyTree'].items()))
infogain = Dropdown(label="Information Gain Trees", button_type="success", menu=list(tree_names_map['InformationGainTree'].items()))
inforatio = Dropdown(label="Information Ratio Trees", button_type="success", menu=list(tree_names_map['InformationRatioTree'].items()))


def change_tree(_attr, _old, new):
    global tree, trees_path
    tree = Tree(None)
    tree.load_tree(''.join([trees_path, new]))

    # attribute_checkbox.labels = [attr for attr in tree.attr_list if attr != tree.attr_list[-1]]
    # # attribute_checkbox.active = [i for i, attr in enumerate(tree.attr_list)]
    # # tree_select.options = ['None'] + [attr for attr in tree.attr_list[:-1]]
    #
    # modify_individual_plot(selected_root, p, tree, active_attributes_list)
    # modify_individual_plot("", best_root_plot, tree, active_attributes_list)
    # # p.select(name="arrowLabels").visible = True
    # p.select(name="multi_lines").visible = True
    # apply_changes_button.disabled = False


entropy.on_change('value', change_tree)
infogain.on_change('value', change_tree)
inforatio.on_change('value', change_tree)


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
    widgets = widgetbox(entropy, infogain, inforatio, sizing_mode="stretch_both")

    main_frame = layout([[widgets, p]], sizing_mode="fixed")
    return main_frame


curdoc().add_root(create_figure())
