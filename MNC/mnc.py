#!/usr/bin/env python
# coding: utf-8

# # <center>Interactive Data Visualization in Python With Bokeh</center>

# ## Adding Interaction

# In[1]:

# import library yang dibutuhkan
import datetime
from os.path import dirname, join
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

# In[2]:

# Import modul bokeh
from bokeh.io import curdoc, show, str
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, DataRange1d, Select, Range1d, MultiSelect, CustomJS, Column
from bokeh.plotting import figure


# Memilih kolom yang digunakan yaitu temp, min, dan max
KOLOM = ['open', 'high', 'low']

# In[3]:


def dataset(src, name, level):  # Membaca data dari dataset
    files = src[src.change == name].copy()
    del files['change']
    files['date'] = pd.to_datetime(files.date)
    files['left'] = files.date - datetime.timedelta(days=0.5)
    files['right'] = files.date + datetime.timedelta(days=0.5)
    files = files.set_index(['date'])
    files.sort_index(inplace=True)
    if level == 'Level 2':  # Membuat distribusi halus agar data terlihat lebih halus
        window, order = 51, 5
        for key in KOLOM:
            files[key] = savgol_filter(files[key], window, order)
    elif level == 'Level 3':  # Membuat distribusi halus agar data terlihat lebih halus
        window, order = 31, 3
        for key in KOLOM:
            files[key] = savgol_filter(files[key], window, order)

    return ColumnDataSource(data=files)


def ploting(source, title):  # Membuat plot
    p = figure(x_axis_type="datetime", width=700, toolbar_location="below", y_range=Range1d(start=0, end=100))
    p.title.text = title

    # Membuat plot untuk kolom maksimum
    p.quad(top='open', bottom=0, left='left', right='right',
              color="#084594", source=source, legend_label="Open")
    # Membuat plot untuk kolom rata-rata
    p.quad(top='high', bottom=0, left='left', right='right',
              color="#4292c6", source=source, legend_label="High")
    # Membuat plot untuk kolom minimum
    p.quad(top='low', bottom=0, left='left', right='right',
              color="#9ecae1", source=source, legend_label="Low")

    # Menambahkan atribut yang akan ditampilkan
    p.xaxis.axis_label = "Tahun"
    p.yaxis.axis_label = "Change %"
    p.axis.axis_label_text_font_style = "bold"
    p.x_range = DataRange1d(range_padding=0.0)
    p.grid.grid_line_alpha = 0.5

    return p


def update_p(attrname, old, new):  # Memperbarui plot sesuai negara yang dipilih
    change = change_select.value
    p.title.text = "Data saham " + changes[change]['title']
    p.title.align = "center"
    src = dataset(files, changes[change]['change'],
                      level_select.value)
    source.data.update(src.data)




# Default negara dan distribusi yang akan ditampilkan
change = 'Rise'
level = 'Level 1'

# Memilih negara apa saja yang akan ditampilkan
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

OPTIONS = [("1", "Level 1"), ("2", "Level 2"), ("3", "Level 3")]

level_select = MultiSelect(value=["1"], options=OPTIONS, title= 'Grafik Diagram')
level_select.js_on_change("value", CustomJS(code="""console.log('level_select: value=' + this.value, this.toString())"""))

str(level_select)


#level_select = Select(
#    value=level, title='Grafik', options=['Level 1', 'Level 2', 'Level 3'])


# Membaca dataset dalam format csv
files = pd.read_csv(join(dirname(__file__), 'data/SahamMNCBank.csv'))
# Menggunakan kolom country
source = dataset(files, changes[change]['change'], level)
# Menyesuakan judul berdasarkan isi dari kolom country
p = ploting(source, "Data Saham " + changes[change]['title'])

x = np.linspace(-40, 40, 200)
y = x



# In[4]:

# Update data dengan menggunakan fitur select

change_select.on_change('value', update_p)
level_select.on_change('value', update_p)

controls = column(change_select, level_select)

curdoc().add_root(row(p, controls))
curdoc().title = "Data Saham MNC Bank"

# In[5]:


# bokeh serve --show myapp.py


# For more on all things interaction in Bokeh, [**Adding Interactions**](https://docs.bokeh.org/en/latest/docs/user_guide/interaction.html) in the Bokeh User Guide is a great place to start.

# In[ ]:
