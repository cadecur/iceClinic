import numpy as np
import holoviews as hv

from bokeh.io import show, curdoc
from bokeh.layouts import layout
from bokeh.models import Slider, Button, WMTSTileSource
from bokeh.models.widgets import Dropdown
import geoviews as gv
import geoviews.feature as gf
import xarray as xr
import scipy
from cartopy import crs, feature
from datetime import datetime
from bokeh.embed import json_item, components
import json
import math
import numpy as np

hv.extension('bokeh')
renderer = hv.renderer('bokeh').instance(mode='server')

# Create the holoviews app again
def sliceDimensions(state, padding=0, roundedOut=False):
    """Returns the appropriate latitude and longitude slices
    """

    # The column names are "","STATEFP","STUSPS","NAME","xmin","ymin","xmax","ymax"

    boundingBoxes = {
        ("1","01","AL","Alabama"): (-88.473227,30.223334,-84.88908,35.008028),
        ("2","02","AK","Alaska"): (-179.148909,51.214183,179.77847,71.365162),
        ("3","60","AS","American Samoa"): (-171.089874,-14.548699,-168.1433,-11.046934),
        ("4","04","AZ","Arizona"): (-114.81651,31.332177,-109.045223,37.00426),
        ("5","05","AR","Arkansas"): (-94.617919,33.004106,-89.644395,36.4996),
        ("6","06","CA","California"): (-124.409591,32.534156,-114.131211,42.009518),
        ("7","08","CO","Colorado"): (-109.060253,36.992426,-102.041524,41.003444),
        ("8","69","MP","Commonwealth of the Northern Mariana Islands"): (144.886331,14.110472,146.064818,20.553802),
        ("9","09","CT","Connecticut"): (-73.727775,40.980144,-71.786994,42.050587),
        ("10","10","DE","Delaware"): (-75.788658,38.451013,-75.048939,39.839007),
        ("11","11","DC","District of Columbia"): (-77.119759,38.791645,-76.909395,38.99511),
        ("12","12","FL","Florida"): (-87.634938,24.523096,-80.031362,31.000888),
        ("13","13","GA","Georgia"): (-85.605165,30.357851,-80.839729,35.000659),
        ("14","66","GU","Guam"): (144.618068,13.234189,144.956712,13.654383),
        ("15","15","HI","Hawaii"): (-178.334698,18.910361,-154.806773,28.402123),
        ("16","16","ID","Idaho"): (-117.243027,41.988057,-111.043564,49.001146),
        ("17","17","IL","Illinois"): (-91.513079,36.970298,-87.494756,42.508481),
        ("18","18","IN","Indiana"): (-88.09776,37.771742,-84.784579,41.760592),
        ("19","19","IA","Iowa"): (-96.639704,40.375501,-90.140061,43.501196),
        ("20","20","KS","Kansas"): (-102.051744,36.993016,-94.588413,40.003162),
        ("21","21","KY","Kentucky"): (-89.571509,36.497129,-81.964971,39.147458),
        ("22","22","LA","Louisiana"): (-94.043147,28.928609,-88.817017,33.019457),
        ("23","23","ME","Maine"): (-71.083924,42.977764,-66.949895,47.459686),
        ("24","24","MD","Maryland"): (-79.487651,37.911717,-75.048939,39.723043),
        ("25","25","MA","Massachusetts"): (-73.508142,41.237964,-69.928393,42.886589),
        ("26","26","MI","Michigan"): (-90.418136,41.696118,-82.413474,48.2388),
        ("27","27","MN","Minnesota"): (-97.239209,43.499356,-89.491739,49.384358),
        ("28","28","MS","Mississippi"): (-91.655009,30.173943,-88.097888,34.996052),
        ("29","29","MO","Missouri"): (-95.774704,35.995683,-89.098843,40.61364),
        ("30","30","MT","Montana"): (-116.050003,44.358221,-104.039138,49.00139),
        ("31","31","NE","Nebraska"): (-104.053514,39.999998,-95.30829,43.001708),
        ("32","32","NV","Nevada"): (-120.005746,35.001857,-114.039648,42.002207),
        ("33","33","NH","New Hampshire"): (-72.557247,42.69699,-70.610621,45.305476),
        ("34","34","NJ","New Jersey"): (-75.559614,38.928519,-73.893979,41.357423),
        ("35","35","NM","New Mexico"): (-109.050173,31.332301,-103.001964,37.000232),
        ("36","36","NY","New York"): (-79.762152,40.496103,-71.856214,45.01585),
        ("37","37","NC","North Carolina"): (-84.321869,33.842316,-75.460621,36.588117),
        ("38","38","ND","North Dakota"): (-104.0489,45.935054,-96.554507,49.000574),
        ("39","39","OH","Ohio"): (-84.820159,38.403202,-80.518693,41.977523),
        ("40","40","OK","Oklahoma"): (-103.002565,33.615833,-94.430662,37.002206),
        ("41","41","OR","Oregon"): (-124.566244,41.991794,-116.463504,46.292035),
        ("42","42","PA","Pennsylvania"): (-80.519891,39.7198,-74.689516,42.26986),
        ("43","72","PR","Puerto Rico"): (-67.945404,17.88328,-65.220703,18.515683),
        ("44","44","RI","Rhode Island"): (-71.862772,41.146339,-71.12057,42.018798),
        ("45","45","SC","South Carolina"): (-83.35391,32.0346,-78.54203,35.215402),
        ("46","46","SD","South Dakota"): (-104.057698,42.479635,-96.436589,45.94545),
        ("47","47","TN","Tennessee"): (-90.310298,34.982972,-81.6469,36.678118),
        ("48","48","TX","Texas"): (-106.645646,25.837377,-93.508292,36.500704),
        ("49","78","VI","United States Virgin Islands"): (-65.085452,17.673976,-64.564907,18.412655),
        ("50","49","UT","Utah"): (-114.052962,36.997968,-109.041058,42.001567),
        ("51","50","VT","Vermont"): (-73.43774,42.726853,-71.464555,45.016659),
        ("52","51","VA","Virginia"): (-83.675395,36.540738,-75.242266,39.466012),
        ("53","53","WA","Washington"): (-124.763068,45.543541,-116.915989,49.002494),
        ("54","54","WV","West Virginia"): (-82.644739,37.201483,-77.719519,40.638801),
        ("55","55","WI","Wisconsin"): (-92.888114,42.491983,-86.805415,47.080621),
        ("56","56","WY","Wyoming"): (-111.056888,40.994746,-104.05216,45.005904)
    }
    bounds = (0.0, 0.0, 0.0, 0.0)
    for item in boundingBoxes.items():
        if (state in item[0]):
            bounds = (item[1][0], item[1][1], item[1][2], item[1][3])
            break
    northeastBounds = (bounds[0] + 360.0 if bounds[0] < 0.0  else bounds[0],bounds[1], bounds[2] + 360 if bounds[2] < 0.0 else bounds[2], bounds[3])
    paddedBounds = (math.floor(northeastBounds[0] - padding),math.floor(northeastBounds[1] - padding), math.ceil(northeastBounds[2] + padding),math.ceil(northeastBounds[3] + padding)) if roundedOut else (northeastBounds[0] - padding, northeastBounds[1] - padding, northeastBounds[2] + padding, northeastBounds[3] + padding)
    return { "lat": slice(paddedBounds[1], paddedBounds[3]), "lon": slice(paddedBounds[0], paddedBounds[2]) }

