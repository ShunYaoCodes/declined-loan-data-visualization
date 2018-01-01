# A program to visualize declined loan data using Pandas and Bokeh
# The data files can be downloaded at "DECLINED LOAN DATA" section on https://www.lendingclub.com/info/download-data.action
# The program runs on Bokeh server: open Anaconda Prompt, go to the folder containing the code file, type bokeh serve --show Reject_stats.py and enter

import pandas as pd
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Select, LinearColorMapper, HoverTool, BoxSelectTool, Slider, LabelSet
from bokeh.palettes import Viridis256
from bokeh.layouts import row, column

def update_y(attr, old, new):   # a function to update y-axis of a chart
    med = all_data[all_data['Application Date'].dt.year == slider1.value].groupby(['Employment Length'])[y_sel.value].mean().round(4)
    med = med.sort_values(ascending=False)
    p_med.yaxis.axis_label = y_sel.value
    p_med.x_range.factors = list(med.index)
    medCDS.data = dict(x=med.index, y=med.values)
    
def update_x(attr, old, new):   # a function to update x-axis of a chart
    cnt = all_data[all_data['Application Date'].dt.year == slider2.value].groupby(x_sel.value)[x_sel.value].count()
    cnt = cnt.sort_values(ascending=False)
    p_cnt.xaxis.axis_label = x_sel.value
    
    if(cnt.count())>=20:
        temp = cnt.nlargest(20) # display 20 largest categories at most on x-axis
        p_cnt.x_range.factors = list(temp.index)
        cntCDS.data = dict(x=temp.index, y=temp.values)
    else:
        p_cnt.x_range.factors = list(cnt.index)
        cntCDS.data = dict(x=cnt.index, y=cnt.values)

# put the data files in the same folder as the code file (for simplicity reasons)
# read the data into Pandas, skip the first rwo, parse 'Application Date' as date format
d0 = pd.read_csv('RejectStatsA.csv', skiprows=[0], parse_dates=['Application Date']) # 2007-2012 data
d1 = pd.read_csv('RejectStatsB.csv', skiprows=[0], parse_dates=['Application Date']) # 2013-2014 data
d2 = pd.read_csv('RejectStatsD.csv', skiprows=[0], parse_dates=['Application Date']) # 2015 data
d3 = pd.read_csv('RejectStats_2016Q1.csv', skiprows=[0], parse_dates=['Application Date']) # 2016 Q1 data
d4 = pd.read_csv('RejectStats_2016Q2.csv', skiprows=[0], parse_dates=['Application Date']) # 2016 Q2 data
d5 = pd.read_csv('RejectStats_2016Q3.csv', skiprows=[0], parse_dates=['Application Date']) # 2016 Q3 data
d6 = pd.read_csv('RejectStats_2016Q4.csv', skiprows=[0], parse_dates=['Application Date']) # 2016 Q4 data
d7 = pd.read_csv('RejectStats_2017Q1.csv', skiprows=[0], parse_dates=['Application Date']) # 2017 Q1 data
d8 = pd.read_csv('RejectStats_2017Q2.csv', skiprows=[0], parse_dates=['Application Date']) # 2017 Q2 data
d9 = pd.read_csv('RejectStats_2017Q3.csv', skiprows=[0], parse_dates=['Application Date']) # 2017 Q3 data
# union data
all_data = pd.concat([d0,d1,d2,d3,d4,d5,d6,d7,d8,d9], ignore_index=True)

# convert Percent(object) to Float
all_data['Debt-To-Income Ratio'] = all_data['Debt-To-Income Ratio'].replace('%','',regex=True).astype('float')/100

# add two selection widgets
y_sel = Select(title='Y Axis:', options=['Amount Requested','Debt-To-Income Ratio'], value='Amount Requested')
x_sel = Select(title='X Axis:', options=['Employment Length', 'Loan Title'], value='Employment Length')

# add two sliders
slider1 = Slider(title="Select above one year", start = all_data['Application Date'].dt.year.min(), end = all_data['Application Date'].dt.year.max(), 
                value = all_data['Application Date'].dt.year.min(), step=1)
slider2 = Slider(title="Select above one year", start = all_data['Application Date'].dt.year.min(), end = all_data['Application Date'].dt.year.max(), 
                value = all_data['Application Date'].dt.year.min(), step=1)

# calculate average Amount Requested over the years, display 4 decimal points
avg_amt = all_data.groupby('Application Date')['Amount Requested'].mean().round(4)

