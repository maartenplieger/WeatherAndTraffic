import pandas
import netCDF4

from datetime import date, timedelta, datetime, time

filePath = "../KNMI-DiTTLab-SWOV/ExportOngevalsData.csv"
fileTest = "test.csv"

v1 = []
v2 = []
v3 = []
v4 = []


test = pandas.read_csv(fileTest)

def padMinute(x):
    x =int(x)
    if (x <= 9):
        x = str.zfill(str(x), 2)
    return str(x)



def tenMin_datetime(dt):
    reminder = (dt.minute%10)
    if reminder <=4:
        minute = dt.minute+0
    else:
        minute =10-reminder+dt.minute
    return dt.replace(minute=0, second=0)+timedelta(minutes=minute)


test["hour"] = test['Uur'].map(lambda x: str(x).split("-")[1].split(".")[0])
test["day"] = test["datum"].map(lambda x: str(x)[:2])
test["month"] = test["datum"].map(lambda x: str(x)[2:5])
test["year"] = test["datum"].map(lambda x: "20"+str(x)[5:])
test["minute"] = test["minuut"].map(lambda x: padMinute(x))
test["TimeStamp"] = pandas.to_datetime(test["year"]+test["month"]+test["day"]+test["hour"]+test["minute"], format='%Y%b%d%H%M')
test["TimeRounded"] = test["TimeStamp"].map(lambda x: tenMin_datetime(x))


fileOutName="createncpoint.nc"



latvar = []
lonvar = []
ernong = []
nDeath = []
nHospital = []
aardong = []


print(test.shape)


latvar.append(test["X"].values)
lonvar.append(test["Y"].values)
ernong.append(test["ernong"].values)
nDeath.append(test["N_Slacht_dood"].values)
nHospital.append(test["N_Slacht_Zh"].values)
aardong.append(test["Aardong"].values)

numpoints=test.shape[0]


ncfile = netCDF4.Dataset(fileOutName,'w')
obs_dim = ncfile.createDimension('obs', numpoints)     # latitude axis
time_dim=ncfile.createDimension('time', numpoints)

lat = ncfile.createVariable('lat', 'd', ('obs'))
lat.units = 'degrees_north'
lat.standard_name = 'latitude'
lon = ncfile.createVariable('lon', 'd', ('obs'))
lon.units = 'degrees_east'
lon.standard_name = 'longitude'

timevar =  ncfile.createVariable('time', 'd', ('time'))
timevar.units="seconds since 1970-01-01 00:00:00"
timevar.standard_name='time'

stringDim = ncfile.createDimension('stringDim',numpoints)
ErnongVar = ncfile.createVariable('Ernong',str, ('stringDim'))
NiveaukopVar = ncfile.createVariable('Niveaukop',str, ('stringDim'))

N_Slacht_doodVar = ncfile.createVariable('NSlachtDood', 'u8', ('stringDim'))
N_Slacht_ZhVar = ncfile.createVariable('NSlachtZh','u8', ('stringDim'))
AardongVar = ncfile.createVariable('Aardong',str, ('stringDim'))
LoctyponVar = ncfile.createVariable('Loctypon',str, ('stringDim'))
N_PersonenautoVar = ncfile.createVariable('NPersoneauto','u8', ('stringDim'))
N_Brom_snorfietsVar = ncfile.createVariable('NBromSnorfiets','u8', ('stringDim'))
N_FietsVar = ncfile.createVariable('NFiets','u8', ('stringDim'))
N_VoetgangerVar = ncfile.createVariable('NVoetgangers','u8', ('stringDim'))



#floatVar.units = 'km'
#floatVar.standard_name = 'distance'


lat[:] = [latvar]
lon[:] = [lonvar]
#timevar[:] = test["TimeRounded"].values

ErnongVar[:] = ernong[0]
N_Slacht_doodVar [:] = [nDeath]
N_Slacht_ZhVar [:] = [nHospital]
AardongVar [:] = aardong[0]


ncfile.featureType = "timeSeries";
ncfile.Conventions = "CF-1.4";
ncfile.close()