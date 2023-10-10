# IMPORTANT TO DOs: Clean code, optimise algos, add comments
# Import Libraries # 
import pandas as pd
import numpy as np
from datetime import datetime
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import math
import copy

# Load IO Log # 
IOlog = pd.read_excel('IO log sample.xlsx')
time_interval = IOlog.shape[0]
print(time_interval)
# Size sheet
data2 = IOlog.to_numpy()
data = np.flip(data2, axis=0)
size = data.size
col = int(size/len(data))
row = len(data)
print(col)
print(row)
print(str(data[1:5,3]))

# Load regression curves
reg = pd.read_excel('Regressions.xlsx')
regressions = reg.to_numpy()
dims2 = regressions.size
totalregs = len(regressions)
print(str(regressions[1,1:7]))

# Load dataset
dataset = pd.read_excel('Data Test 5.xlsx')
data3 = dataset.to_numpy()
totalrows = len(data3)
print(totalrows)
print(str(data3[1,0:5]))

# Time converter
def convert_time(time_strings):
    time_format = "%m-%d-%Y %H:%M:%S"
    base_time = datetime.strptime(time_strings[0], time_format)
    time_in_minutes = [(datetime.strptime(t, time_format) - base_time).total_seconds() / 60 for t in time_strings]
    return time_in_minutes

# Initialise controllers and instruments - PRESENTLY HARDCODED, NEED TO MOVE TO EXCEL DATAFRAME!
controllerlist = [["LIC101",0,0,0,0,0], ["LIC108",4,56.5,0,0,0], ["FIC103",0,0,0,0,0], ["FIC108",0,0,0,0,0], ["FCV200",1.5,20,0,0,0], ["FIC201",1.5,20,0,0,0]]
controllers = {"LIC101" : [0,0,0,0,0], "LIC108" : [4,0,0,0,0], "FIC103": [0,0,0,0,0], "FIC108": [0,0,0,0,0], "FCV200": [1.5,20,0,0,0], "FIC201": [1.5,20,0,0,0]}
controllers["LIC108"][0] = 1
print(controllers)
pumps = {"J100": [0,0], "J101a": [0,0], "J101b_": [0,0], "J102": [0,0], "J103": [0,0], "J104": [0,0], "J105": [0,0], "J106": [0,0], "FCV200" : [0,0]}
print(len(controllers))

# Initialise arrays
ManPumpSpeedchanges = []
Pchanges = []
Ichanges = []
pumpmodechanges = []
controllerSPchanges = []
ManPumpSpeedchangesT = []
PchangesT = []
IchangesT = []
pumpmodechangesT = []
controllerSPchangesT = []
convals = []
controlchangesT = []

# Run through whole IO log
for i in range(2,len(data)-1):