# calculate average Debt-To-Income Ratio, display 4 decimal points
avg_ratio = all_data.groupby('Application Date')['Debt-To-Income Ratio'].mean().round(4)

# calculate average based on slider value and sort, display 4 decimal points
med = all_data[all_data['Application Date'].dt.year == slider1.value].groupby(['Employment Length'])[y_sel.value].mean().round(4)
med = med.sort_values(ascending=False)

# calculate counts based on slider value and sort, display 4 decimal points
cnt = all_data[all_data['Application Date'].dt.year == slider2.value].groupby(x_sel.value)[x_sel.value].count()
cnt = cnt.sort_values(ascending=False)

# put into Column Data Source for faster and easier visualization
avg_amtCDS = ColumnDataSource(data=dict(x=avg_amt.index, y=avg_amt.values))
avg_ratioCDS = ColumnDataSource(data=dict(x=avg_ratio.index, y=avg_ratio.values))
medCDS = ColumnDataSource(data=dict(x=med.index, y=med.values))
cntCDS = ColumnDataSource(data=dict(x=cnt.index, y=cnt.values))

# create figure 1, add tools, time series chart
p_amt = figure(title='Trend of Average Amount Requested (Declined)', x_axis_label='Application Date', y_axis_label='Average Amount Requested', 
                  x_axis_type="datetime", plot_width=600, plot_height=400)
p_amt.add_tools(BoxSelectTool(), HoverTool(tooltips=[('Average Amount','$y{1.11}')])) 
p_amt.line('x', 'y', color='blue', legend='Average Amount Requested (Declined)', source=avg_amtCDS)

# create figure 2, add tools, time series chart
p_ratio = figure(title='Trend of Average Debt-To-Income Ratio', x_axis_label='Application Date', y_axis_label='Average Debt-To-Income Ratio',
                 x_axis_type="datetime", plot_width=600, plot_height=400) #  y_range=(0,200), y_range=(0,10)
p_ratio.add_tools(BoxSelectTool(), HoverTool(tooltips=[('Average Ratio','$y{1.11}')])) 
p_ratio.line('x', 'y', color='red', legend='Average Debt-To-Income Ratio', source=avg_ratioCDS)

Viridis256.reverse()    # reverse color palettes so that the higher values are in deeper colors

# create figure 3, add tools, vertical bar chart
p_med = figure(title='Average by Employment Length by Year', x_axis_label='Employment Length', x_range = list(med.index), plot_width=600, plot_height=400)
p_med.vbar('x', top='y', width=.5, source=medCDS,
           color={'field':'y','transform':LinearColorMapper(palette=Viridis256, low=min(med.values), high=max(med.values))})
p_med.add_tools(BoxSelectTool(), HoverTool(tooltips=[('Median Amount','$y{1.11}'), ('Employment Length','@x')]))
p_med.yaxis.axis_label = y_sel.value

# create figure 4, add tools, vertical bar chart
p_cnt = figure(title='Top 20 Counts by Year', y_axis_label='Count', x_range = list(cnt.index), plot_width=600, plot_height=400)
p_cnt.vbar('x', top='y', width=.5, source=cntCDS,
           color={'field':'y','transform':LinearColorMapper(palette=Viridis256, low=min(cnt.values), high=max(cnt.values))})
p_cnt.add_tools(BoxSelectTool(), HoverTool(tooltips=[('Median count','$y{1.11}'), ('X Value','@x')])) 
p_cnt.xaxis.major_label_orientation = 45
p_cnt.xaxis.axis_label = x_sel.value

# event triggers for selection widgets and sliders
y_sel.on_change('value',update_y)
x_sel.on_change('value',update_x)
slider1.on_change('value', update_y)
slider2.on_change('value', update_x)

# add data labels to figure 3 and 4
barLabels1 = LabelSet(x='x', y='y', text='y', text_font_size='8pt', x_offset=-10, y_offset=2,source=medCDS)
barLabels2 = LabelSet(x='x', y='y', text='y', text_font_size='8pt', x_offset=-10, y_offset=2,source=cntCDS)
p_med.add_layout(barLabels1)
p_cnt.add_layout(barLabels2)

# put into layout and run on Bokeh server
layout = column(row(p_amt,p_ratio), row(column(row(slider1,y_sel), p_med), column(row(slider2,x_sel), p_cnt)))
curdoc().add_root(layout)
curdoc().title = "Declined Loan Data"