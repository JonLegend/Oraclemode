# Load helper functions and files
# Import Libraries # 
import pandas as pd
import numpy as np
from datetime import datetime
import scipy.integrate as integrate
import matplotlib.pyplot as plt
import math
import copy


# Load Alarm Files
alarm_f = pd.read_excel('Alarm List.xlsx')
alarm_list = alarm_f.to_numpy()


# Load Regression Files
reg_f = pd.read_excel('Regressions.xlsx')
regressions_list = reg_f.to_numpy()
reg_list_length = len(regressions_list)


# Load Raw Data Files
df = pd.read_excel('Data Test 6.xlsx')
data = df.to_numpy()
data_rows = len(data)
data_cols = np.shape(data)[1]


# Transmitter Object Class
class Transmitter:
    def __init__(self, name, reading, state, anomalousness, alarms):
        self.name = name
        self.reading = reading
        self.state = state                   # 1 = Higher, 2 = Lower, 3 = Expected and Non-Zero
        self.anomalousness = anomalousness   # A = Default, B = +40 % Error, C = -40 % Error
        self.alarms = alarms

    def define_state(self):
        if self.reading > self.alarms[2]:
            self.state = 1
        elif self.reading < self.alarms[3]:
            self.state = 2
        elif self.reading != 0:
            self.state = 3
        return self.state
    
    def define_anomalousness(self, pred_value, y):
        error_dec = (pred_value - y)/y
        error_pc = 100 * error_dec
        if error_pc > 40:
            self.anomalousness = 'B'
        if error_pc < -40:
            self.anomalousness = 'C'
        else:
            self.anomalousness = 'A'
        return str(self.anomalousness)
    
    def give_status(self):
        self.net_status = str(self.state) + str(self.anomalousness)
        return [self.name, self.net_status]



# Forming Transmitter Lists
trans_object_list = []  # Data Adress List
trans_name_list = []    # Data Name List

for i in range(1, len(alarm_list)):
    trans_name = alarm_list[i, 0]
    locals()[trans_name] = Transmitter(trans_name, 0, 0, 'A', alarm_list[i, 1:5])
    trans_object_list.append(locals()[trans_name])
    trans_name_list.append(trans_name)


# Load Error States
error_f = pd.read_excel('Node 8a2 C and E diagram.xlsx')
error_list = error_f.to_numpy()

# Prepare Transmitter and Error Conditions Lists
error_trans_list = []   # List of Affected Transmitter(s) for Each Error
error_cond_list = []    # List of Corresponding Conditions

for i in range(1, len(error_list)):
    error_transmitters = error_list[i, 1].split(',')
    error_conditions = error_list[i, 2].split(',')
    error_trans_list.append(error_transmitters)
    error_cond_list.append(error_conditions)


# Value Predictor Function
def predict_value(y_instr, x_instr, reg_list, x):
    output = 0
    
    for i in range(1, len(reg_list)):
        if reg_list[i, 0] == y_instr and reg_list[i, 1] == x_instr and y_instr != x_instr:
            output = (reg_list[i, 2] * ((float(x)) ** 3)) + (reg_list[i, 3] * ((float(x)) ** 2)) + \
            (reg_list[i, 4] * (float(x))) + reg_list[i, 5]
    return output



# Classifying Raw Data
status_at_time = {}                 # Dictionary with Each Transmitter's Status at Time i
erring_at_time = {}                 # Dictionary with Erring Transmitters at Time i
triggered_at_time = {}              # Dictionary with Trigerred Error Conditions at Time i

for i in range(1, len(data)):       # Changing i changes Timeframe len(data)
    status_at_i = []
    erring_at_i = []
    triggered_at_i = []

    # Define Transmitter Status
    for j in range(1, data_cols):   # Changing j changes Transmitter
        k = j - 1

        target_trans = Transmitter(trans_name_list[k], data[i, j], 0, 'A', alarm_list[j])
        state_at_i = target_trans.define_state()

        #if target_trans.define_state != 3:
            #erring_at_i.append(trans_name_list[k])
        
        for h in range(1, len(trans_name_list)):    # Changing h changes what j is compared against
            if trans_name_list[h] == trans_name_list[k]:
                pred_value = data[i, j]
            else:
                pred_value = predict_value(trans_name_list[k], trans_name_list[h], \
                                           regressions_list, data[i, h+1])

            if data[i, j] != 0 and data[i, h+1] != 0:
                anomalousness_at_i = target_trans.define_anomalousness(pred_value, data[i, j])
                status_at_i.append(target_trans.give_status())

                if anomalousness_at_i != 'A':
                    erring_at_i.append(trans_name_list[k])
                    net_state = str(state_at_i) + str(anomalousness_at_i)
                    triggered_at_i.append(net_state)

    status_at_time[data[i, 0]] = status_at_i
    erring_at_time[data[i, 0]] = erring_at_i
    triggered_at_time[data[i, 0]] = triggered_at_i

#time = status_at_time.keys()

for a in range(1, len(data)):                                            # Picks a Time
    for i in range(1, len(error_list)):                 # Picks an Error
        erring_match = str(erring_at_time[data[a, 0]]) in str(error_trans_list[i-1])
        condition_match = str(triggered_at_time[data[a, 0]]) in str(error_cond_list[i-1])

        if erring_match == True: #and condition_match == True:  -  Turning this on gives zero detection
            print('PROBLEM AT ' + str(erring_at_time[data[a, 0]]) + ' ON ' + str(data[a, 0]))
            print('Cause: ' + error_list[i, 3])
            print('Remedy: ' + error_list[i, 4])
            print('Time to consequence: ' + error_list[i, 5] + '\n')



#print(erring_at_time[data[791, 0]])

#print(status_at_time["09-11-2023 11:41:09"])
#print(erring_at_time["09-11-2023 11:41:09"])
#print(triggered_at_time["09-11-2023 11:41:09"])
        
#print(error_trans_list)
#print(len(error_trans_list))        
#print(len(error_list))        



# dataを横にスキャンしないとリアルタイムでの対応ができない!
# なので i で時間を選び、j でメインコンポーネントを選び、h で比較対象を選んで、次の i へ移っている。