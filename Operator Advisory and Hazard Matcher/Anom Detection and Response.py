# Load helper functions and files
# Import Libraries # 
import pandas as pd
import numpy as np
from datetime import datetime
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import math
import copy
import os
import file_read as fr

# Name - Name, Reading - Numerical Value, State- 0 to 3, Anomstate - 0 to 3, Alarms - levels - UNUSED PRESENTLY
class transmitter:
    def __init__(name, trans, reading, state, anomstate, alarms):
        name.trans = trans
        name.reading = reading
        name.state = state
        name.anomstate = anomstate
        name.alarms = alarms

def predicted_val(y_value_ind,x_value_ind, regressions, xval):
    output = 0
    for i in range(len(regressions)):
        if (regressions[i][1] == x_value_ind 
            and regressions[i][0] == y_value_ind 
            and regressions[i][0] != regressions[i][1] 
            and regressions[i][1] != regressions[i][0]):
            output = regressions[i][2] * ((float(xval)) ** 3) + regressions[i][3] * ((float(xval)) ** 2) + regressions[i][4] * (float(xval)) + regressions[i][5]
    return output

# Load Logs and Regressions # 
alarm_list = fr.path_read_excel('Raw Data/Alarm List.xlsx').to_numpy()

data = fr.path_read_excel('Raw Data/Data Test 6.xlsx').to_numpy()
col = int(data.size/len(data))
print(str(data[1,0:5]))

regressions = fr.path_read_excel('Raw Data/Regressions.xlsx').to_numpy()
total_regresssions = len(regressions)

# Initialise transmitters
transmitters = []
transmitter_names = []
for i in range(1,len(alarm_list)):
    variable_name = alarm_list[i][0]
    locals()[variable_name] = transmitter(variable_name,0,0,'A',alarm_list[i][1:5])
    transmitters.append(locals()[variable_name])
    transmitter_names.append(alarm_list[i][0])

print(col)
print(len(transmitter_names))
print(len(transmitters))

# Error state identification

# Load error states
error_states = fr.path_read_excel("Raw Data/Node 8a2 C and E diagram.xlsx").to_numpy()
print(error_states[1])

error_transmitter = []
error_conditions = []
for p in range(len(error_states)):
    trans = error_states[p][1].split(',')
    conds = error_states[p][2].split(',')
    error_transmitter.append(trans)
    error_conditions.append(conds)



# Load data
transmitter_time_trace = {}
transmitter_time_errors = {}
error_transmitter_time = {}
for i in range(1,len(data)): 
    transmitter_1 = []
    transmitter_error_1 = []
    error_transmitter_1 = []
    
    for j in range(1,12):
    # name, trans, reading, state, anomstate, alarms
        transmitter = [alarm_list[j][0],data[i][j],0,'A',list(alarm_list[j][1:5])]
        if data[i][j] > alarm_list[j][2]:
            transmitter[2] = 1
        elif data[i][j] < alarm_list[j][3]:
            transmitter[2] = 2
        elif data[i][j] != 0:
            transmitter[2] = 3
        transmitter_1.append(transmitter)
        for k in range(len(transmitter_names)):
            p = j - 1
            if transmitter_names[p] != transmitter_names[k]:
                pred_value = predicted_val(transmitter_names[p], transmitter_names[k], regressions, data[i][k+1])
            else:
                pred_value = data[i][j]
            error_percent = 0
            if data[i][j] != 0 and data[i][k+1] != 0:
                error = (pred_value - data[i][j])/data[i][j]
                error_percent = 100 * error
            if error_percent > 40:
                transmitter[3] = 'B'
                continue
            elif error_percent < -40:
                transmitter[3] = 'C'
                continue
        state = str(transmitter[2]) + str(transmitter[3])
        if transmitter[3] != 'A':
            transmitter_error_1.append(transmitter[0])
            error_transmitter_1.append(state)
    transmitter_time_trace[data[i][0]] = transmitter_1
    transmitter_time_errors[data[i][0]] = transmitter_error_1 
    error_transmitter_time[data[i][0]] = error_transmitter_1

times = list(transmitter_time_trace.keys())
print(transmitter_time_trace["09-11-2023 10:39:30"])
print(transmitter_time_errors["09-11-2023 10:39:30"])
print(error_transmitter_time["09-11-2023 10:39:30"])

# Error state identification

# Load error states
error_list = fr.path_read_excel("Raw Data/Node 8a2 C and E diagram.xlsx")
error_states = error_list.to_numpy()

error_trans = []
error_conds = []
for p in range(len(error_states)):
    trans = error_states[p][1].split(',')
    conds = error_states[p][2].split(',')
    error_trans.append(trans)
    error_conds.append(conds)


# Glitches to solve...many false positives. Existing functionality is for a single node only, requires enhancement
for key in transmitter_time_trace:
    for j in range(1,len(error_states)):
        if len(error_trans[j]) == len(error_transmitter_time[key]):
            errormatches = 0
            for q in range(len(error_trans[j])):
                if error_transmitter_time[key][q] in error_conds[j][q]:
                    errormatches += 1
            if errormatches == len(error_trans[j]):
                print("PROBLEM AT " + key)
                print("Cause: " + error_states[j][3])
                print("Remedy: " + error_states[j][4])
                print("Time to consequence: " + error_states[j][5] + '\n')