import pandas
import netCDF4
import numpy as np
import pyproj

from datetime import date, timedelta, datetime, time



## Padding of the minute with a zero if represented by one digit.
## For non compliant format (i.e., "Onbekend" string situation) a 0 minute is set.
#   @param string representing the minute.
#   @return padded string
def padMinute(x):
    try:
        x =int(x)
        if (x <= 9):
            x = str.zfill(str(x), 2)
    except ValueError:
        #print("Error minute:"+x)
        x=0
    return str(x)


## The time is approximated to the closest 10-minute value.
#   @param datetime variable.
#   @return datetime variable approximated.
def tenMin_datetime(dt):
    reminder = (dt.minute%10)
    if reminder <=4:
        minute = dt.minute-reminder
    else:
        minute =10-reminder+dt.minute
    returnVal = dt.replace(minute=0, second=0)+timedelta(minutes=minute)
    #dt = returnVal
    return returnVal


## Hours are read from the string format and if in the right format parsed.
## For non compliant format (i.e., "Onbekend" string situation) a 0 hour is set.
#   @param string representing the minute.
#   @return padded string
def convertHour(x):
    xx = ""
    try:
        xx = str(x).split("-")[1].split(".")[0]
    except IndexError:
        #print("error:" + x)
        xx = str(0)
    return(xx)




## Minute field (original from the dataset) is check for non compliant values.
#   @param string representing the minute.
#   @return string with TRUE if correct format, FALSE otherwise.
def isCorrect(x):
    if x=="Onbekend":
        x="FALSE"
    else:
        x="TRUE"
    return(x)


def createNetCDF(dataFrame, fileNumber):
    fileOutName = "/nobackup/users/pagani/weatherTraffic/SWOVDataFull"+str(fileNumber)+".nc"

    ##definition of the projections
    wgs84 = pyproj.Proj("+init=EPSG:4326")
    epsg28992 = pyproj.Proj("+init=EPSG:28992")


    ##list variables to store data
    latvar = []
    lonvar = []
    ernong = []
    nDeath = []
    nHospital = []
    aardong = []
    loctypon = []
    nCars = []
    nBikes = []
    nScooters = []
    nPedestrians = []
    niveauKop = []
    timeNC = []
    errorInDateTime = []

    # print(test.shape)

    ##lists are filled with values of the data frame
    [lon, lat] = pyproj.transform(epsg28992, wgs84, dataFrame["X"].values, dataFrame["Y"].values)
    latvar.append(lat)
    lonvar.append(lon)
    ernong.append(dataFrame["ernong"].values)
    nDeath.append(dataFrame["N_Slacht_dood"].values)
    nHospital.append(dataFrame["N_Slacht_Zh"].values)
    aardong.append(dataFrame["Aardong"].values)
    loctypon.append(dataFrame["loctypon"].values)
    nCars.append(dataFrame["N_Personenauto"].values)
    nBikes.append(dataFrame["N_Fiets"].values)
    nScooters.append(dataFrame["N_Brom_snorfiets"].values)
    nPedestrians.append(dataFrame["N_Voetganger"].values)
    niveauKop.append(dataFrame["Niveaukop"].values)
    timeNC.append(pandas.to_datetime(dataFrame["TimeRounded"].values))
    errorInDateTime.append(dataFrame["NoError"].values)

    # print(pandas.to_datetime(timeNC[0]).strftime("%s"))
    # print(timeNC)
    # print(test["TimeRounded"].values)



    numpoints = dataFrame.shape[0]

    ##NetCDF file and variables are created

    ncfile = netCDF4.Dataset(fileOutName, 'w')
    obs_dim = ncfile.createDimension('obs', numpoints)
    time_dim = ncfile.createDimension('time', 1)

    lat = ncfile.createVariable('lat', 'd', ('obs'))
    lat.units = 'degrees_north'
    lat.standard_name = 'latitude'
    lon = ncfile.createVariable('lon', 'd', ('obs'))
    lon.units = 'degrees_east'
    lon.standard_name = 'longitude'

    timevar = ncfile.createVariable('time', 'd', ('time'))
    timevar.units = "seconds since 1970-01-01 00:00:00"
    timevar.standard_name = 'time'

    stringDim = ncfile.createDimension('stringDim', numpoints)
    ErnongVar = ncfile.createVariable('Ernong', str, ('stringDim', 'time'))
    NiveaukopVar = ncfile.createVariable('Niveaukop', str, ('stringDim', 'time'))

    N_Slacht_doodVar = ncfile.createVariable('NSlachtDood', 'u8', ('stringDim', 'time'))
    N_Slacht_ZhVar = ncfile.createVariable('NSlachtZh', 'u8', ('stringDim', 'time'))
    AardongVar = ncfile.createVariable('Aardong', str, ('stringDim', 'time'))
    LoctyponVar = ncfile.createVariable('Loctypon', str, ('stringDim', 'time'))
    N_PersonenautoVar = ncfile.createVariable('NPersoneauto', 'u8', ('stringDim', 'time'))
    N_Brom_snorfietsVar = ncfile.createVariable('NBromSnorfiets', 'u8', ('stringDim', 'time'))
    N_FietsVar = ncfile.createVariable('NFiets', 'u8', ('stringDim', 'time'))
    N_VoetgangerVar = ncfile.createVariable('NVoetgangers', 'u8', ('stringDim', 'time'))
    errorInDateTimeVar = ncfile.createVariable('TimeIsOK', str, ('stringDim', 'time'))

    ##NetCDF variables and file are filled with the list data

    lat[:] = [latvar]
    lon[:] = [lonvar]
    timevar[:] = np.array(timeNC[0][0], dtype='datetime64[s]')
    ErnongVar[:] = ernong[0]
    NiveaukopVar[:] = niveauKop[0]
    N_Slacht_doodVar[:] = [nDeath]
    N_Slacht_ZhVar[:] = [nHospital]
    AardongVar[:] = aardong[0]
    LoctyponVar[:] = loctypon[0]
    N_PersonenautoVar[:] = [nCars]
    N_Brom_snorfietsVar[:] = [nScooters]
    N_FietsVar[:] = [nBikes]
    N_PersonenautoVar[:] = [nCars]
    N_VoetgangerVar[:] = [nPedestrians]
    errorInDateTimeVar[:] = errorInDateTime[0]

    ncfile.featureType = "timeSeries"
    ncfile.Conventions = "CF-1.4"
    ncfile.close()






