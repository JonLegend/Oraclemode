#This is used to read the xlxs and csv files from their correct paths

from pandas import read_excel, read_csv
from os import getcwd

def path_read_excel(file_name): #New Excel reading function
    pathed_file_name = str(getcwd() + "/Operator Advisory and Hazard Matcher/" + file_name)
    return read_excel(pathed_file_name)

def path_read_csv(file_name): #New CSV reading function
    pathed_file_name = str(getcwd() + "/Operator Advisory and Hazard Matcher/" + file_name)
    return read_csv(pathed_file_name)