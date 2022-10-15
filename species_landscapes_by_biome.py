# species_landscape_by_biome.py
# ews 10/15/2022

# Goal:  generate a table showing the area of different species landscapes by biome for a given year
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
import json

# Set up

# data files organized by folder by time point are in this directory:
scl_dir = r"C:\proj\species\tigers\TCLs v3\TCL delineation\scl_stats_09142022"
# subdirectory for pivot tables outputs
pivot_subdir = "pivot_tables\habitat_areas"
# data input file
datafile = "scl_species.geojson"
# csv output file
csv_file = 'species_landscapes_by_biome.csv'

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

    # pull out ecoregions json where the biome info is
    ecoregions_df = df[['id','ecoregions']]

    # set index to match id (note this is the unique id of the polygon from GEE, not lsid)
    ecoregions_df.set_index('id', inplace=True, drop=True)
    #ecoregions_df.set_index('month')

    # convert df to dictionary, indexed by lsid
    # note this requires transposition and selection of the right keyword for *.to_dict
    # see this helpful explainer: https://stackoverflow.com/questions/26716616/convert-a-pandas-dataframe-to-a-dictionary
    # ecoregion_list above is 1 item list containing a list of json strings
    ecoregions_dict = ecoregions_df.T.to_dict('list')

    # create an empty dictionary to hold biome sums, eventually this will be key'd by id, biome_name
    biome_sum = {}

    # an id for testing
    #an_id = '00000000000000000001_00000000000000000010'

    # loop over each id
    for an_id in ecoregions_dict.keys():

        # create an empty dictionary entry for each id
        biome_sum[an_id] = {}

        # loop over data_strings for each id
        for data_str in ecoregions_dict[an_id]:

            # convert to from json (is this necessary? is there a better way?)... results in list of dictionaries
            data_list = json.loads(data_str)

            # loop over the list to access the dictionaries with the biome data
            for data_dict in data_list:

                # set value to zero if first time seeing this biome
                if data_dict['biome_name'] not in biome_sum[an_id]:
                    biome_sum[an_id][data_dict['biome_name']] = 0

                # add eff_pot_hab_area for this id sum of biome area
                biome_sum[an_id][data_dict['biome_name']] = biome_sum[an_id][data_dict['biome_name']] + data_dict['eff_pot_hab_area']
                #print(an_id, data_dict['biome_name'], biome_sum[an_id][data_dict['biome_name']])

    # convert biome_sum back to df
    # transpose so the index is id and the columsn are the sums by biome
    biome_df = pd.DataFrame.from_dict(biome_sum).T

    # fill NaN values with 0
    biome_df = biome_df.fillna(0)

    # get list of biomes as a list
    biomes = list(biome_df.columns)
    
    # set index name before merging, then reset to create column before merge
    biome_df.index.name = 'id'
    biome_df.reset_index()

    # get just id and eff_pot_hab_area from the full df
    df1 = df[['id','lsid','eff_pot_hab_area']]

    # merge biome data with the data extract above
    biome_areas_df = pd.merge(df1, biome_df, how = 'inner', on = 'id')

    # use pivot to calculate sum for each lsid
    values_list = ['eff_pot_hab_area'] + biomes
    ls_biome_df = pd.pivot_table(biome_areas_df, 
        values = values_list,    
        index = ['lsid'],
        aggfunc = 'sum')

    # calculate fraction of landscape area in each biome
    for biome in biomes:
        ls_biome_df[biome] = ls_biome_df[biome] / ls_biome_df['eff_pot_hab_area']  

    # add a few columns to fill out table before output
    ls_biome_df['date'] = year
    ls_biome_df['lsid'] = ls_biome_df.index                   
    ls_biome_df['lstype'] = "species"
    ls_biome_df['name'] = "tbd"

    # expected order for output
    # note this will drop any biome = NaN, which creates some small rounding issues
    biome_order = ['Tropical & Subtropical Moist Broadleaf Forests', 'Tropical & Subtropical Dry Broadleaf Forests', 'Tropical & Subtropical Grasslands, Savannas & Shrublands', 'Tropical & Subtropical Coniferous Forests', 'Mangroves', 'Temperate Broadleaf & Mixed Forests', 'Temperate Conifer Forests', 'Flooded Grasslands & Savannas', 'Montane Grasslands & Shrublands', 'Boreal Forests/Taiga', 'Deserts',  'Xeric Shrublands']

    # if a biome doesn't exist, then make it and fill with zero
    for biome in biome_order:
        if biome not in ls_biome_df.columns:
            ls_biome_df[biome] = 0

    # output to csv with fields in desired order
    # write header
    fieldnames = ['Analysis date','Lsid','Landscape type','Name'] + biome_order
    with open(os.path.join(scl_dir, csv_file), 'w', newline='', encoding = 'utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

    # output to csv from dataframe
    fields = ['date','lsid','lstype','name'] + biome_order
    ls_biome_df.to_csv(os.path.join(scl_dir, csv_file), columns = fields, header=False, index = False, mode='a')