filePath = "../KNMI-DiTTLab-SWOV/ExportOngevalsData.csv"
fileTest = "test.csv"

##read in the csv data as dataframe
dataFrame = pandas.read_csv(filePath)

dataFrame["hour"] = dataFrame['Uur'].map(lambda x: convertHour(x))
dataFrame["day"] = dataFrame["datum"].map(lambda x: str(x)[:2])
dataFrame["month"] = dataFrame["datum"].map(lambda x: str(x)[2:5])
dataFrame["year"] = dataFrame["datum"].map(lambda x: "20" + str(x)[5:])
dataFrame["minute"] = dataFrame["minuut"].map(lambda x: padMinute(x))
dataFrame["NoError"] = dataFrame["minuut"].map(lambda x: isCorrect(x))
timeStampToConvert = dataFrame["year"] + dataFrame["month"] + dataFrame["day"] + dataFrame["hour"] + dataFrame["minute"]
dataFrame["TimeStamp"] = pandas.to_datetime(timeStampToConvert, format='%Y%b%d%H%M', unit='s')
#print(test["TimeStamp"].values)
dataFrame["TimeRounded"] = dataFrame["TimeStamp"].map(lambda x: tenMin_datetime(x))


test = dataFrame.sort(["TimeRounded"])

 #= test.groupby("TimeRounded")

iterVar = 0

timeGroups = test['TimeRounded'].unique()

for timeSlice in timeGroups:
    testDF = test[test['TimeRounded'] == timeSlice]
    createNetCDF(testDF, iterVar)
    iterVar +=1
    #print(outfilename)
    #df[df['Gene'] == gene].to_csv(outfilename)


