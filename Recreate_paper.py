# %% Import Lybrearys
# Import Lybrearys
# Standard Libraries

import sys
import os

TRACKLIB_folder_path = r"PATH TO TRACKLIB"
db          = 'ResRoute'
db_user     = 'postgres'
db_password = 'postgres'

if TRACKLIB_folder_path not in sys.path:
    sys.path.insert(0, TRACKLIB_folder_path)
    
import time 
from tracklib.core.obs_time import ObsTime
from tracklib.core import bbox
import my_utils
import psycopg2
import numpy as np

# Proxy settings (if needed)
http_proxy = "http://proxy.ign.fr:3128"
proxy = {
    'http': http_proxy,
    'https': http_proxy
}

ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")

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
ECA_h_radius= 10
where       = "select id_indiv from indiv_human"

x_min = 942749.5
x_max = 958749.5
y_min = 6504411.5
y_max = 6520411.5

bbox = [x_min,x_max,y_min,y_max]

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
        height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap,     
        ECA_h_radius,
        db,
        where)

# %% HDA = 500

HDA_radius  = 500
tail_HDA_500 = '_HDA_500'

tracks, tracks_simp_new_filter, id_traj = my_utils.create_filltered_hda_table(
                                                        head+'traj_ints'+tail, 
                                                        head, 
                                                        tail_HDA_500, 
                                                        db, 
                                                        HDA_radius, 
                                                        esp = min_dist, 
                                                        #mode = 1, 
                                                        cells = [], 
                                                        bbox = bbox, 
                                                        bbox_grid = [],
                                                        time_max=min_time)

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

qurry = """\
        COMMENT ON TABLE """ + head + """hda""" + tail_HDA_500+ """ IS 
        'source_table   =  """ + str(head+'traj_ints'+tail) + """
        shift       = """+ str(shift) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

source_ppa      =  head+'ppa'+tail
source_hda      =  head+'hda'+tail_HDA_500 
source_pairing  =  head+'traj_ints'+tail

start = time.time()

my_utils.create_encounter_events(source_ppa, 
                            source_hda, 
                            source_pairing,
                            head, 
                            tail_HDA_500, 
                            comp_type = 'geom', 
                            db = db)

ee_length = time.time()-start

print(ee_length)

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

# adds comments to table saving the peremiters used for the table
qurry = """\
        COMMENT ON TABLE """ + head + """encounter_event""" + tail_HDA_500+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ppa   = """+ str(source_ppa) + """
        source_hda   = """+ str(head+'hda'+tail_HDA_500) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""
        duration    = """+ str(ee_length)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

HDA_radius = 250

print('------WAIT Visibility Check should be run in QGIS Before proceeding------')


# %% d_gap_a

d_gap_a = 999999999
tail_d_gap_a_none    = '_d_gap_a_none'

source_table = head+'traj_ints'+tail

my_utils.create_ppa_table(source_table, head, tail_d_gap_a_none, db, d_gap_a = d_gap_a,bbox=bbox)

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

