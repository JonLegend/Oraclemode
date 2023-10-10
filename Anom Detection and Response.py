# Load helper functions and files
# Import Libraries # 
import pandas as pd
import numpy as np
from datetime import datetime
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import math
import copy

# Name - Name, Reading - Numerical Value, State- 0 to 3, Anomstate - 0 to 3, Alarms - levels - UNUSED PRESENTLY
class transmitter:
    def __init__(name, trans, reading, state, anomstate, alarms):
        name.trans = trans
        name.reading = reading
        name.state = state
        name.anomstate = anomstate
        name.alarms = alarms

def predicted_val(yvalueind,xvalueind, regressions, xval):
    output = 0
    for i in range(len(regressions)):
        if regressions[i][1] == xvalueind and regressions[i][0] == yvalueind and regressions[i][0] != regressions[i][1] and regressions[i][1] != regressions[i][0]:
            output = regressions[i][2] * ((float(xval)) ** 3) + regressions[i][3] * ((float(xval)) ** 2) + regressions[i][4] * (float(xval)) + regressions[i][5]
    return output

# Load Logs and Regressions # 
alarms = pd.read_excel('Alarm List.xlsx')
alarmlist = alarms.to_numpy()
dataset = pd.read_excel('Data Test 6.xlsx')
data = dataset.to_numpy()
col = int(data.size/len(data))
print(str(data[1,0:5]))
reg = pd.read_excel('Regressions.xlsx')
regressions = reg.to_numpy()
totalregs = len(regressions)

# Initialise transmitters
transmitters = []
transnames = []
for i in range(1,len(alarmlist)):
    variable_name = alarmlist[i][0]
    locals()[variable_name] = transmitter(variable_name,0,0,'A',alarmlist[i][1:5])
    transmitters.append(locals()[variable_name])
    transnames.append(alarmlist[i][0])

print(col)
print(len(transnames))
print(len(transmitters))

# Error state identification

# Load error states
errorlist = pd.read_excel("Node 8a2 C and E diagram.xlsx")
errorstates = errorlist.to_numpy()
print(errorstates[1])

errortrans = []
errorconds = []
for p in range(len(errorstates)):
    trans = errorstates[p][1].split(',')
    conds = errorstates[p][2].split(',')
    errortrans.append(trans)
    errorconds.append(conds)

# Load data
transtimetrace = {}
transtimeerrors = {}
errortranstime = {}
for i in range(1,len(data)): 
    transmitter1 = []
    transerror1 = []
    errortrans1 = []
    
    for j in range(1,12):
    # name, trans, reading, state, anomstate, alarms
        transmitter = [alarmlist[j][0],data[i][j],0,'A',list(alarmlist[j][1:5])]
        if data[i][j] > alarmlist[j][2]:
            transmitter[2] = 1
        elif data[i][j] < alarmlist[j][3]:
            transmitter[2] = 2
        elif data[i][j] != 0:
            transmitter[2] = 3
        transmitter1.append(transmitter)
        for k in range(len(transnames)):
            p = j - 1
            if transnames[p] != transnames[k]:
                predvalue = predicted_val(transnames[p], transnames[k], regressions, data[i][k+1])
            else:
                predvalue = data[i][j]
            errorpercent = 0
            if data[i][j] != 0 and data[i][k+1] != 0:
                error = (predvalue - data[i][j])/data[i][j]
                errorpercent = 100 * error
            if errorpercent > 40:
                transmitter[3] = 'B'
                continue
            elif errorpercent < -40:
                transmitter[3] = 'C'
                continue
        state = str(transmitter[2]) + str(transmitter[3])
        if transmitter[3] != 'A':
            transerror1.append(transmitter[0])
            errortrans1.append(state)
    transtimetrace[data[i][0]] = transmitter1
    transtimeerrors[data[i][0]] = transerror1 
    errortranstime[data[i][0]] = errortrans1

times = list(transtimetrace.keys())
print(transtimetrace["09-11-2023 10:39:30"])
print(transtimeerrors["09-11-2023 10:39:30"])
print(errortranstime["09-11-2023 10:39:30"])

# Error state identification

# Load error states
errorlist = pd.read_excel("Node 8a2 C and E diagram.xlsx")
errorstates = errorlist.to_numpy()

errortrans = []
errorconds = []
for p in range(len(errorstates)):
    trans = errorstates[p][1].split(',')
    conds = errorstates[p][2].split(',')
    errortrans.append(trans)
    errorconds.append(conds)


# Glitches to solve...many false positives. Existing functionality is for a single node only, requires enhancement
for key in transtimetrace:
    for j in range(1,len(errorstates)):
        if len(errortrans[j]) == len(errortranstime[key]):
            errormatches = 0
            for q in range(len(errortrans[j])):
                if errortranstime[key][q] in errorconds[j][q]:
                    errormatches += 1
            if errormatches == len(errortrans[j]):
                print("PROBLEM AT " + key)
                print("Cause: " + errorstates[j][3])
                print("Remedy: " + errorstates[j][4])
                print("Time to consequence: " + errorstates[j][5] + '\n')