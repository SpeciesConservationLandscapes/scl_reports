# landscape_habitat_areas_trends.py
# ews 10/14/2022

# Goal:  generate a table showing range-wide landscape area trends for the six landscape types form the SCL pipeline
# 
# results should be reported with all the past years to see the trend
# see notes in this Word doc:  SCL website rangewide table details 10-14-2022.docx

# SCL data is avaiable on in a Google Cloud Platform storage bucket
# here we assume those data have been downloaded locally using the scl_download_google_cloud.py script in scl_dir (defined below)

# this script works off the scl landscape geojson outputs from the SCL pipeline
# there are six landscape types as defined in the landscape_names variable below

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
datafiles = ["scl_species.geojson", "scl_species_fragment.geojson", "scl_survey.geojson", "scl_survey_fragment.geojson", "scl_restoration.geojson", "scl_restoration_fragment.geojson"]
# csv output file
csv_file = 'landscape_area_trends.csv'

# the years to analyze are:
years = ['2020-01-01','2019-01-01','2018-01-01','2017-01-01','2016-01-01','2015-01-01','2014-01-01','2013-01-01','2012-01-01','2011-01-01','2010-01-01','2009-01-01','2008-01-01','2007-01-01','2006-01-01','2005-01-01','2004-01-01','2003-01-01','2002-01-01','2001-01-01']
# a single year for testing purposes
#years = ['2020-01-01']
# habitat types to analyze are:
types = ['eff_pot_hab_area']
# variable names
landscape_names = ['Species conservation landscapes', 'Species fragments', 'Survey landscapes', 'Survey fragments', 'Restoration landscapes', 'Restoration fragments']



# make an empty dictionary to hold areas by year
df_hab_areas = {}

# loop over years and calculate pivot tables 
for year in years:
    
    # create empty dictionary for this year
    df_hab_areas[year] = {}

    for datafile in datafiles:
        print ("Working on", year, datafile)
        # load gejson files into df
        df = gpd.read_file(os.path.join(scl_dir, year, datafile))
        # sum up eff_pot_hab_area; note using datafile as stand in for ls_type
        df_hab_areas[year][datafile] = df['eff_pot_hab_area'].sum()

#print(df_hab_areas)

# output to csv

with open(os.path.join(scl_dir, csv_file), 'w', newline='', encoding = 'utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Analysis date'] + landscape_names)
    for year in years:
        data_list = []
        for datafile in datafiles:
            data_list.append(df_hab_areas[year][datafile])
        writer.writerow([year] + data_list)

            
    
