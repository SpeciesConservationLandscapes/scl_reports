# species_landscape_by_admin.py
# ews 10/14/2022

# Goal:  generate a table showing the area of different species landscapes by country for a given year
# 
# results should be reported with all the past years to see the trend
# see notes in this Word doc:  SCL website rangewide table details 10-14-2022.docx

# SCL data is avaiable on in a Google Cloud Platform storage bucket
# here we assume those data have been downloaded locally using the scl_download_google_cloud.py script in scl_dir (defined below)

# here the key dataset is scl_species.geojson

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
datafile = "scl_species.geojson"
# csv output file
csv_file = 'species_landscapes_by_admin.csv'

# the years to analyze are:
#years = ['2020-01-01','2019-01-01','2018-01-01','2017-01-01','2016-01-01','2015-01-01','2014-01-01','2013-01-01','2012-01-01','2011-01-01','2010-01-01','2009-01-01','2008-01-01','2007-01-01','2006-01-01','2005-01-01','2004-01-01','2003-01-01','2002-01-01','2001-01-01']
# a single year for testing purposes
years = ['2020-01-01']
# habitat types to analyze are:
types = ['eff_pot_hab_area']

# make an empty dictionary to hold areas by year
#dict_pivots = {}

# loop over years
for year in years:

    # read file
    df = gpd.read_file(os.path.join(scl_dir, year, datafile))

    # for each habitat type, create pivot table using pandas summing areas by type
    pivot_areas_df = pd.pivot_table(df, 
        values = types,       
        index = ['lsid','country'],
        aggfunc = 'sum')

    # sum up the areas by lsid using groupby then rename column to avoid confusion
    ls_sum_df = pivot_areas_df.groupby(level='lsid').sum()
    ls_sum_df.rename(columns={'eff_pot_hab_area': 'sum_area'}, inplace = True)

    # reset indexes to get rid of multi-index before joining using merge
    ls_areas_df = pd.merge(pivot_areas_df.reset_index(), ls_sum_df.reset_index(), how = 'inner', on = 'lsid')

    # calculate fraction of each landscape in each country
    ls_areas_df['ls_frac'] = ls_areas_df['eff_pot_hab_area'] / ls_areas_df['sum_area']

    # drop the areas
    ls_areas_df.drop(columns=['eff_pot_hab_area','sum_area'], axis=1, inplace=True)

    # repivot to get the final arrangement for the table
    ls_admin_df = pd.pivot_table(ls_areas_df, 
        values = ['ls_frac'],       
        index = ['lsid'],
        columns = ['country'],
        aggfunc = 'sum',
        fill_value = 0)   

    #pivot above results in mutli-index for columns, so drop a level
    ls_admin_df = ls_admin_df.droplevel(0, axis = 1)

    # get list of countries, which are the column heads holding the ls_frac data
    countries = list(ls_admin_df.columns)

    # add a few columns to fill out table before output
    ls_admin_df['date'] = year
    ls_admin_df['lsid'] = ls_admin_df.index                   
    ls_admin_df['lstype'] = "species"
    ls_admin_df['name'] = "tbd"

    # output to csv with fields in desired order
    # write header
    fieldnames = ['Analysis date','Lsid','Landscape type','Name'] + countries
    with open(os.path.join(scl_dir, csv_file), 'w', newline='', encoding = 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

    # output to csv from dataframe
    fields = ['date','lsid','lstype','name'] + countries
    ls_admin_df.to_csv(os.path.join(scl_dir, csv_file), columns = fields, header=False, index = False, mode='a')