# landscapes.py
# ews 10/14/2022

# Goal:  generate a table listing all the lansdcapes for a given year at the range-wide scale as define dby the SCL pipeline
# for each landscape, provide its unique id, landscape type, name, structural habitat, effective potential habitat, known occupied habitat, %KBA, %PA
# see notes in this Word doc:  SCL website rangewide table details 10-14-2022.docx

# SCL data is avaiable on in a Google Cloud Platform storage bucket
# here we assume those data have been downloaded locally using the scl_download_google_cloud.py script in scl_dir (defined below)

# this script works off the scl landscape geojson outputs from the SCL pipeline
# there are six landscape types as defined in the landscape_names variable below

# note:  landscapes have been subdivided by states/province boundaries, so it's necessary to sum up each on by lsid
# note:  names are provided by joining with a separate file that gives names by year, landscape type, and lsid (tbd)

# run using Anaconda environment:  C:\Users\esanderson>conda activate scl

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
csv_file = 'landscape_list.csv'

# the years to analyze are:
#years = ['2020-01-01','2019-01-01','2018-01-01','2017-01-01','2016-01-01','2015-01-01','2014-01-01','2013-01-01','2012-01-01','2011-01-01','2010-01-01','2009-01-01','2008-01-01','2007-01-01','2006-01-01','2005-01-01','2004-01-01','2003-01-01','2002-01-01','2001-01-01']
# a single year for testing purposes
years = ['2020-01-01']
# habitat types to analyze are:
types = ['str_hab_area','eff_pot_hab_area','occupied_eff_pot_hab_area', 'kba_eff_pot_hab_area', 'pa_eff_pot_hab_area']
# a single type for testing purposes
#types = ['str_hab_area']
# landscape names
landscape_names = ['species', 'species fragment', 'survey', 'survey fragment', 'restoration', 'restoration fragment']
# fieldnames
fieldnames = ['Analysis date','Lsid','Landcape type','Name','Structural habitat','Effective potential habitat','Known occupied habitat','%KBA','%Protected']
# use list comprehension to put landscape names with datafiles in dictionary
dict_landscape_names = {datafiles[i]: landscape_names[i] for i in range(len(datafiles))}


# make an empty dictionary to hold areas by year
dict_pivots = {}

# loop over datafiles
for year in years:
    for datafile in datafiles:
        print ("Working on", year, datafile)
        # load gejson files into df
        df = gpd.read_file(os.path.join(scl_dir, year, datafile))

        # for each habitat type, create pivot table using pandas summing areas by type
        pivot_areas_df = pd.pivot_table(df, 
            values = types,       
            index = ['lsid'],
            aggfunc = 'sum')

        # add some additional columns for output
        pivot_areas_df['date'] = year
        pivot_areas_df['lsid'] = pivot_areas_df.index                   
        pivot_areas_df['lstype'] = dict_landscape_names[datafile]
        pivot_areas_df['name'] = "tbd"
        pivot_areas_df['kba_frac'] = pivot_areas_df['kba_eff_pot_hab_area'] / pivot_areas_df['eff_pot_hab_area'] 
        pivot_areas_df['pa_frac'] = pivot_areas_df['pa_eff_pot_hab_area'] / pivot_areas_df['eff_pot_hab_area'] 
        #pivot_areas_df.drop(labels = ['kba_eff_pot_hab_area','pa_eff_pot_hab_area'], axis=1)
        #print (datafile)

        #print (pivot_areas_df.head())
        dict_pivots[datafile] = pivot_areas_df

# export to csv
# write header
with open(os.path.join(scl_dir, csv_file), 'w', newline='', encoding = 'utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(fieldnames)
# write to csv from pandas
for year in years:
    data_list = []
    for datafile in datafiles:
        #print(datafile)
        #for col in dict_pivots[datafile].columns:
        #    print (col)
        #print(dict_pivots[datafile].head())
        fields= ['date','lsid','lstype','name','str_hab_area','eff_pot_hab_area','occupied_eff_pot_hab_area','kba_frac','pa_frac']
        dict_pivots[datafile].to_csv(os.path.join(scl_dir, csv_file), columns = fields, header=False, index = False, mode='a')