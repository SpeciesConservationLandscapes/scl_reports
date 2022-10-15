# habitat_areas_trends.py
# ews 10/14/2022

# Goal:  generate a table showing range-wide habitat trends for the following metrics from SCL pipline:
# indigenous resident range, structural habitat, effective potential habitat, known occupied habitat
# for the latest year
# 
# results should be reported with all the past years to see the trend
# see notes in this Word doc:  SCL website rangewide table details 10-14-2022.docx

# SCL data is avaiable on in a Google Cloud Platform storage bucket
# here we assume those data have been downloaded locally using the scl_download_google_cloud.py script in scl_dir (defined below)

# this script works off the scl_states.geojson output from the SCL pipeline
# scl_states represents the intersection of all the states/provinces within the indigenous range and reports out for each state:
# indigenous_range_area, str_hab_area, eff_pot_hab_area, occupied_eff_pot_hab_area measured using GEE's area algorithm

# run using Anaconda environment:  C:\Users\esanderson>conda activate scl


# Imports

# imports
import os
import geopandas as gpd
import pandas as pd
import numpy as np
import csv


# Set up

# data files organized by folder by time point are in this directory:
scl_dir = r"C:\proj\species\tigers\TCLs v3\TCL delineation\scl_stats_09142022"
# subdirectory for pivot tables outputs
pivot_subdir = "pivot_tables\habitat_areas"
# data input file
datafile = "scl_states.geojson"
# csv output file
csv_file = 'habitat_area_trends.csv'

# the years to analyze are:
years = ['2020-01-01','2019-01-01','2018-01-01','2017-01-01','2016-01-01','2015-01-01','2014-01-01','2013-01-01','2012-01-01','2011-01-01','2010-01-01','2009-01-01','2008-01-01','2007-01-01','2006-01-01','2005-01-01','2004-01-01','2003-01-01','2002-01-01','2001-01-01']
# a single year for testing purposes
#years = ['2020-01-01']
# habitat types to analyze are:
types = ['indigenous_range_area','str_hab_area','eff_pot_hab_area','occupied_eff_pot_hab_area']
# variable names
habitat_names = ['Indigenous resident range', 'Structural habitat', 'Effective potential habitat', 'Known occupied habitat']
# use list comprehension to put these together as a dictionary
habitat_area_names = {types[i]: habitat_names[i] for i in range(len(types))}


# make an empty dictionary to hold areas by year
df_hab_areas = {}

# loop over years and calculate 
for year in years:
    
    # create empty dictionary for this year
    df_hab_areas[year] = {}
    
    # load gejson files into df
    df = gpd.read_file(os.path.join(scl_dir, year, datafile))

    # for each habitat type, just sum up the column
    for type in types:
        print ("Working on", year, type)
        df_hab_areas[year][type] = df[type].sum()

#print(df_hab_areas)

# output to csv

with open(os.path.join(scl_dir, csv_file), 'w', newline='', encoding = 'utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Timepoint'] + habitat_names)
    for year in years:
        data_list = []
        for type in types:
            data_list.append(df_hab_areas[year][type])
        writer.writerow([year] + data_list)

            
    
