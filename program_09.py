#!/bin/env python
# Modifier: Linji Wang
# Original Author: Keith Cherkauer
# Date of Modification: 04/03/2020
# Filename: porgram_09.py
# Description: This python script check the quality of the dataset 
# "DataQualityChecking.txt". Specifically removes no data values, identify
# gross errors, inconsistencies in variables, and range errors. Also, creates
# output for the data quality check including corrected data, and plots.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "Date", "Precip", "Max Temp", "Min Temp", "Wind Speed". Function
    returns the completed DataFrame, and a dictionary designed to contain all 
    missing value counts."""
    
    # define column names
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

    # open and read the file
    DataDF = pd.read_csv("DataQualityChecking.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    
    # define and initialize the missing data dictionary
    ReplacedValuesDF = pd.DataFrame(0.0, index=["1. No Data",
                                                "2. Gross Error",
                                                "3. Swapped",
                                                "4. Range Fail"], columns=colNames[1:])
    return( DataDF, ReplacedValuesDF )
 
def Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ):
    """This check replaces the defined No Data value with the NumPy NaN value
    so that further analysis does not use the No Data values.  Function returns
    the modified DataFrame and a count of No Data values replaced."""

    # Replace all values of -999 in this file with the NumPy NaN values.
    DataDF[DataDF==-999]=np.nan
    return( DataDF, ReplacedValuesDF )
    # Record the number of values replaced for each data type in the dataframe ReplacedValuesDF with the index "1. No Data"
    for i in range(DataDF.shape[1]):
        ReplacedValuesDF.iloc[0,i]=DataDF.iloc[:,i].isna().sum()
    return(DataDF,ReplacedValuesDF)
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
    """This function checks for gross errors, values well outside the expected 
    range, and removes them from the dataset.  The function returns modified 
    DataFrames with data the has passed, and counts of data that have not 
    passed the check."""
 
    # Apply the following error thresholds: 0 d P d 25; -25d T d 35, 0 d WS d 10. Replace values outside this range with NaN.
    # Record the number of values replaced for each data type in the dataframe ReplacedValuesDF with the index "2. Gross Error"
    index=(DataDF['Precip']<0) | (DataDF['Precip']>25)
    ReplacedValuesDF.iloc[1,0]= index.sum()
    DataDF['Precip'][index]=np.nan
    
    for i in range(1,3):
        index=(DataDF.iloc[:,i]<-25) | (DataDF.iloc[:,i]>35)
        ReplacedValuesDF.iloc[1,i]= index.sum()
        DataDF.iloc[:,i][index]=np.nan
    
    index=(DataDF['Wind Speed']<0) | (DataDF['Wind Speed']>10)
    ReplacedValuesDF.iloc[1,3]= index.sum()
    DataDF['Wind Speed'][index]=np.nan
    
    return( DataDF, ReplacedValuesDF )
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
    
    # Check that all values of Max Temp are greater then for Min Temp for the current day's observations.
    # Record the number of values replaced for each data type in the dataframe ReplacedValuesDF with the index "3. Swapped"
    index=(DataDF['Max Temp']<DataDF['Min Temp'])

    ReplacedValuesDF.iloc[2,1]= index.sum()
    ReplacedValuesDF.iloc[2,2]= index.sum()
    # Where they are not, swap the values.
    DataDF['Max Temp'][index],DataDF['Min Temp'][index]=\
                DataDF['Min Temp'][index],DataDF['Max Temp'][index]
    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
    # Identify days with temperature range (Max Temp minus Min Temp) greater than 25°C.
    index=(DataDF['Max Temp']-DataDF['Min Temp']>25)
    # Record the number of values to be replaced for each data type in the dataframe ReplacedValuesDF with the index "4. Range Fail"
    ReplacedValuesDF.iloc[3,1]= index.sum()
    ReplacedValuesDF.iloc[3,2]= index.sum()
    
    # When range is exceeded replace both Tmax and Tmin with NaN.
    DataDF['Max Temp'][index]=np.nan
    DataDF['Min Temp'][index]=np.nan
    return( DataDF, ReplacedValuesDF )
    

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)
    
    print("\nRaw data.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF )
    
    print("\nMissing values removed.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check02_GrossErrors( DataDF, ReplacedValuesDF )
    
    print("\nCheck for gross errors complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF )
    
    print("\nCheck for swapped temperatures complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check04_TmaxTminRange( DataDF, ReplacedValuesDF )
    
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)

    # Reassign name to dataset after correction and reinport the dataset before check
    CorrectedDataDF=DataDF
    OriginalDataDF=ReadData(fileName)[0]
    
    # Plot each dataset before and after correction has been made.
    # PCP plot:
    OriginalDataDF['Precip'].plot(figsize=(15,10),style='r')
    CorrectedDataDF['Precip'].plot(style='g')
    plt.legend(["Orinigal","Corrected"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Precipitation (mm)")
    plt.savefig("Precipitation Data Quality Check.jpg")
    plt.close()
    # Max Temp:
    OriginalDataDF['Max Temp'].plot(figsize=(15,10),style='r')
    CorrectedDataDF['Max Temp'].plot(style='g')
    plt.legend(["Orinigal","Corrected"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Max Air Temperature (°C)")
    plt.savefig("Max Air Temperature Data Quality Check.jpg")
    plt.close()
    # Min Temp:
    OriginalDataDF['Min Temp'].plot(figsize=(15,10),style='r')
    CorrectedDataDF['Min Temp'].plot(style='g')
    plt.legend(["Orinigal","Corrected"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Min Temperature (°C)")
    plt.savefig("Min Temperature Data Quality Check.jpg")
    plt.close()
    # Wind Speed:
    OriginalDataDF['Wind Speed'].plot(figsize=(15,10),style='r')
    CorrectedDataDF['Wind Speed'].plot(style='g')
    plt.legend(["Orinigal","Corrected"], loc='best',edgecolor='k')
    plt.xlabel("Date")
    plt.ylabel("Wind Speed (m/s)")
    plt.savefig("Wind Speed Data Quality Check.jpg")
    plt.close()
    
    # Write data that has passed the quality check into a new file with the same format as the input data file.
    CorrectedDataDF.to_csv('Corrected_Data.txt', sep=" ", header=None)
    
    # Output information on failed checks to a separate Tab delimited file that can be imported into Metadata file.
    ReplacedValuesDF.to_csv("Summary.txt", sep="\t")
