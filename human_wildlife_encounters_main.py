 # %%


import my_utils as mus 
from tracklib.core.obs_time import ObsTime

# Proxy settings (if needed)
http_proxy = "http://proxy.ign.fr:3128"
proxy = {
    'http': http_proxy,
    'https': http_proxy
}

ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")
HDA_radius = 250
shift = 15

x_min = 942749.5
x_max = 958749.5
y_min = 6504411.5
y_max = 6520411.5

bbox = [x_min,x_max,y_min,y_max]
db = 'ResRoute'

# %%


where = "select id_indiv from indiv_human" #where source != 'Strava' limit all
shift = 15
head = 'dldl'
tail = ''
db = 'ResRoute'


mus.find_comparable_routes(where, shift, head, tail, db)


# %%


head = 'dldl'
tail = ''
source_table = head+'traj_ints'+tail

mus.create_ppa_table(source_table, head, tail, db, HDA_radius, bbox=bbox)

# %% Create filtered DA
# Create filtered DA

source_head = 'dldl'
source_tail = ''
source_table = source_head+'traj_ints'+source_tail
esp = 25
time_max = 60

head = 'dldl'
tail = ''


tracks, tracks_simp_new_filter, id_traj = mus.create_filltered_da_table(source_table, 
                                                    head, 
                                                    
                                                    tail, 
                                                    db, 
                                                    HDA_radius, 
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


mus.create_encounter_events(source_ppa, 
                           source_da, 
                           source_pairing,
                           head, 
                           tail, 
                           comp_type = 'geom', 
                           db = db)

# %% Assign encounters to encounter_event

esp = 25
time_max = 60
buffer_size = 250

#dbs.assign_encoutners('p2_encounter_event'+'_buff_'+str(buffer_size)+'_filt_'+str(esp)+'_time_'+str(time_max)+'_no_m_animal',  db)
mus.assign_encoutners('p2_encounter_event_buff_250_filt_25_time_60_no_m_hum',  db)

