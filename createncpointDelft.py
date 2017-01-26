import datetime
import netCDF4
import numpy as np
from random import randint



fileOutName="TUDExample2.nc"


latvar = []
lonvar = []
pointvar = []
speedVar = []
flowVar = []
distVar = []
timevar = []




#latvar.append( 51.913368);
#lonvar.append( 6.294848);
#pointvar.append(1);
latvar.extend( [52.090825, 52.090825]);
lonvar.extend( [5.122388,5.18]);
pointvar.extend([1,2]);
speedVar.extend([55,66]);
flowVar.extend([1500,1800]);
distVar.extend([44,99])
numpoints=len(pointvar)


ncfile = netCDF4.Dataset(fileOutName,'w')
obs_dim = ncfile.createDimension('obs', numpoints)     # latitude axis
time_dim=ncfile.createDimension('time', 2)
detector_dim=ncfile.createDimension('detectorDist', 2)

lat = ncfile.createVariable('lat', 'd', ('obs'))
lat.units = 'degrees_north'
lat.standard_name = 'latitude'
lon = ncfile.createVariable('lon', 'd', ('obs'))
lon.units = 'degrees_east'
lon.standard_name = 'longitude'

dist = ncfile.createVariable('distance', 'd', ('obs'))
dist.units = 'meters'
dist.standard_name = 'distance'

speed = ncfile.createVariable('speed', 'd', ('obs'))
speed.units = 'km/h'
speed.standard_name = 'kilometer_per_hour'

flow = ncfile.createVariable('flow', 'd', ('obs'))
flow.units = 'veh/h/lane'
flow.standard_name = 'vehicle_per_hour_per_lane'

timevar =  ncfile.createVariable('time', 'd', ('time'))
timevar.units="seconds since 1970-01-01 00:00:00"
timevar.standard_name='time'

#floatVar = ncfile.createVariable('Vethuizen','f4',('obs'))
#floatVar.units = 'km'
#floatVar.standard_name = 'distance'


lat[:] = [latvar]
lon[:] = [lonvar]
speed[:] = [speedVar]
flow[:] = [flowVar]
dist[:] = [distVar]

test  = netCDF4.date2num(datetime.datetime.now(), "seconds since 1970-01-01 00:00:00")

times = [datetime.datetime.now(), datetime.datetime.now() - datetime.timedelta(minutes=20)]

timevar[:] = np.array(times, dtype='datetime64[s]')
#timevar[:] = , "seconds since 1970-01-01 00:00:00")

#floatVar[:] = pointvar


ncfile.featureType = "timeSeries";
ncfile.Conventions = "CF-1.4";
ncfile.close()
