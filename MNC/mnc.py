
import datetime
from os.path import dirname, join
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

from bokeh.io import curdoc, show, str
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, DataRange1d, Select, Range1d, MultiSelect, CustomJS, Column
from bokeh.plotting import figure


# Memilih kolom yang digunakan  
KOLOM = ['open', 'high', 'low']


def dataset(src, name, level):  # Membaca data dari dataset
    files = src[src.change == name].copy()
    del files['change']
    files['date'] = pd.to_datetime(files.date)
    files['left'] = files.date - datetime.timedelta(days=0.5)
    files['right'] = files.date + datetime.timedelta(days=0.5)
    files = files.set_index(['date'])
    files.sort_index(inplace=True)
    if level == 'Level 2': 
        window, order = 51, 5
        for key in KOLOM:
            files[key] = savgol_filter(files[key], window, order)
    elif level == 'Level 3':  
        window, order = 31, 3
        for key in KOLOM:
            files[key] = savgol_filter(files[key], window, order)

    return ColumnDataSource(data=files)


def ploting(source, title): 
    p = figure(x_axis_type="datetime", width=700, toolbar_location="below", y_range=Range1d(start=0, end=100))
    p.title.text = title

    # Membuat plot
    p.quad(top='open', bottom=0, left='left', right='right',
              color="#084594", source=source, legend_label="Open")
    p.quad(top='high', bottom=0, left='left', right='right',
              color="#4292c6", source=source, legend_label="High")
    p.quad(top='low', bottom=0, left='left', right='right',
              color="#9ecae1", source=source, legend_label="Low")

    # Tampilkan
    p.xaxis.axis_label = "Tahun"
    p.yaxis.axis_label = "Change %"
    p.axis.axis_label_text_font_style = "bold"
    p.x_range = DataRange1d(range_padding=0.0)
    p.grid.grid_line_alpha = 0.5

    return p


def update_p(attrname, old, new): 
    change = change_select.value
    p.title.text = "Data saham " + changes[change]['title']
    p.title.align = "center"
    src = dataset(files, changes[change]['change'],
                      level_select.value)
    source.data.update(src.data)


change = 'Rise'
level = 'Level 1'

changes = {
    'Rise': {
        'change': 'Rise',
        'title': 'Rise Change',
    },
    'Lower limit': {
        'change': 'Lower limit',
        'title': 'lower Limit Change',
    }, 
    'Unchnaged': {
        'change': 'Unchnaged',
        'title': 'Unchnaged Change',
    },
    'Upper Limit': {
        'change': 'Upper limit',
        'title': 'Upper Limit Change',
    },
     'Fall': {
        'change': 'Fall',
        'title': 'Fall Change',
    }
}

# Membuat dropdown
change_select = Select(value=change, title='Change',
                       options=sorted(changes.keys()))

#Membuat options
OPTIONS = [("1", "Level 1"), ("2", "Level 2"), ("3", "Level 3")]

level_select = MultiSelect(value=["1"], options=OPTIONS, title= 'Grafik Diagram')
level_select.js_on_change("value", CustomJS(code="""console.log('level_select: value=' + this.value, this.toString())"""))

show(level_select)


#level_select = Select(
#    value=level, title='Grafik', options=['Level 1', 'Level 2', 'Level 3'])



files = pd.read_csv(join(dirname(__file__), 'data/SahamMNCBank.csv'))
source = dataset(files, changes[change]['change'], level)
p = ploting(source, "Data Saham " + changes[change]['title'])

x = np.linspace(-40, 40, 200)
y = x


change_select.on_change('value', update_p)
level_select.on_change('value', update_p)

controls = column(change_select, level_select)

curdoc().add_root(row(p, controls))
curdoc().title = "Data Saham MNC Bank"

