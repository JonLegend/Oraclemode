# Import Libraries # 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import file_read


#might need to change the file load path to run
ld_data = pd.read_csv("/home/toshiba/Documents/Github Docs/Oraclemode/Operator Advisory and Hazard Matcher/Raw Data/Data Test 5.csv") #Load data from file
print(ld_data.info()) #Gets info about loaded file

ld_data['Log Time Stamp'] = ld_data['Log Time Stamp'].astype('datetime64[ns]')
#pd.to_datetime(ld_data['Log Time Stamp'])

print(ld_data.info())

#===== test plots======

sns.jointplot(data=ld_data, x='Log Time Stamp', y='/FT108', color='blue')
sns.jointplot(data=ld_data, x='Log Time Stamp', y='/FT109', color='red')
sns.jointplot(data=ld_data, x='Log Time Stamp', y='/LT108', color='green')
sns.jointplot(data=ld_data, x='Log Time Stamp', y='PT115b', color='yellow')
