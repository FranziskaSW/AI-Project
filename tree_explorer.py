from bokeh.models import ColumnDataSource, Panel, Tabs, Toggle
from bokeh.models.widgets import Button, CheckboxGroup, Paragraph, Select, Slider
from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox
from bokeh_utils.plot.get_data import set_new_dataset
from bokeh_utils.plot.utils import create_plot, get_new_data_source, modify_individual_plot
from bokeh_utils.tree.generate_bokeh_data import get_bokeh_data
from tree import *
import pandas as pd
from os import listdir

trees_path = './data/Trees/'
files = [f for f in listdir(trees_path)]

tree = Tree(None)
tree.load_tree(''.join([trees_path, files[26]]))


# tree = set_new_dataset("lens")

test_percentage = 10
attr_info = Paragraph(text="""
   Get Predicted Demand:
""")
arrow_list = {"current": [], "previous": []}
selected_root = ""
attribute_checkbox = CheckboxGroup()
apply_changes_button = Button(label="Run", button_type="success")
# arrow_button = Toggle(label="Show Arrow Labels", button_type="warning")

tree_select = Select(title="Choose Tree Method and Attributes:")
tree_select.options = list(set(['None'] + [' '.join(f.split('.')[0].split('_')[:-1]) for f in files]))

# dataset_select = Select(title="Choose Data Set:", value="lens", options=["lens", "mushrooms"])
# dataset_slider = Slider(start=10, end=50, value=10, step=5, title="Test Set Percentage Split")


def apply_changes():
    modify_individual_plot(selected_root, p, tree, active_attributes_list)
    modify_individual_plot("", best_root_plot, tree, active_attributes_list)
    p.select(name="arrowLabels").visible = True
    p.select(name="multi_lines").visible = True
    apply_changes_button.disabled = False


apply_changes_button.on_click(apply_changes)


def change_dataset(_attr, _old, new):
    global selected_root, tree
    tree = set_new_dataset(new, test_percentage)
    selected_root = ""
    attribute_checkbox.labels = [attr for attr in tree.attr_list if attr != tree.attr_list[-1]]
    attribute_checkbox.active = [i for i, attr in enumerate(tree.attr_list)]
    # tree_select.options = ['None'] + [attr for attr in tree.attr_list[:-1]]
    apply_changes()


# dataset_select.on_change('value', change_dataset)


def create_figure():
    global active_attributes_list, p, best_root_plot

    # active_attributes_list = [attr for attr in tree.attr_list if attr != tree.attr_list[-1]]
    instance = {}

    source, depth, width, level_width, acc = get_bokeh_data(tree, instance)
    y = [str(i) for i in range(0, depth+1)]
    x = [str(x) for x in range(0, width+2)]

    elements = pd.DataFrame.from_dict(source)
    df = elements.copy()
    get_new_data_source(df)
    data_source = ColumnDataSource(data=df)

    p = create_plot(depth, level_width, acc, x, y, data_source, instance)

    best_root_plot_data = data_source.data.copy()
    best_root_plot_data_source = ColumnDataSource(data=best_root_plot_data)
    best_root_plot = create_plot(depth, level_width, acc, x, y, best_root_plot_data_source, instance)
    p.select(name="decision_text").visible = False
    best_root_plot.select(name="decision_text").visible = False
    p.select(name="arrowLabels").visible = False
    best_root_plot.select(name="arrowLabels").visible = False
    tab1 = Panel(child=p, title="Tree 1")
    tab2 = Panel(child=best_root_plot, title="Tree 2")
    # tab3 = Panel(child=p, title="Tree Method 3")
    # tab4 = Panel(child=best_root_plot, title="Tree Method 4")
    tree_tab = Tabs(tabs=[tab1, tab2], width=p.plot_width)
    change_dataset("", "", "lens")

    widgets = widgetbox(tree_select, attr_info, attribute_checkbox, apply_changes_button,
                        sizing_mode="stretch_both")

    main_frame = layout([[widgets, tree_tab]])
    return main_frame


def modify_test_percentage(_attr, _old, new):
    tree.update(tree.data, tree.attr_values, tree.attr_list,
                tree.attr_values_dict, tree.attr_dict, new)


# dataset_slider.on_change('value', modify_test_percentage)


def update_attributes(new):
    active_attributes_list[:] = []
    for i in new:
        active_attributes_list.append(tree.attr_list[i])
    if selected_root != '' and selected_root not in active_attributes_list:
        apply_changes_button.disabled = True
    else:
        apply_changes_button.disabled = False


attribute_checkbox.on_click(update_attributes)


def update_root(_attr, _old, new):
    global selected_root
    new = tree_select.options.index(new)
    method_type_selected = tree.attr_list[new - 1]
    if new == 0:
        selected_root = ''
        apply_changes_button.disabled = False
    elif method_type_selected not in active_attributes_list:
        selected_root = method_type_selected
        apply_changes_button.disabled = True
    else:
        selected_root = method_type_selected
        apply_changes_button.disabled = False


# root_select.on_change('value', update_root)


curdoc().add_root(create_figure())