# def createNetCDF(dataFrame, fileNumber):
#
#     fileOutName="SWOVData.nc"
#
#
#     ##list variables to store data
#     latvar = []
#     lonvar = []
#     ernong = []
#     nDeath = []
#     nHospital = []
#     aardong = []
#     loctypon = []
#     nCars = []
#     nBikes = []
#     nScooters = []
#     nPedestrians = []
#     niveauKop = []
#     timeNC = []
#     errorInDateTime = []
#
#
#     #print(test.shape)
#
#     ##lists are filled with values of the data frame
#     latvar.append(dataFrame["X"].values)
#     lonvar.append(dataFrame["Y"].values)
#     ernong.append(dataFrame["ernong"].values)
#     nDeath.append(dataFrame["N_Slacht_dood"].values)
#     nHospital.append(dataFrame["N_Slacht_Zh"].values)
#     aardong.append(dataFrame["Aardong"].values)
#     loctypon.append(dataFrame["loctypon"].values)
#     nCars.append(dataFrame["N_Personenauto"].values)
#     nBikes.append(dataFrame["N_Fiets"].values)
#     nScooters.append(dataFrame["N_Brom_snorfiets"].values)
#     nPedestrians.append(dataFrame["N_Voetganger"].values)
#     niveauKop.append(dataFrame["Niveaukop"].values)
#     timeNC.append(pandas.to_datetime(dataFrame["TimeRounded"].values))
#     errorInDateTime.append(dataFrame["NoError"].values)
#
#     # print(pandas.to_datetime(timeNC[0]).strftime("%s"))
#     # print(timeNC)
#     # print(test["TimeRounded"].values)
#
#
#
#     numpoints=dataFrame.shape[0]
#
#
#     ##NetCDF file and variables are created
#
#     ncfile = netCDF4.Dataset(fileOutName,'w')
#     obs_dim = ncfile.createDimension('obs', numpoints)
#     time_dim=ncfile.createDimension('time', numpoints)
#
#     lat = ncfile.createVariable('lat', 'd', ('obs'))
#     lat.units = 'degrees_north'
#     lat.standard_name = 'latitude'
#     lon = ncfile.createVariable('lon', 'd', ('obs'))
#     lon.units = 'degrees_east'
#     lon.standard_name = 'longitude'
#
#     timevar =  ncfile.createVariable('time', 'u8', ('time'))
#     timevar.units="seconds since 1970-01-01 00:00:00"
#     timevar.standard_name='time'
#
#     stringDim = ncfile.createDimension('stringDim',numpoints)
#     ErnongVar = ncfile.createVariable('Ernong',str, ('stringDim'))
#     NiveaukopVar = ncfile.createVariable('Niveaukop',str, ('stringDim'))
#
#     N_Slacht_doodVar = ncfile.createVariable('NSlachtDood', 'u8', ('stringDim'))
#     N_Slacht_ZhVar = ncfile.createVariable('NSlachtZh','u8', ('stringDim'))
#     AardongVar = ncfile.createVariable('Aardong',str, ('stringDim'))
#     LoctyponVar = ncfile.createVariable('Loctypon',str, ('stringDim'))
#     N_PersonenautoVar = ncfile.createVariable('NPersoneauto','u8', ('stringDim'))
#     N_Brom_snorfietsVar = ncfile.createVariable('NBromSnorfiets','u8', ('stringDim'))
#     N_FietsVar = ncfile.createVariable('NFiets','u8', ('stringDim'))
#     N_VoetgangerVar = ncfile.createVariable('NVoetgangers','u8', ('stringDim'))
#     errorInDateTimeVar = ncfile.createVariable('TimeIsOK', str, ('stringDim'))
#
#
#
#     ##NetCDF variables and file are filled with the list data
#
#     lat[:] = [latvar]
#     lon[:] = [lonvar]
#     timevar[:] =  np.array(timeNC[0], dtype='datetime64[s]')
#     ErnongVar[:] = ernong[0]
#     NiveaukopVar[:] = niveauKop[0]
#     N_Slacht_doodVar [:] = [nDeath]
#     N_Slacht_ZhVar [:] = [nHospital]
#     AardongVar [:] = aardong[0]
#     LoctyponVar [:] = loctypon[0]
#     N_PersonenautoVar[:] = [nCars]
#     N_Brom_snorfietsVar[:] = [nScooters]
#     N_FietsVar[:] = [nBikes]
#     N_PersonenautoVar[:] = [nCars]
#     N_VoetgangerVar[:] = [nPedestrians]
#     errorInDateTimeVar[:] = errorInDateTime[0]
#
#
#     ncfile.featureType = "timeSeries"
#     ncfile.Conventions = "CF-1.4"
#     ncfile.close()