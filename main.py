import holoviews as hv
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.plotting import figure
from bokeh.models import Slider, Button, TextInput, Div
from bokeh.models.widgets import Dropdown
import geoviews as gv
import geoviews.feature as gf
import xarray as xr
from cartopy import crs, feature
import cftime

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')
hv.opts.defaults(hv.opts.Curve(width=600, framewise=True))

'''Helper function to return the maximum and minimum values for
a variable over the whole time series. Used to fix the scale of the
map visualization
Input: xarray dataset and name of variable
Output: 99.9 and .01 percentile of the data'''
def getMinMax(data, var):
    if var == 'SPI':
        dataMax = data.quantile(.999)['SPI'].data.tolist()
        dataMin = data.quantile(.001)['SPI'].data.tolist()
        return dataMin, dataMax
    varData = data.data_vars[var]
    dataMin = float(varData.values.min())
    print(dataMin)
    dataMax = float(varData.values.max())
    print(dataMax)
    return dataMin, dataMax

#Change these to change the default variables and intervention
curr_var = "TS"
curr_intervention = "FRAM"

#Initializes the paths and opens the datasets for all three types of interventions
path = './iceClinic/data/f09_g16.B.cobalt.FRAM.MAY.{}.200005-208106.nc'.format(curr_var)
fram_data = xr.open_dataset(path)

control_path = './iceClinic/data/f09_g16.B.cobalt.CONTROL.MAY.{}.200005-208106.nc'.format(curr_var)
control_data = xr.open_dataset(control_path)

global_path = './iceClinic/data/f09_g16.B.cobalt.GLOBAL.MAY.{}.200005-208106.nc'.format(curr_var)
global_data = xr.open_dataset(global_path)

#Maps variables to different colorschemes
CMAP_DICT = {'PRECT' : 'Blues', 'TS' : 'coolwarm', 'SPI' : 'BrBG', "FWI" : 'YlOrRd'}
#Maps intervention selections to the correct dataset
DATA_DICT = {'CONTROL': control_data, 'FRAM' : fram_data, 'GLOBAL' : global_data}

curr_dataset = DATA_DICT[curr_intervention]
min_range, max_range = getMinMax(curr_dataset, curr_var)

'''Callback function for geo graph dynamic map
Returns new visualization when time_step, variable,
or intervention type changes'''
def geo_plot(time_step, var, intervention):
    return gv_geo_plot[time_step]

'''Helper function to generate the timeseries plot for a
given intervention type and variable'''
def process_dataset(dataset, label, var, lat, lon):
    location_slice = dataset.sel(lon=int(lon), lat=int(lat), method='nearest')
    full_years = location_slice.sel(time=slice('2001-01-01', '2080-12-01'))
    data = full_years[var].resample(time="12M").mean(dim="time")
    data = data.rolling(time=10, center=True).mean()
    return hv.Curve(data, kdims=['time'], label=label)

'''Callback for the timeseries plot that updates the timeseries
when the variable or current latitude or longitude changes'''
def timeseries(var, lat, lon):
    control_plot = process_dataset(control_data, "Control", var, lat, lon)
    fram_plot = process_dataset(fram_data, 'Fram', var, lat, lon)
    global_plot = process_dataset(global_data, 'Global', var, lat, lon)
    plot = fram_plot * control_plot * global_plot
    labels = {'TS':'Temperature (C)',
              'PRECT' : "Precipitation (mm/day)",
              "SPI" : "Standardized Precipitation Index",
              "FWI" : "Fosberg Fire Weather Index"}
    return plot.opts(width=500, framewise=True, 
                     title='{} timeseries data'.format(curr_var), ylabel=labels[var])

stream = hv.streams.Stream.define('time_step', time_step=cftime.DatetimeNoLeap(2000, 6, 1))()
var_stream = hv.streams.Stream.define('Var', var="TS")()
lat_stream = hv.streams.Stream.define('Lat', lat=45)()
lon_stream = hv.streams.Stream.define('Lon', lon=122)()
intervention_stream = hv.streams.Stream.define('intervention', intervention="FRAM")()

