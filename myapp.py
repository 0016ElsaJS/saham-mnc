#Import library yang digunakan
import datetime
from os.path import dirname, join
from token import OP
from click import option
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

#Modul bokeh yang digunakan
from bokeh.io import curdoc, show
from bokeh.layouts import column, row, widgetbox
from bokeh.models import ColumnDataSource, DataRange1d, Select, Range1d, MultiSelect, CustomJS, TextAreaInput
from bokeh.models.widgets import Slider
from bokeh.plotting import figure


# Kolom dataset yang digunakan yaitu kolom open, high dan low yang digunakan untuk perbandingan
KOLOM = ['open', 'high', 'low']

#Membaca data dari dataset saham mnc
def dataset(src, name, level): 
    files = src[src.change == name].copy()
    
    #Melihat data change untuk lihat nilai sahamnya
    del files['change']
    files['date'] = pd.to_datetime(files.date)
    files['left'] = files.date - datetime.timedelta(days=0.5)
    files['right'] = files.date + datetime.timedelta(days=0.5)
    files = files.set_index(['date'])
    files.sort_index(inplace=True)
    #Membuat data menjadi smooth
    if level == 'Level 2': 
        window, order = 51, 5
        for key in KOLOM:
            files[key] = savgol_filter(files[key], window, order)
    elif level == 'Level 3':  
        window, order = 31, 3
        for key in KOLOM:
            files[key] = savgol_filter(files[key], window, order)

    return ColumnDataSource(data=files)

#Membuat plot high, open dan low
def ploting(source, title): 
    p = figure(x_axis_type="datetime", width=700, toolbar_location="below", y_range=Range1d(start=0, end=100))
    p.title.text = title

    # Membuat plot untuk kolom open
    p.quad(top='open', bottom=0, left='left', right='right',
              color="#084594", source=source, legend_label="Open")
    # Membuat plot untuk kolom high
    p.quad(top='high', bottom=0, left='left', right='right',
              color="#4292c6", source=source, legend_label="High")
    # Membuat plot untuk kolom low
    p.quad(top='low', bottom=0, left='left', right='right',
              color="#9ecae1", source=source, legend_label="Low")

    # Menambahkan atribut yang ditampilkan
    p.xaxis.axis_label = "Tahun"
    p.yaxis.axis_label = "Change %"
    p.axis.axis_label_text_font_style = "bold"
    p.x_range = DataRange1d(range_padding=0.2)
    p.grid.grid_line_alpha = 0.5

    return p

# Melakukan update plot sesuai change
def update_p(attrname, old, new): 
    change = change_select.value
    p.title.text = "Data saham " + changes[change]['title']
    p.title.align = "center"
    src = dataset(files, changes[change]['change'],
                      level_select.value)
    source.data.update(src.data)

# Default change dan level yang ditampilkan pertama kali
change = 'Rise'
level = 'Level 1'

# Membuat data change yang akan ditampilkan
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

# Membuat options
OPTIONS = [("1", "Level 1"), ("2", "Level 2"), ("3", "Level 3")]

level_select = MultiSelect(value=["1"], options=OPTIONS, title= 'Grafik Diagram')
level_select.js_on_change("value", CustomJS(code="""console.log('level_select: value=' + this.value, this.toString())"""))

show(level_select)

# Membuat Textarea
text_area_input = TextAreaInput(value="Tuliskan apapun", rows=6, title="Tulis saja:")
text_area_input.js_on_change("value", CustomJS(code="""
    console.log('text_area_input: value=' + this.value, this.toString())
"""))

show(text_area_input)

#level_select = Select(
#    value=level, title='Grafik Diagram', options=['Level 1', 'Level 2', 'Level 3'])

# Membaca dataset dalam format csv
files = pd.read_csv(join(dirname(__file__), 'data/SahamMNCBank.csv'))
# Menggunakan kolom change
source = dataset(files, changes[change]['change'], level)
# Memberikan judul berdasarkan isi dari kolom change
p = ploting(source, "Data Saham " + changes[change]['title'])

x = np.linspace(-20, 20, 200)
y = x

# Update data dengan menggunakan fitur select
change_select.on_change('value', update_p)
level_select.on_change('value', update_p)

controls = column(change_select, level_select, text_area_input)

curdoc().add_root(row(p, controls))
curdoc().title = "Data Saham MNC Bank"

