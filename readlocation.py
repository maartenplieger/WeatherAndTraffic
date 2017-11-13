#sudo apt-get install python-pyshp
# http://opendata.ndw.nu/NDW_Shapefiles_20170926.zip
import shapefile
import pandas
from scipy import stats
import datetime
import netCDF4
import numpy as np
import dateutil.parser
import time

def getSpeed(timeandtype, location, time):  
  rows = timeandtype.loc[timeandtype.periodStart == time]

  indices = rows['index'].unique()
  firstIndex = indices[0]
  
  values = []
  modulo = -1
  if firstIndex.find('A') != -1:# No category for speed: 2A, 4A, 6A and 8A
    modulo = 2
  if firstIndex.find('B') != -1:# Three vehicle categories for speed: 8B, 16B, 24B and 32B
    modulo = 8
  if firstIndex.find('C') != -1:# Six vehicle categories for speed: 12C, 24C, 36C and 48C
    modulo = 12

  for index in indices:
    value = int(index[:-1])
    if value < 200 and value % modulo == 0:
      speed = float(rows.loc[(rows['index'] == index)].avgVehicleSpeed)
      #print speed
      if speed >= 0: 
        values.append(speed)
  return  stats.hmean(values)

def getIntensity(timeandtype, location, time):  
  rows = timeandtype.loc[(timeandtype.periodStart == time)]
  indices = rows['index'].unique()
  firstIndex = indices[0]
  
  values = []
  modulo = -1
  offset =0
  if firstIndex.find('A') != -1:# No category for flow: 1A, 3A, 5A and 7A
    modulo = 2
    offset = 1
  if firstIndex.find('B') != -1:# Three vehicle categories for flow: 4B, 12B, 20B and 28B
    modulo = 8
    offset = 4
  if firstIndex.find('C') != -1:# Six vehicle categories for flow: 6C, 18C, 30C, 42 and 54C
    modulo = 12
    offset = 6

  for index in indices:
    value = int(index[:-1])
    if value < 200 and (value + offset) % modulo == 0:
      flow = float(rows.loc[(rows['index'] == index)].avgVehicleFlow)
      #print flow
      if flow >= 0: 
        values.append(flow)
  return  sum(values)


# Make a map of locations with their coords
sf = shapefile.Reader("Telpunten_20170926.shp")
records = sf.records()
shapes = sf.shapes()
locationsByName = {}
for j in range(0,len(records)):
  name = records[j][2]
  lon =  shapes[j].points[0][0]
  lat =  shapes[j].points[0][1]
  locationsByName[name] = [lat, lon]

"""

flowTable = pandas.read_csv('accident20151230_intensiteit_00001.csv')
speedTable = pandas.read_csv('accident20151230_snelheid_00001.csv')
#print getIntensity(flowTable, 'RWS01_MONIBAS_0020vwm0558ra', '2015-12-31 23:45:00');
#print getSpeed(speedTable, 'RWS01_MONIBAS_0020vwm0558ra', '2015-12-31 23:45:00');

locations = speedTable.measurementSiteReference.unique()
dates = speedTable.periodStart.unique()
print len(locations)
print len(dates)
#for loc in locations:
loc = 'RWS01_MONIBAS_0020vwm0558ra'

timeandtypespeed = speedTable.loc[(speedTable.measurementSiteReference == loc)]
timeandtypeflow = flowTable.loc[(flowTable.measurementSiteReference == loc)]
for time in dates: # Note localtime used , not UTC
  print time, loc, locationsByName[loc], getIntensity(timeandtypeflow, loc, time), getSpeed(timeandtypespeed, loc, time)
"""

measurements = {}
measurements['RWS01_MONIBAS_0020vwm0558ra'] = {}
measurements['RWS01_MONIBAS_0020vwm0558ra']['lon'] = 5
measurements['RWS01_MONIBAS_0020vwm0558ra']['lat'] = 52
measurements['RWS01_MONIBAS_0020vwm0558ra']['time'] = '2015-12-31 23:45:00'
measurements['RWS01_MONIBAS_0020vwm0558ra']['speed'] = 52
measurements['RWS01_MONIBAS_0020vwm0558ra']['flow'] = 52

## Write NetCDF ##
"""
netcdf Amsterdam20170314 {
dimensions:
        station = 1110 ;
        time = 360 ;
        distance = 1110 ;
variables:
        double lat(station) ;
                lat:units = "degrees_north" ;
        double lon(station) ;
                lon:units = "degrees_east" ;
        int station(station) ;
        double time(time) ;
                time:units = "seconds since 1970-01-01 00:00:00" ;
                time:standard_name = "time" ;
        float flow(station, time) ;
        float speed(station, time) ;
        float distance(distance) ;
        short roadId(station) ;
                roadId:flag_meanings = "A1R A1L A10L A10R A4L A4R A9L A2R A2L " ;
                roadId:flag_values = 0s, 1s, 2s, 3s, 4s, 5s, 6s, 7s, 8s ;
                roadId:valid_range = 0s, 9s ;

// global attributes:
                :featureType = "timeSeries" ;
}
"""

fileOutName="ndw_speed_intensity.nc"

latvar = []
lonvar = []
timevardata = []
station = np.array([], dtype='object')

for loc in measurements:
  latvar.append(measurements[loc]['lat'])
  lonvar.append(measurements[loc]['lon'])
  inputdate = measurements[loc]['time'] +'CEST'
  date = dateutil.parser.parse(inputdate)#,"%Y-%m-%d %M:%H:%S")
  utctimestring =  time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.mktime(date.timetuple())))
  netcdfDate = netCDF4.date2num(dateutil.parser.parse(utctimestring), "seconds since 1970-01-01 00:00:00")
  timevardata.append(netcdfDate)
  station = np.append(station,loc)


numpoints=len(station)


ncfile = netCDF4.Dataset(fileOutName,'w')
obs_dim = ncfile.createDimension('obs', numpoints)     # latitude axis
time_dim=ncfile.createDimension('time', 1)

lat = ncfile.createVariable('lat', 'd', ('obs'))
lat.units = 'degrees_north'
lat.standard_name = 'latitude'
lon = ncfile.createVariable('lon', 'd', ('obs'))
lon.units = 'degrees_east'
lon.standard_name = 'longitude'

timevar =  ncfile.createVariable('time', 'd', ('time'))
timevar.units="seconds since 1970-01-01 00:00:00"
timevar.standard_name='time'

floatVar = ncfile.createVariable('station',str,('obs'))
floatVar.units = '-'
floatVar.standard_name = 'station'


lat[:] = [latvar]
lon[:] = [lonvar]
timevar[:] = [timevardata]

floatVar[:] = station


ncfile.featureType = "timeSeries";
ncfile.Conventions = "CF-1.4";
ncfile.close()