def getMinMax(data, var):
    varData = data.data_vars[var]
    dataMax = varData.values.max()
    dataMin = varData.values.min()
    return dataMax, dataMin

path = './data/f09_g16.B.cobalt.FRAM.MAY.TS.200005-208106.nc'
preDataSet = xr.open_dataset(path)
curr_var = "TS"

dataMax, dataMin = getMinMax(preDataSet, curr_var)

def variableDropdown(value):
    path = './data/f09_g16.B.cobalt.FRAM.MAY.{}.200005-208106.nc'.format(value)
    preDataSet = xr.open_dataset(path)


def sine(phase, var):
    
    global path, preDataSet, curr_var, dataMax, dataMin
    #Select time frame (months)
    print(path)
    preDataSetSlice = preDataSet.isel(time=slice(int(phase),int(phase)+1))
    global curr_time 
    curr_time = str(preDataSetSlice['time'].data[0])
    ##acquire bounding box
    ##in this case we want to look at California
    #sliceObjects = sliceDimensions('CA', roundedOut = True, padding=1)
    #preDataSet = preDataSet.sel(lat=sliceObjects["lat"], lon = sliceObjects["lon"])

    ## Interpolated data
    #granularity = 16
    #new_lon = np.linspace(preDataSet.lon[0], preDataSet.lon[-1], preåDataSet.dims['lon'] * granularity)
    #new_lat = np.linspace(preDataSet.lat[0], preDataSet.lat[-1], preDataSet.dims['lat'] * granularity)

    #interpData = preDataSet.interp(lat=new_lat, lon=new_lon)

    # interpData.air.plot(ax=axes[1])
    # axes[1].set_title('Interpolated data')


    #creating dataset
    dataset = gv.Dataset(preDataSetSlice, ['lon', 'lat'], var)
    return gv.Image(dataset, vdims=hv.Dimension(var, range=(dataMin, dataMax))).opts(cmap='Reds', colorbar=True) * gf.coastline() * gf.borders() * gv.Feature(feature.STATES)

    # return gv.Image(dataset) * gf.coastline() * gf.borders() * gv.Feature(feature.STATES)
    #cobalt = dataset.to(gv.Image, ['lon', 'lat'], 'TS')
    #cobalt = cobalt.opts(backend='bokeh', responsive=True, cmap='Reds', colorbar=True) * gf.coastline() * gf.borders() * gv.Feature(feature.STATES)
    #return cobalt
    #xs = np.linspace(0, np.pi*4)
    #return hv.Curve((xs, np.sin(xs+phase))).opts(width=800)