dmap = hv.DynamicMap(geo_plot, streams=[stream, var_stream, intervention_stream]).opts(width=600)
dataset = gv.Dataset(curr_dataset)
stateBasemap = gv.Feature(feature.STATES)
gv_geo_plot = dataset.to(gv.Image, ['lon', 'lat'], 'TS', dynamic=True).opts(
    title = '{} Intervention, {} data'.format(curr_intervention, curr_var),
    cmap='coolwarm', colorbar=True, backend='bokeh', projection = crs.PlateCarree()) * gf.coastline() * gf.borders() * stateBasemap.opts(fill_alpha=0,line_width=0.5)
gv_geo_plot = gv_geo_plot.redim(TS=hv.Dimension(curr_var, range=(min_range, max_range)))

dmap_time_series = hv.DynamicMap(timeseries, streams=[var_stream, lat_stream, lon_stream]).opts(width=500, framewise=True)
#Main function that processes incoming events and defines the current layout
def modify_doc(doc):
    # Bokeh renderers that hold current viz as its state
    hvplot = renderer.get_plot(dmap, doc)
    timeseriesPlot = renderer.get_plot(dmap_time_series, doc)

    def animate_update():
        year = slider.value + 1
        if year > end:
            year = start
        slider.value = year

    callback_id = None
    def animate():
        global callback_id
        if button.label == '► Play':
            button.label = '❚❚ Pause'
            callback_id = doc.add_periodic_callback(animate_update, 75)
        else:
            button.label = '► Play'
            doc.remove_periodic_callback(callback_id)

    def slider_update(attrname, old, new):
        # Notify the HoloViews stream of the slider update 
        year = 2000 + (new // 12)
        month = (new % 12) + 1
        stream.event(time_step=cftime.DatetimeNoLeap(year,month,1))
        slider.title = "{}-{}".format(year,month)
        
    def variable_update(event):
        global path, fram_data, curr_var, min_range, max_range, control_path, control_data, global_data, global_path, gv_geo_plot, curr_dataset, curr_intervention, DATA_DICT
        path = './iceClinic/data/f09_g16.B.cobalt.FRAM.MAY.{}.200005-208106.nc'.format(event.item)
        control_path = './iceClinic/data/f09_g16.B.cobalt.CONTROL.MAY.{}.200005-208106.nc'.format(event.item)
        global_path = './iceClinic/data/f09_g16.B.cobalt.GLOBAL.MAY.{}.200005-208106.nc'.format(event.item)
        curr_var = event.item
        fram_data = xr.open_dataset(path)
        control_data = xr.open_dataset(control_path)
        global_data = xr.open_dataset(global_path)
        DATA_DICT = {'CONTROL': control_data, 'FRAM' : fram_data, 'GLOBAL' : global_data}
        curr_dataset = DATA_DICT[curr_intervention]
       
        dataset = gv.Dataset(curr_dataset)
        stateBasemap = gv.Feature(feature.STATES)
        gv_geo_plot = dataset.to(gv.Image, ['lon', 'lat'], curr_var, dynamic=True).opts(title = '{} Intervention, {} data'.format(curr_intervention, curr_var), cmap=CMAP_DICT[curr_var], colorbar=True, backend='bokeh', projection = crs.PlateCarree()) *gf.coastline() * gf.borders() * stateBasemap.opts(fill_alpha=0,line_width=0.5)

        #control_min_range, control_max_range = getMinMax(control_data, curr_var)
        #print(control_min_range, control_max_range)
        fram_min_range, fram_max_range = getMinMax(fram_data, curr_var)
        global_min_range, global_max_range = getMinMax(global_data, curr_var)
        min_range = min(fram_min_range, global_min_range)
        max_range = max(fram_max_range,global_max_range)
        
        gv_geo_plot = gv_geo_plot.redim(**{curr_var:hv.Dimension(curr_var, range=(min_range, max_range))})
        var_stream.event(var=event.item)

    def lat_update(attr, old, new):
        if int(new) in range(-90,90):
            lat_stream.event(lat=int(new)) 

    def lon_update(attr, old, new):
        if int(new) in range(-180,180):
            new_lon = int(new) + 180
            lon_stream.event(lon=new_lon) 

    def intervention_update(event):
        global curr_var, DATA_DICT, control_data, curr_intervention, gv_geo_plot, min_range, max_range
        curr_intervention = event.item
        curr_ds = DATA_DICT[event.item]
        dataset = gv.Dataset(curr_ds)
        gv_geo_plot = dataset.to(gv.Image, ['lon', 'lat'], curr_var, dynamic=True).opts(title = '{} Intervention, {} data'.format(curr_intervention, curr_var), cmap=CMAP_DICT[curr_var], colorbar=True, backend='bokeh', projection = crs.PlateCarree()) *gf.coastline() * gf.borders() * stateBasemap.opts(fill_alpha=0,line_width=0.5)        
        gv_geo_plot = gv_geo_plot.redim(**{curr_var:hv.Dimension(curr_var, range=(min_range, max_range))})
        intervention_stream.event(intervention=event.item)

    #Time_slider
    #Note: It starts as 5 because the datasets start in June 2000, the fifth month with zero indexing
    start, end = 5, 900
    slider = Slider(start=start, end=end, value=start, step=1, title="Date", show_value=False)
    slider.on_change('value', slider_update)
    
    #Variable Dropdown
    menu = [("Temperature", "TS"), ("Precipitation", "PRECT"), ("Fire Weather", "FWI"), ("Precipitation Index", "SPI")]
    dropdown = Dropdown(label="Select Variable", button_type="primary", menu=menu)
    dropdown.on_click(variable_update)

    #Intervention Dropdown
    intervention_menu = [("Control", "CONTROL"), ("Fram", "FRAM"), ("Global", "GLOBAL")]
    intervention_dropdown = Dropdown(label="Select Intervention Type", button_type="primary", menu=intervention_menu)
    intervention_dropdown.on_click(intervention_update)

    #Lat Text Input
    lat_input = TextInput(value="45", title="Latitude:")
    lat_input.on_change("value", lat_update)

    #Lon Text Input
    lon_input = TextInput(value="122", title="Longitude:")
    lon_input.on_change("value", lon_update)

    #Slider Play Button
    button = Button(label='► Play', width=60)
    button.on_click(animate)
    

    #Code to generate the layout
    lat_lon_text = Div(text="<b>Note:</b> Latitude ranges from -90 to 90 and longitude from -180 to 180")
    spacer = Div(height=200)

    logo = figure(x_range=(0, 10), y_range=(0, 10), plot_width=300, plot_height=300)
    logo.image_url( url=['./iceClinic/static/logo.png'], x=0, y=0, w=10, h=10, anchor="bottom_left")
    logo.toolbar.logo, logo.toolbar_location = None, None
    logo.xaxis.visible, logo.yaxis.visible = None, None
    logo.xgrid.grid_line_color, logo.ygrid.grid_line_color = None, None
    # Combine the holoviews plot and widgets in a layout

    logo = row(logo, align='center')
    options_row = row(slider, button, align='center')
    left_plot_row= row(hvplot.state, align='center')
    left_column = column(left_plot_row, options_row, dropdown, intervention_dropdown, sizing_mode='stretch_width', align='center')
    coords_row = row(lat_input, lon_input, align='center')
    right_plot_row = row(timeseriesPlot.state, align='center')
    right_column = column(right_plot_row, coords_row, lat_lon_text)

    graphs = row(left_column, right_column, sizing_mode="stretch_width", align='center')

    plot = column(logo, graphs, spacer, sizing_mode='stretch_width', align='center')
    
    curdoc().add_root(plot)


# To display in a script
doc = modify_doc(curdoc())