# %% Import Lybrearys
# Import Lybrearys

# Standard Libraries
import numpy as np
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
import psycopg2
import math 
# Plotting Libraries
import matplotlib.pyplot as plt
import contextily as cx
import time 
from tracklib.core import db as dbs

# Geospatial Libraries
from shapely.geometry import LineString, Point
import shapely as shp
from mpl_toolkits.basemap import Basemap

# Custom Libraries
import ortega as ot
import tracklib as tkl
from tracklib.core.obs_time import ObsTime
from tracklib.io.track_reader import TrackReader
from tracklib.io.track_writer import TrackWriter
from tracklib.core import obs_coords as Coordsfrom 
from tracklib.core import track

from tracklib.core import bbox
from tracklib.core import encounters
from tracklib.core import (listify)
from tracklib.core import db as dbs

# Proxy settings (if needed)
http_proxy = "http://proxy.ign.fr:3128"
proxy = {
    'http': http_proxy,
    'https': http_proxy
}

ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
buffer_size = 500
shift = 15

x_min = 942749.5
x_max = 958749.5
y_min = 6504411.5
y_max = 6520411.5

bbox = [x_min,x_max,y_min,y_max]
db = 'ResRoute'

# %% Create traj_ints

# Create traj_ints

where = "select id_indiv from indiv_human" #where source != 'Strava' limit all
shift = 15
head = 'p2_'
tail = ''
db = 'ResRoute'


dbs.find_comparable_routes(where, shift, head, tail, db)


# %% Create PPA
# Create PPA

head = 'p2_'
tail = ''
source_table = head+'traj_ints'+tail

dbs.create_ppa_table(source_table, head, tail, db, buffer_size,bbox=bbox)

 # %% Create filtered DA
 # Create filtered DA

source_head = 'p2_'
source_tail = ''
source_table = source_head+'traj_ints'+source_tail
esp = 25
time_max = 60

head = 'p2_'
tail = '_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)


tracks, tracks_simp_new_filter, id_traj = dbs.create_filltered_da_table(source_table, 
                                                    head, 
                                                    tail, 
                                                    db, 
                                                    buffer_size, 
                                                    esp = esp, 
                                                    mode = 1, 
                                                    cells = [], 
                                                    bbox = bbox, 
                                                    bbox_grid = [],
                                                    time_max=time_max)

# %%  Create filtered encounter_events
# Create filtered encounter_events Geom

esp = 25
time_max = 60
buffer_size = 250
source_ppa      =  'b_1_ppa_full_vis'
source_da       =  'p2_da'+'_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)
#source_da = 'b_1_da_full_vis_250m_buf_25_time_max_60'
source_pairing  =  'p2_traj_ints'


head = 'p2_'
tail = '_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)+'_no_m_hum'

start = time.time()

dbs.create_encounter_events(source_ppa, 
                           source_da, 
                           source_pairing,
                           head, 
                           tail, 
                           comp_type = 'geom', 
                           db = db)
print(time.time()-start) # 177.54374480247498 seconds




# %% Assign encounters to encounter_event

esp = 25
time_max = 60
buffer_size = 250

#dbs.assign_encoutners('p2_encounter_event'+'_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)+'_no_m_animal',  db)
dbs.assign_encoutners('p2_encounter_event_buff_250_filt_25_time_60_no_m_hum',  db)





# %% Create Encouter table 


db = 'ResRoute'
source_table = 'p2_encounter_event'+'_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)
traj_pair_tables = 'p2_traj_ints'
head = 'p2'
tail = '_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)

dbs.create_encounter_table(source_table, traj_pair_tables, head, tail,  db)


# %% 

buffer_size = 250

 # %% Create filtered DA
 # Create filtered DA

source_head = 'p2_'
source_tail = ''
source_table = source_head+'traj_ints'+source_tail
esp = 25
time_max = 60

head = 'p2_'
tail = '_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)


tracks, tracks_simp_new_filter, id_traj = dbs.create_filltered_da_table(source_table, 
                                                    head, 
                                                    tail, 
                                                    db, 
                                                    buffer_size, 
                                                    esp = esp, 
                                                    mode = 1, 
                                                    cells = [], 
                                                    bbox = bbox, 
                                                    bbox_grid = [],
                                                    time_max=time_max)

# %%  Create filtered encounter_event
# Create filtered encounter_event Geom

esp = 25
time_max = 60
source_ppa      =  'p2_ppa'
source_da       =  'p2_da'+'_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)
source_pairing  =  'p2_traj_ints'

head = 'p2'
tail = '_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)

start = time.time()

dbs.create_encounter_events(      source_ppa, 
                           source_da, 
                           source_pairing,
                           head, 
                           tail, 
                           comp_type = 'geom', 
                           db = db)
print(time.time()-start) # 177.54374480247498 seconds




# %% Assign encounters to encounter_event


dbs.assign_encoutners('p2_encounter_event'+'_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max),  db)




# %% Create Encouter table 


db = 'ResRoute'
source_table = 'p2_encounter_event'+'_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)
traj_pair_tables = 'p2_traj_ints'
head = 'p2'
tail = '_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)

dbs.create_encounter_table(source_table, traj_pair_tables, head, tail,  db)
