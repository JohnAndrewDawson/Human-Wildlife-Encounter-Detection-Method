# %% Import Lybrearys
# Import Lybrearys
# Standard Libraries

import sys
import os

folder_path = # PATH TO TRACKLIB

if folder_path not in sys.path:
    sys.path.insert(0, folder_path)
    
import time 
from tracklib.core.obs_time import ObsTime
from tracklib.core import bbox
import my_utils
import psycopg2
import numpy as np

ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")

#--------------------#
head        = 'exp_'
tail        = '_Default'
shift       = 15
max_speed   = 1.25  #Does not update
d_gap_a     = 500
min_dist    = 25
min_time    = 60
HDA_radius  = 250
d_gap_h     = 500
height_h    = 1.6   # Does not update!!! must update in QGIS code saves value in table comments
height_a    = 1     # Does not update!!! must update in QGIS code saves value in table comments
t_gap       = 8 * 60     
ECAh_radius = 10
where       = "select id_indiv from indiv_human"

x_min = 942749.5
x_max = 958749.5
y_min = 6504411.5
y_max = 6520411.5

bbox = [x_min,x_max,y_min,y_max]
db = 'ResRoute'

# %% First Half Before running visibility

my_utils.enounter_events(
        bbox,
        head,
        tail,
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h,
        height_h,  # Does not update!!! must update in QGIS code saves value in table comments
        height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap,     
        ECAh_radius,
        db,
        where)

# %%  Second Half After running visibility

my_utils.Encounters(
        bbox,
        head        = head,
        tail        = tail,
        shift       = shift,
        max_speed   = max_speed,  #Does not update
        d_gap_a     = d_gap_a,
        min_dist    = min_dist,
        min_time    = min_time,
        HDA_radius  = HDA_radius,
        d_gap_h     = d_gap_h,
        height_h    = height_h,  # Does not update!!! must update in QGIS code saves value in table comments
        height_a    = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap       = t_gap,     
        ECAh_radius = ECAh_radius,
        db          = 'ResRoute',
        where       = where)