qurry = """\

        COMMENT ON TABLE """ + head + """close_points_animal""" + tail_d_gap_a_none + """ IS
        
        'source_table   = """+ str(source_table) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """';

        
        COMMENT ON TABLE """ + head + """ppa""" + tail_d_gap_a_none + """ IS
        
        'source_table   = """+ str(source_table) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """';

        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()


source_ppa      =  head+'ppa'+tail_d_gap_a_none
source_hda      =  head+'hda'+tail
source_pairing  =  head+'traj_ints'+tail

start = time.time()

my_utils.create_encounter_events(source_ppa, 
                            source_hda, 
                            source_pairing,
                            head, 
                            tail_d_gap_a_none, 
                            comp_type = 'geom', 
                            db = db)

ee_length = time.time()-start 

print(ee_length)

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

# adds comments to table saving the peremiters used for the table
qurry = """\
        COMMENT ON TABLE """ + head + """encounter_event""" + tail_d_gap_a_none+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ppa  = """+ str(head+'ppa'+tail_d_gap_a_none) + """
        source_hda  = """+ str(source_hda) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ +str(1.25) + """
        d_gap_a     = """ +str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""
        duration    = """+ str(ee_length)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()



d_gap_a = 500



# %% d_gap_h

d_gap_h = 999999999
tail_d_gap_h_none    = '_d_gap_h_none'

source_table = head+'traj_ints'+tail

tracks, tracks_simp_new_filter, id_traj = my_utils.create_filltered_hda_table(
                                                        source_table, 
                                                        head, 
                                                        tail_d_gap_h_none, 
                                                        HDA_radius, 
                                                        esp = min_dist, 
                                                        db = db,
                                                        db_user = 'postgres', 
                                                        db_password = 'postgres', 
                                                        cells = [],
                                                        d_gap_h = d_gap_h, 
                                                        bbox = bbox, 
                                                        bbox_grid = [],
                                                        time_max=min_time)

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

qurry = """\
        COMMENT ON TABLE """ + head + """hda""" + tail_d_gap_h_none+ """ IS 
        'source_table   =  """ + str(source_table) + """
        shift       = """+ str(shift) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

source_ppa      =  head+'ppa'+tail
source_hda      =  head+'hda'+tail_d_gap_h_none
source_pairing  =  head+'traj_ints'+tail

start = time.time()

my_utils.create_encounter_events(source_ppa, 
                            source_hda, 
                            source_pairing,
                            head, 
                            tail_d_gap_h_none, 
                            comp_type = 'geom', 
                            db = db)

ee_length = time.time()-start 

print(ee_length)

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

# adds comments to table saving the peremiters used for the table
qurry = """\
        COMMENT ON TABLE """ + head + """encounter_event""" + tail_d_gap_h_none+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ppa   = """+ str(source_ppa) + """
        source_hda   = """+ str(head+'HDA'+tail_d_gap_h_none) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""
        duration    = """+ str(ee_length)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()


d_gap_h = 500

# %% Second Half After running visibility
# Create encounters for default settings
my_utils.Encounters(
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
        height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap,     
        ECA_h_radius,
        db,
        where)


# %% Second Half for HDA = 500

my_utils.Encounters(
        bbox,
        head,
        '_hda_500',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius = 500,
        d_gap_h=d_gap_h,
        height_h=height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a=height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap=t_gap,     
        ECA_h_radius=ECA_h_radius,
        db=db,
        where=where,
        source_table    = 'exp_encounter_event_hda_500',
        source_pairing  = 'exp_traj_ints_default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_500',
        id_column       = 'id_encounter',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half for d_gap_h = None

my_utils.Encounters(
        bbox,
        head,
        '_d_gap_h_none',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = 999999999,
        height_h=height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a=height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap=t_gap,     
        ECA_h_radius=ECA_h_radius,
        db=db,
        where=where,
        source_table    = 'exp_encounter_event_d_gap_h_none',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_Default',
        source_hda      = 'exp_hda_d_gap_h_none',
        id_column       = 'id_encounter',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half for d_gap_a = None

my_utils.Encounters(
        bbox,
        head,
        '_d_gap_a_none',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = 999999999,
        height_h=height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a=height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap=t_gap,     
        ECA_h_radius=ECA_h_radius,
        db=db,
        where=where,
        source_table    = 'exp_encounter_event_d_gap_a_none',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_d_gap_a_none',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half t_gap = 2 min

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_2_min',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 2*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_t_gap_2_min',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half t_gap = 4 min

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_4_min',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 4*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_t_gap_4_min',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half t_gap = 16 min

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_16_min',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 16*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_t_gap_16_min',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half t_gap = 2 hours

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_2_h',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 2*60*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_t_gap_2_h',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half t_gap = 4 hours

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_4_h',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 4*60*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_t_gap_4_h',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half t_gap = 24 hours

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_24_h',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 24*60*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_t_gap_24_h',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% Second Half height_chamois = 0.8 m

my_utils.Encounters(
        bbox,
        head,
        tail = '_chamois_8_dm',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = 0.8,          # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_chamois_8_dm',
        vis_column      = 'vis_grid_chamois_8_dm',
        vis_table       = 'vis_grid_chamois_8_dm')

# %% Second Half height_chamois = 1.2 m

my_utils.Encounters(
        bbox,
        head,
        tail = '_chamois_12_dm',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = 1.2,          # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_chamois_12_dm',
        vis_column      = 'vis_grid_chamois_12_dm',
        vis_table       = 'vis_grid_chamois_12_dm')


# %% Second Half height_human = 2 m

my_utils.Encounters(
        bbox,
        head,
        tail = '_human_2_m',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = 2,                 # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,          # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_human_2_m',
        vis_column      = 'vis_grid_human_2_m',
        vis_table       = 'vis_grid_human_2_m')



# %% Second Half ignoring visibility

source_table = head + """encounter_event""" + tail

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

qurry = """\

        ALTER TABLE """ + source_table + """ DROP IF EXISTS vis_grid_all_true;
        
        ALTER TABLE """ + source_table + """
        ADD vis_grid_all_true BOOLEAN NOT NULL DEFAULT TRUE;

     """
curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

my_utils.Encounters(
        bbox,
        head,
        tail = '_ignore_vis',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_Default',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_500',
        id_column       = 'id_encounter_ignore_vis',
        vis_column      = 'vis_grid_all_true',
        vis_table       = None # Skips joining visibility
        )



# %% Second Half ignoring visibility hda_500

source_table = head + """encounter_event_hda_500"""

conn = psycopg2.connect(database= db , user='postgres')

curs = conn.cursor()

qurry = """\

        ALTER TABLE """ + source_table + """ DROP IF EXISTS vis_grid_all_true;
        
        ALTER TABLE """ + source_table + """
        ADD vis_grid_all_true BOOLEAN NOT NULL DEFAULT TRUE;

     """
curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

my_utils.Encounters(
        bbox,
        head,
        tail = '_ignore_vis_hda_500',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = 500,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = 'exp_encounter_event_hda_500',
        source_pairing  = 'exp_traj_ints_Default',
        source_ppa      = 'exp_ppa_default',
        source_hda      = 'exp_hda_default',
        id_column       = 'id_encounter_ignore_vis',
        vis_column      = 'vis_grid_all_true',
        vis_table       = None # Skips joining visibility
        )



# %%