# Pump change detection
    timechange = str(data[i,0])
    item = str(data[i,1])
    inputlog = str(data[i,3])
    
    if inputlog[0:10] == "HSICmd.Man":
        if inputlog[10:12] == "SP":
            speedchange = inputlog[12:]
            speeds = speedchange.split()
            speeds.append(timechange)
            b = speeds[2]
            pumps[item][0] = int(b)
            speeds.pop(1)
            ManPumpSpeedchanges.append(speeds)
            ManPumpSpeedchangesT.append(timechange)

        # Detect pump mode - TO DO: CHANGE OUTPUT DEPENDING ON REQUIREMENT
        elif inputlog[7:10] == "Man":
            pumps[item][1] = int(0)
            pumpmodechanges.append(["Man",timechange])
            pumpmodechangesT.append(timechange)
    
    elif inputlog == "HSICmd.Auto False -> True ":
        pumps[item][1] = int(1)
        pumpmodechanges.append(["Auto",timechange])
        pumpmodechangesT.append(timechange)
                
    # SP change
    elif inputlog[0:9] == "HSICmd.SP":
        setptchange = inputlog[18:]
        setpts = setptchange.split()
        sp1 = setpts[0]
        sp2 = setpts[2]
        controllers[item][4] = float(sp2)
        controllerSPchanges.append([item,sp2,timechange])
        controllerSPchangesT.append(timechange)
    
    # Controller changes - types
    elif inputlog[0:14] == "InteractionPar":
        
        if inputlog[20:34] == "ControllerType":
            modechange = inputlog[35:]
            modes = modechange.split()
            mode1 = modes[0]
            mode2 = modes[2]
            templist1 = copy.deepcopy(controllerlist)
            for j in range(len(templist1)):
                if item == templist1[j][0]:
                    templist1[j][4] = int(mode2)
            controllerlist = templist1
            convals.append(templist1)
            controlchangesT.append(timechange)
        
        # P changes
        elif inputlog[15:24] == "Main.Gain":
            gainchange = inputlog[25:]
            gains = gainchange.split()
            P2 = gains[2]
            gains.append(timechange)
            gains.pop(1)
            gains.insert(0,item)
            
            templist2 = copy.deepcopy(controllerlist)
            for j in range(len(templist2)):
                if item == templist2[j][0]:
                    templist2[j][1] = float(P2)
            controllerlist = templist2
            convals.append(templist2)
            controlchangesT.append(timechange)

            Pchanges.append(gains)
            PchangesT.append(timechange)
            
        # I changes
        elif inputlog[15:22] == "Main.Ti":
            intchange = inputlog[23:]
            ints = intchange.split()
            Ti1 = ints[0]
            Ti2 = ints[2]
            controllers[item][1] = Ti2
            ints.append(timechange)
            ints.pop(1)
            ints.insert(0,item)
            mode = controllers[item][3]
            Ichanges.append(ints)
            IchangesT.append(timechange)
            
            templist3 = copy.deepcopy(controllerlist)
            for j in range(len(templist3)):
                if item == templist3[j][0]:
                    templist3[j][2] = float(Ti2)  
            controllerlist = templist3
            convals.append(templist3)
            controlchangesT.append(timechange)

print(convals)

# Oracle mode functions
# Time int = Range

testset = pd.read_excel('PI response tester.xlsx')
test = testset.to_numpy()
print(test[0][2])
pumpres = []
times = []
for i in range(len(test)):
    pumpres.append(test[i][0])
    times.append(test[i][4])
    
def FOPTD_solver(Kp,tau,step1,step2,timedelay,valuerange2,timerange2):
    stepchange = step2 - step1
    processvars = []
    for i in range(len(timerange2)):
        if timerange2[i] > timedelay:
            term = 1-math.exp(-(timerange2[i] - timedelay)/tau)
            processvar2 = term * stepchange * Kp + valuerange2[0]
        else:
            processvar2 = valuerange2[0]
        processvars.append(processvar2)
    return processvars

def predicted_val(yvalueind,xvalueind, regressions, xval):
    for i in range(len(regressions)):
        if regressions[i][1] == xvalueind and regressions[i][0] == yvalueind:
            output = regressions[i][2] * ((float(xval)) ** 3) + regressions[i][3] * ((float(xval)) ** 2) + regressions[i][4] * (float(xval)) + regressions[i][5]
    return output

# NB: SOME BUGS. PLEASE FIX
def PI_solver(P,I,setpointcv,timeint,deltaT,startvalue,Tdsystem,initialpv):

    Pprime = 1*P
    errors = []
    initialval = startvalue
    operrorcorrection = -0.428*(setpointcv - startvalue) - 0.6214
    for i in range(I):
        errorin = int(0)
        errors.append(errorin)
    lagvalues = []
    for i in range(Tdsystem):
        lagvalues.append(float(initialpv))
    
    processvars = []
    for i in range(len(timeint)):
        error = startvalue - setpointcv
        errors.append(error)
        errors.pop(0)
        integral = sum(errors)
        op = setpointcv + Pprime*(error + (1/I)*integral)
        processvar = (75.5 - op)/1.3
        
        if processvar > 100:
            processvar = 100
        if processvar < 0:
            processvar = 0
        
        if i > Tdsystem:
            lagvalues.append(processvar)
            lagvalues.pop(0)
            lastval = len(lagvalues) - 1
            response = FOPTD_solver(-1.22,135,lagvalues[0],lagvalues[1],0,[startvalue,0],timeint) 
            initialpv = lagvalues[0]
            level = response[Tdsystem]
            levelreal = level - operrorcorrection
        else:
            level = initialval
            levelreal = level
        processvars.append(levelreal)
        startvalue = level
    return processvars