stream = hv.streams.Stream.define('Phase', phase=0)()
var_stream = hv.streams.Stream.define('Var', var="TS")()
dmap = hv.DynamicMap(sine, streams=[stream, var_stream]).opts(width=500, height=400)
# Define valid function for FunctionHandler
# when deploying as script, simply attach to curdoc
def modify_doc(doc):
    # Create HoloViews plot and attach the document
    hvplot = renderer.get_plot(dmap, doc)

    # Create a slider and play buttons
    def animate_update():
        year = slider.value + 1
        if year > end:
            year = start
        slider.value = year

    def slider_update(attrname, old, new):
        # print(attrname, old, new)
        # Notify the HoloViews stream of the slider update 
        stream.event(phase=new)
        slider.title = curr_time
        
    def variable_update(event):
        global path, preDataSet, curr_var, dataMax, dataMin
        path = './data/f09_g16.B.cobalt.FRAM.MAY.{}.200005-208106.nc'.format(event.item)
        curr_var = event.item
        # print(path)
        preDataSet = xr.open_dataset(path)
        var_stream.event(var=event.item)
        dataMax, dataMin = getMinMax(preDataSet, curr_var)

    start, end = 0, 100
    slider = Slider(start=start, end=end, value=start, step=1, title="Date", show_value=False)
    slider.on_change('value', slider_update)
    
    #Variable Dropdown
    menu = [("Temperature", "TS"), ("Percipitation", "PRECT")]
    dropdown = Dropdown(label="Select Variable", button_type="primary", menu=menu)
    dropdown.on_click(variable_update)

    callback_id = None

    def animate():
        global callback_id
        if button.label == '► Play':
            button.label = '❚❚ Pause'
            callback_id = doc.add_periodic_callback(animate_update, 50)
        else:
            button.label = '► Play'
            doc.remove_periodic_callback(callback_id)
    button = Button(label='► Play', width=60)
    button.on_click(animate)
    
    curveData = preDataSet.sel(time=slice('2001-01-01', '2080-12-01'))
    data = curveData['TS'].resample(time="12M").mean(dim="time")
    temp_curve = hv.Curve(data.isel(lon=122, lat=45), kdims=['time']).opts(width=500)

    # Combine the holoviews plot and widgets in a layout
    plot = layout([
    [hvplot.state, hv.render(temp_curve)],
    [slider, button],
    [dropdown]], sizing_mode='fixed')
    
    curdoc().add_root(plot)
    #return doc

# To display in the notebook
#show(modify_doc, notebook_url='localhost:8888')

# To display in a script
doc = modify_doc(curdoc())
