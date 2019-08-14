from bokeh.models import ColumnDataSource, HoverTool, LabelSet, PanTool, ResetTool, WheelZoomTool
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from math import atan, pi
from bokeh_utils.tree.generate_bokeh_data import get_bokeh_data
from bokeh_utils.plot.get_data import get_all_colors
import pandas as pd


TOOLTIPS = [
    ("Decision", "@{decision}")
]


def create_plot(depth, level_width, acc, x, y, data_source, instance, node_list):
    circle_radius = 5
    # title = "Decision Tree " + ("\t\t\t\tAccuracy (%): " + str(round(acc * 100, 1))) \
    #                             + "   (Test Size: " + str('not available') + ", " \
    #                             + "Train Size: " + str('not available') + ")"
    hover = HoverTool(names=["circles"])
    wheel = WheelZoomTool()
    wheel.zoom_on_axis = False
    p = figure(width=750, tools=[hover, wheel, ResetTool(), PanTool()],
               x_range=x, y_range=list(y),
               tooltips=TOOLTIPS)
    _, label = draw_arrow(depth, level_width, x, y, data_source.data, p, instance, node_list)
    p.add_layout(label)
    p.circle("y", "x", radius=circle_radius, radius_units='screen',
             source=data_source,
             name="circles", legend="attribute_type",
             color=factor_cmap('attribute_type',
                               palette=get_all_colors(), factors=instance['all_attr_list']))
    # Final settings
    p.axis.visible = False
    p.toolbar.active_scroll = wheel
    p.outline_line_color = "white"
    p.grid.grid_line_color = None
    p.axis.axis_line_color = None
    return p


def draw_arrow(depth, level_width, x, y, source, p, instance, node_list, mode="draw"):
    arrow_coordinates = {"x_start": [], "x_end": [], "y_start": [], "y_end": [], "x_avg": [], "y_avg": [],
                         "label_name": [], "instances": [], "angle": [], "xs": [], "ys": []}
    for i in range(depth):
        x_offset = 0
        for j in range(level_width[i]):
            offset = sum(level_width[:i])
            if source["attribute_type"][offset + j] != 'Demand':
                children_names = [str(c.choices[-1][1]) for c in instance['nodes_map'][node_list[offset + j]].children]
                number_of_children = len(children_names)
                for index in range(number_of_children):
                    x_start = source["y"][offset + j]
                    y_start = source["x"][offset + j]
                    x_end = source["y"][x_offset + index + sum(level_width[: i + 1])]
                    y_end = source["x"][index + sum(level_width[: i + 1])]
                    if not x_end-x_start:
                        angle = -pi/2
                    else:
                        angle = atan((y_end - y_start) / (x_end - x_start) *
                                     (len(x) / len(y)) * (p.plot_height/p.plot_width))
                    arrow_coordinates["x_start"].append(x_start)
                    arrow_coordinates["x_end"].append(x_end)
                    arrow_coordinates["y_start"].append(y_start)
                    arrow_coordinates["y_end"].append(y_end)
                    arrow_coordinates["x_avg"].append((x_start + x_end) / 2)
                    arrow_coordinates["angle"].append(angle)
                    arrow_coordinates["y_avg"].append((y_start + y_end) / 2)
                    arrow_coordinates["label_name"].append(children_names[index])
                    arrow_coordinates["instances"].append(source["instances"][index + sum(level_width[: i + 1])])
                x_offset += number_of_children

    arrow_instance_min = min((int(x) for x in arrow_coordinates["instances"]), default=2)
    arrow_instance_max = max((int(x) for x in arrow_coordinates["instances"]), default=1)

    arrow_coordinates["xs"] = [[x_start] for x_start in arrow_coordinates["x_start"]]
    for i in range(len(arrow_coordinates["x_end"])):
        arrow_coordinates["xs"][i] += [arrow_coordinates["x_end"][i]]
    arrow_coordinates["ys"] = [[y_start] for y_start in arrow_coordinates["y_start"]]
    for i in range(len(arrow_coordinates["y_end"])):
        arrow_coordinates["ys"][i] += [arrow_coordinates["y_end"][i]]
    arrow_coordinates["instances"] = [1 + 7 * (int(x) - arrow_instance_min) /
                                      (arrow_instance_max - arrow_instance_min + 1)
                                      for x in arrow_coordinates["instances"]]
    arrow_data_source = ColumnDataSource(data=pd.DataFrame.from_dict(arrow_coordinates))
    if mode == "draw":
        p.multi_line(line_width="instances", line_alpha=0.7, line_color="darkgray",
                     name="multi_lines",
                     xs="xs", ys="ys", source=arrow_data_source)
    label = LabelSet(x='x_avg', y='y_avg', angle="angle",
                     name="arrowLabels", text="label_name",
                     text_font_size="8pt", text_color="darkgray", source=arrow_data_source, text_align="center")
    return arrow_data_source, label


def get_new_data_source(df):
    ''' modular data source
    Args:
        df: data frame
    '''
    df["nonLeafNodes_stat"] = [str(x) for x in df["nonLeafNodes_stat"]]
    if not df['nonLeafNodes_stat'].dropna().empty:
        df['nonLeafNodes_stat'] = ["-" if i == "None" else str(round(float(i), 3)) for i in df['nonLeafNodes_stat']]
    else:
        df['nonLeafNodes_stat'] = [1]
    df['decision'] = [decision if decision else "-" for decision in df['decision']]
    df["nonLeafNodes_stat"] = df["nonLeafNodes_stat"].fillna(0)


def modify_individual_plot(root, p, instance, active_attributes_list):
    ''' modular plot
    Args:
        root: select root of tree
        p: plot p to be modified
        instance: data class
        active_attributes_list: attributes that are currently selected
    '''
    data, depth, width, level_width, acc = get_bokeh_data(instance,
                                                          active_attributes_list + [instance.attr_list[-1]],
                                                          root)
    data = pd.DataFrame.from_dict(data)
    get_new_data_source(data)

    p.select(name="circles")[0].data_source.data = ColumnDataSource(data=data).data
    p.y_range.factors = y = [str(i) for i in range(0, depth + 1)]
    p.x_range.factors = x = [str(x) for x in range(0, width + 2)]
    arrow_data, _ = draw_arrow(depth, level_width, x, y, p.select(name="circles")[0].data_source.data,
                               p, instance, "get_data")
    p.select(name="multi_lines")[0].data_source.data = ColumnDataSource(data=arrow_data.data).data
    test_size = int(len(instance.data) * instance.test_percentage / 100)
    p.title.text = "Decision Tree" + ("\t\t\t\tAccuracy (%): " + str(round(acc * 100, 1))) \
                   + "   (Test Size: " + str(test_size) + ", "\
                   + "Train Size: " + str(int(len(instance.data) - test_size)) + ")"
