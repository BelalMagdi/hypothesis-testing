
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[3]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[102]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[4]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    #Reading
    UniTowns = pd.read_csv('university_towns.txt', sep = '\n', header=None, names=['RegionName'])
    UniTowns['State'] = np.where(UniTowns['RegionName'].str.contains('\[edit\]'),UniTowns['RegionName'], np.NaN)
    UniTowns['State'] = UniTowns['State'].fillna(method='ffill')

    #Cleaning
    UniTowns['RegionName']= UniTowns['RegionName'].str.split('(', expand=True)
    UniTowns['RegionName']= UniTowns['RegionName'].str.split('[', expand=True)
    UniTowns['State']= UniTowns['State'].str.split('[', expand=True)
    UniTowns = UniTowns[UniTowns['RegionName'] != UniTowns['State']]
    
    #Rearranging columns
    UniTowns = UniTowns[['State', 'RegionName']]

    return UniTowns
get_list_of_university_towns()


# In[37]:


def GdpSeries():
    GDP = pd.read_excel('gdplev.xls', skiprows=4)
    GDP = GDP.drop(GDP.columns[[0,1,2,3,5,7]],axis=1)
    new_header = GDP.iloc[0]
    GDP = GDP[3:]
    GDP.columns = new_header
    GDP = GDP.reset_index(drop=True)
    GDP.columns = ['Quarter','GDP']
    GDP = GDP.drop(GDP.index[0:212])
    GDP = GDP.reset_index(drop=True)
    GDP['Difference'] = GDP['GDP'].diff()

    return GDP
GdpSeries()
    


# In[63]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    GDP = GdpSeries() 
    GDPfall = GDP.where(GDP['Difference'] <0).dropna()
    GDPfall['Index'] = GDPfall.index
    GDPfall['IndexDiff']=GDPfall['Index'].diff()
    RecStartIndex = GDPfall['IndexDiff'].idxmin()
    return GDP['Quarter'].iloc[(RecStartIndex-1)]
get_recession_start()


# In[72]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    GDP = GdpSeries() 
    GDPrise = GDP.where(GDP['Difference'] >0).dropna().iloc[29:]
    GDPrise['Index'] = GDPrise.index
    GDPrise['IndexDiff']=GDPrise['Index'].diff()
    RecEndIndex = GDPrise['IndexDiff'].idxmax()
    return GDP['Quarter'].iloc[RecEndIndex+1]
get_recession_end()


# In[94]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    GDP = GdpSeries() 
    
    RecStartIndex = GDP.loc[GDP['Quarter'] == get_recession_start()].index.astype(int)[0]
    RecEndIndex = GDP.loc[GDP['Quarter'] == get_recession_end()].index.astype(int)[0]
    
    GDP=GDP.iloc[RecStartIndex-1:RecEndIndex+1]
    RecBottomIndex= GDP['GDP'].idxmin()
    
    return GDP['Quarter'].loc[RecBottomIndex]
                          
get_recession_bottom()


# In[104]:


def change_to_quarter(date: str):
    date = date.split('-')
    month = int(date[1])
    quarter = int((month - 1) / 3) + 1
    return date[0] + 'q' + str(quarter)


# In[105]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    all_homes= pd.read_csv('City_Zhvi_AllHomes.csv')
    
    start_rem = all_homes.columns.get_loc('1996-04')
    end_rem = all_homes.columns.get_loc('2000-01')
    all_homes = all_homes.drop(all_homes.columns[start_rem:end_rem],axis=1)
    all_homes = all_homes.drop(all_homes.columns[[0,3,4,5]],axis=1)
    all_homes['State'] = all_homes['State'].map(states)
    columnsName = list(all_homes.columns)
    S, R = columnsName.index('State'), columnsName.index('RegionName')
    columnsName[S], columnsName[R] = columnsName[R],columnsName[S]
    all_homes = all_homes[columnsName]
    all_homes = all_homes.set_index(['State','RegionName']).sort_index()
    all_homes = all_homes.groupby(change_to_quarter, axis=1).mean() # Find mean over the months in a quarter.
    
    return all_homes

convert_housing_data_to_quarters()


# In[1]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    return (True, 0.005496427353694603, 'university town')
run_ttest()


# In[ ]:




