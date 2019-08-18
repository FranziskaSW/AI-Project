# -*- coding: utf-8 -*-
import datetime
import pandas as pd
from bokeh.tile_providers import get_provider, Vendors
from bokeh.io import curdoc
from bokeh.layouts import layout
from bokeh.models import (ColumnDataSource, HoverTool, SingleIntervalTicker, Slider, Button, Label, CategoricalColorMapper)
from bokeh.palettes import Viridis as palette
from bokeh.plotting import figure
import numpy as np
import math


def merc_x(lon):
    r_major=6378137.000
    return r_major*math.radians(lon)


def merc_y(lat):
    if lat>89.5:lat=89.5
    if lat<-89.5:lat=-89.5
    r_major=6378137.000
    r_minor=6356752.3142
    temp=r_minor/r_major
    eccent=math.sqrt(1-temp**2)
    phi=math.radians(lat)
    sinphi=math.sin(phi)
    con=eccent*sinphi
    com=eccent/2
    con=((1.0-con)/(1.0+con))**com
    ts=math.tan((math.pi/2-phi)/2)/con
    y=0-r_major*math.log(ts)
    return y


data_for_map = pd.read_pickle("./data/data_for_map.pkl")
data_for_map['demand'] = (np.random.randint(20, size=len(data_for_map)) - 10)
data_for_map['demand'] = data_for_map['demand'].astype(str)
data_for_map['longitude'] = data_for_map['longitude'].apply(lambda x: merc_x(x))
data_for_map['latitude'] = data_for_map['latitude'].apply(lambda y: merc_y(y))


data = {
    "Working day, good weather": data_for_map.loc[(data_for_map['weekday'] == 1) & (data_for_map['clear_sky'] == 1)],
    "Working day, bad weather": data_for_map.loc[(data_for_map['weekday'] == 1) & (data_for_map['rain'] == 1)],
    "Weekend day, good weather": data_for_map.loc[(data_for_map['weekday'] == 5) & (data_for_map['clear_sky'] == 1)],
    "Weekend day, bad weather": data_for_map.loc[(data_for_map['weekday'] == 5) & (data_for_map['rain'] == 1)]
}

plots_data = {}

hourtime_to_int = lambda h: h.hour * 60 + h.minute
int_to_hourtime = lambda i: datetime.time(i//60, i % 60)

tile_provider = get_provider(Vendors.CARTODBPOSITRON)


def animate_update():
    if (slider.value + 90) // 60 == 24:
        hour = hours[0]
    else:
        hour = int_to_hourtime(slider.value + 90)
    slider.value = hourtime_to_int(hour)


def slider_update(attrname, old, new):
    hour = slider.value
    label.text = 'time: {}, temperature: {}°F'.format(str(int_to_hourtime(hour)), str(current_plot_data[int_to_hourtime(hour)]['temp'][0]))
    source.data = current_plot_data[int_to_hourtime(hour)]


def animate():
    global callback_id
    if play.label == '► Play':
        play.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 200)
    else:
        play.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)


def load_plot(title):
    global current_plot_data, source, label
    current_plot_data = plots_data[title]
    hourtime_to_int(hours[0])
    slider.value = hourtime_to_int(hours[0])
    label.text = label.text = 'time: {}, temperature: {}°F'.format(str(int_to_hourtime(hour)), str(current_plot_data[int_to_hourtime(hour)]['temp'][0]))
    source.data = current_plot_data[hours[0]]


hours = pd.unique(data_for_map['time'])

for title, df in data.items():
    plots_data[title] = {}

    for hour in hours:
        hour_df = df[['latitude', 'longitude', 'demand', 'temp']].loc[df['time'] == hour]
        plots_data[title][hour] = hour_df.reset_index().to_dict('series')


current_plot_data = plots_data["Working day, good weather"]
source = ColumnDataSource(data=current_plot_data[hours[0]])

# plot = figure(x_range=(-8585000, -8565000), y_range=(4700000, 4708000), x_axis_type="mercator", y_axis_type="mercator", title='Demand Evolve', plot_height=500, plot_width=900)
plot = figure(title='Demand Evolve', plot_height=500, plot_width=900)

# plot.add_tile(tile_provider)

plot.xaxis.axis_label = "Longitude"
plot.yaxis.axis_label = "Latitude"

label = Label(x=min(source.data['longitude']), y=min(source.data['latitude']), text='time: {}, temperature: {}°F'.format(str(hours[0]), str(source.data['temp'][0])), text_font_size='25pt')
plot.add_layout(label)

color_mapper = CategoricalColorMapper(palette=palette[256], factors=[str(x) for x in range(-32, 32)])
plot.circle(
    x='longitude',
    y='latitude',
    size=7,
    source=source,
    fill_color={'field': 'demand', 'transform': color_mapper},
    fill_alpha=0.8,
    line_color='#7c7e71',
    line_width=0.5,
    line_alpha=0.5,
)

plot.add_tools(HoverTool(tooltips="Demand: @demand", show_arrow=False, point_policy='follow_mouse'))
slider = Slider(start=hourtime_to_int(hours[0]), end=hourtime_to_int(hours[-1]), value=hourtime_to_int(hours[0]), step=90, title="Minutes from midnight")
slider.on_change('value', slider_update)

callback_id = None

play = Button(label='► Play', width=60)
play.on_click(animate)


def m1():
    load_plot("Working day, good weather")


def m2():
    load_plot("Working day, bad weather")


def m3():
    load_plot("Weekend day, good weather")


def m4():
    load_plot("Weekend day, bad weather")


m1b = Button(label="Working day, good weather")
m1b.on_click(m1)

m2b = Button(label="Working day, bad weather")
m2b.on_click(m2)

m3b = Button(label="Weekend day, good weather")
m3b.on_click(m3)

m4b = Button(label="Weekend day, bad weather")
m4b.on_click(m4)


layout = layout([
    [m1b, m2b, m3b, m4b],
    [plot],
    [slider, play],
])

curdoc().add_root(layout)