from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select, Dropdown
from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox
from bokeh_utils.plot.utils import create_plot, get_new_data_source, draw_arrow
from bokeh_utils.tree.generate_bokeh_data import get_bokeh_data, tree_2_json
from tree import *
import pandas as pd
from os import listdir
import json

trees_path = './bokeh_utils/trees_for_visualization/'
files = [f for f in listdir(trees_path)]

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

entropy = Dropdown(label="Entropy Trees features", button_type="success", menu=list(tree_names_map['EntropyTree'].items()))
infogain = Dropdown(label="Information Gain Trees features", button_type="success", menu=list(tree_names_map['InformationGainTree'].items()))
inforatio = Dropdown(label="Information Ratio Trees features", button_type="success", menu=list(tree_names_map['InformationRatioTree'].items()))


def change_tree(_attr, _old, new):
    global tree, trees_path, data_source, arrow_dc, main_frame
    tree = Tree(None)
    tree.load_tree(''.join([trees_path, new]))
    main_frame.children = create_figure(new)


entropy.on_change('value', change_tree)
infogain.on_change('value', change_tree)
inforatio.on_change('value', change_tree)

p = None
tree = None
data_source = None
arrow_dc = None


def create_figure(file):
    global tree, p, data_source, arrow_dc

    tree = Tree(None)
    tree.load_tree(''.join([trees_path, file]))

    # active_attributes_list = [attr for attr in tree.attr_list if attr != tree.attr_list[-1]]
    instance = {}

    source, depth, width, level_width, acc, node_list = get_bokeh_data(tree, instance)
    y = [str(i) for i in range(0, depth+1)]
    x = [str(x) for x in range(0, width+2)]

    elements = pd.DataFrame.from_dict(source)
    df = elements.copy()
    get_new_data_source(df)
    data_source = ColumnDataSource(data=df)

    p, arrow_dc = create_plot(depth, level_width, acc, x, y, data_source, instance, node_list)
    p.title.text = "DecisionTreeMethod <features>: {}".format(' '.join(''.join(file.split('.')[:-1]).split('_')[:-1]))

    p.select(name="decision_text").visible = True
    p.select(name="arrowLabels").visible = True
    widgets = widgetbox(entropy, infogain, inforatio)

    return [widgets, p]


doc = curdoc()
main_frame = layout(create_figure(files[4]))
doc.add_root(main_frame)