values = [41.9,1]

levels = FOPTD_solver(1.22,30,15,20,15,values,times)
# P,I,setpointcv,timeint,deltaT,startvalue,Tdsystem,initialpv
J101b = PI_solver(-4,75,31,times,1,41,20,19)

FT108 = []
FT109 = []
LT108 = []

def regressor(yvalueind,xvalueind, regressions, xvallist):
    values = []
    for i in range(len(regressions)):
        if regressions[i][1] == xvalueind and regressions[i][0] == yvalueind:
            for j in range(len(xvallist)):
                output = regressions[i][2] * ((float(xvallist[j])) ** 3) + regressions[i][3] * ((float(xvallist[j])) ** 2) + regressions[i][4] * (float(xvallist[j])) + regressions[i][5]
                values.append(output)
    return values

plt.plot(times,J101b)

# Solver proper - EXTREMELY MESSY, WOULD BE REALLY NICE IF SOMEONE COULD MAKE THIS MORE CONCISE!

# Bug on this one to fix - if the seconds number = 59 it rounds wrong, rounded down to 57 as a temp fix
def round_to_nearest_3_seconds(time):
    seconds = time.second
    remainder = seconds % 3
    if remainder < 2:
        rounded_seconds = seconds - remainder
    else:
        rounded_seconds = seconds + (3 - remainder)
        if rounded_seconds == 60:
            rounded_seconds = 57
    return time.replace(second=rounded_seconds, microsecond=0)

timearray = []
for i in range(301):
    timearray.append(i)
print(timearray[2])

leveltraces = []
flowtraces = []

# FOPTD prediction on any manual pump changes
for p in range(len(ManPumpSpeedchangesT)):
    time = datetime.strptime(ManPumpSpeedchangesT[p], "%Y-%m-%d %H:%M:%S")
    timeform = round_to_nearest_3_seconds(time)
    timeformmod = timeform.strftime("%m-%d-%Y %H:%M:%S")
    for g in range(len(data3)):
        if timeformmod == data3[g][0]:
            print("Found!", timeformmod)
            startvalue = data3[g][3]
            startvals = [startvalue,0]
            start = float(ManPumpSpeedchanges[p][0])
            end = float(ManPumpSpeedchanges[p][1])
            predlevels = levels = FOPTD_solver(-1.22,75,start,end,15,startvals,timearray)
            leveltraces.append(predlevels)
            flows = regressor("FT108","LT108",regressions,predlevels)
            flowtraces.append(flows)

# Pump mode updater - Semiworking, TBC what to do with this

for q in range(len(pumpmodechangesT)):
    time = datetime.strptime(pumpmodechangesT[q], "%Y-%m-%d %H:%M:%S")
    timeform2 = round_to_nearest_3_seconds(time)
    timeformmod2 = timeform2.strftime("%m-%d-%Y %H:%M:%S")
    for g in range(len(data3)):
        if timeformmod2 == data3[g][0]:
            print("Found!", timeformmod2)

# SP changes

setptsimlist = []

for r in range(len(controlchangesT)):
    time3 = datetime.strptime(controlchangesT[r], "%Y-%m-%d %H:%M:%S")
    timeform3 = round_to_nearest_3_seconds(time3)
    timeformmod3 = timeform3.strftime("%m-%d-%Y %H:%M:%S")
    for g in range(len(data3)):
        levelactual = []
        if timeformmod3 == data3[g][0]:
            cont = controllerSPchanges[r][0]
            print(timeformmod3)
            for q in range(len(controllerlist)):
                if convals[r][q][0] == cont:
                    gain = -convals[r][q][1]
                    contint = int(convals[r][q][2])
                    setpt = float(controllerSPchanges[r][1])
                    inival = float(data3[g][3])
                    inival2 = (75.5 - inival)/1.3
                    print("Hello there!", gain,contint,setpt,inival,inival2)
                    simvals = PI_solver(gain,contint,setpt,timearray,3,inival,19,inival2)
                    setptsimlist.append(simvals)
                    
# P,I,setpointcv,timeint,deltaT,startvalue,Tdsystem,initialpv

plt.plot(timearray,setptsimlist[-2])