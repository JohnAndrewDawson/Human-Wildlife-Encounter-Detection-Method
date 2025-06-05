# %%
import math
import shapely as shp
import psycopg2
import numpy as np
from tracklib.core import track
from tracklib.core import track_collection
from tracklib.core import Obs
from tracklib.core import ObsTime
from tracklib.core import ENUCoords
from tracklib.core import makeCoords

class WrongArgumentError(Exception):
    pass



def find_comparable_routes(where, shift, head, tail, db):




     conn = psycopg2.connect(database= db , user='postgres')

     curs = conn.cursor()

     qurry = """\

     DROP TABLE IF EXISTS  """ + head + """traj_ints""" + tail + """;

     select 
          a_.id_traj as id_traj_1,
          b_.id_traj as id_traj_2, 
          a_.date as date_1, 
          b_.date as date_2,
          a_.start_time_1 as start_time_1,
          a_.end_time_1 as end_time_1,
          b_.start_time_2 as start_time_2,
          b_.end_time_2 as end_time_2
     into """ + head +"""traj_ints""" + tail + """
     from (
          select trajectories.* , min(sub_trajectories.start_time) as start_time_1, max(sub_trajectories.end_time ) as end_time_1
          from trajectories
          left join sub_trajectories 
          on sub_trajectories.id_traj = trajectories.id_traj
          where id_indiv in 
               (select id_indiv from trajectories_indivs where type_indiv = 'animal')
          group by trajectories.id_traj, sub_trajectories.id_traj
     ) as a_

     inner join (
          select trajectories.* , min(sub_trajectories.start_time) as start_time_2, max(sub_trajectories.end_time ) as end_time_2
          from trajectories
          left join sub_trajectories 
          on sub_trajectories.id_traj = trajectories.id_traj
          where id_indiv in 
               (select id_indiv from trajectories_indivs where type_indiv = 'human')
          and id_indiv in 
               ("""+where+""")
          and trajectories.id_traj != 15059
          group by trajectories.id_traj, sub_trajectories.id_traj
     ) as b_
               
     on  extract(doy  from a_.date) <= extract(doy from b_.date)+ """+ str(shift)+ """
     and extract(doy from a_.date) >= extract(doy from b_.date)- """+ str(shift) +"""

     where a_.count_points-a_.count_missing_geom-a_.count_outlier >= 24
     and (a_.start_time_1 >= b_.start_time_2 
     and a_.start_time_1 <= b_.end_time_2
          
     or   b_.start_time_2 >= a_.start_time_1 
     and  b_.start_time_2 <= a_.end_time_1
          
     or   a_.end_time_1 >= b_.start_time_2 
     and  a_.end_time_1 <= b_.end_time_2
          
     or   b_.end_time_2 >= a_.start_time_1 
     and  b_.end_time_2 <= a_.end_time_1);
     
    DROP INDEX IF EXISTS """ + head + """idx_traj_ints_id_traj_2""" + tail+ """;
    DROP INDEX IF EXISTS """ + head + """idx_traj_ints_id_traj_1""" + tail+ """;

    CREATE INDEX """ + head + """idx_traj_ints_id_traj_2""" + tail+ """ ON """ + head + """traj_ints""" + tail+ """(id_traj_2);
    CREATE INDEX """ + head + """idx_traj_ints_id_traj_1""" + tail+ """ ON """ + head + """traj_ints""" + tail+ """(id_traj_1);


     """
     curs.execute(qurry)

     conn.commit()
     curs.close()
     conn.close()

def create_ppa_table(source_table, head, tail, db, buffer_size, cells = [], bbox = [], bbox_grid = []):

    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    qurry = """\
    
    DROP TABLE IF EXISTS """ + head + """ppa""" + tail+ """;
    DROP TABLE IF EXISTS """ + head + """close_points_animal""" + tail+ """;

    SELECT 
        DISTINCT p.*,
        FLOOR((st_x(p.geom) - 942749.5) / 25) as x_grid,
        FLOOR((st_y(p.geom) - 6504411.5) / 25) as y_grid,
        ti.id_traj_1 as id_traj,
        ti.date_1
    into """ + head + """close_points_animal""" + tail+ """
    FROM """ + source_table + """ ti
    LEFT JOIN sub_trajectories st ON st.id_traj = ti.id_traj_1
    LEFT JOIN points p ON p.id_sub_traj = st.id_sub_traj
    WHERE p.outlier = 'false'
    AND p.geom IS NOT NULL;

    alter table """ + head + """close_points_animal""" + tail+ """
    add ppa geometry;

    alter table """ + head + """close_points_animal""" + tail+ """
    add primary key (id_point)
    """


    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close()

    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    print('Here')


    qurry = """\
        SELECT id_point, id_traj, temps,  st_x(geom), st_y(geom)
        FROM """ + head + """close_points_animal""" + tail+ """
        order by id_traj, temps
        """

    curs.execute(qurry)

    id_point_lst = []

    print('Here 1')

    tracks = track_collection.TrackCollection()
    trace  = track.Track([],1)

    LINES = curs.fetchall()
    trace.tid = LINES[0][1]

    for row in LINES:
        id_traj = row[1]

        if id_traj != trace.tid:
            if trace is None:
                continue
            if trace.size() <= 0:
                continue
            print(len(trace))
            trace.createAnalyticalFeature('id_point', id_point_lst)
            tracks.addTrack(trace)
            id_point_lst = []
            trace = track.Track([],1)
            trace.tid = id_traj

        id_point_lst.append(row[0])
        trace.addObs(track.TrackObs(track.TrackENUCoords(row[3],row[4],-1),track.TrackObsTime.readTimestamp(str(row[2]))))



    print('Here 3')


    tracks.addAnalyticalFeature(add_ppa)

    print('Here 4')


    d = list(zip(
        tracks.getAnalyticalFeature('add_ppa'),
        tracks.getAnalyticalFeature('id_point')
    ))


    print('Here 5')


    curs.executemany("""
        update """ + head + """close_points_animal""" + tail+ """
            set ppa = ST_GeomFromWKB(%s::geometry, 2154) 
            where id_point = %s 
                """,d)

    print('Here 6')


    conn.commit()
    curs.close()
    conn.close()

    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    qurry = """\

    DROP INDEX IF EXISTS """ + head + """idx_sub_traj_temps_ppa""" + tail+ """;
    DROP INDEX IF EXISTS """ + head + """idx_id_traj_ppa""" + tail+ """;


    CREATE INDEX """ + head + """idx_sub_traj_temps_ppa""" + tail+ """ ON """ + head + """close_points_animal""" + tail+ """(id_sub_traj, temps);
    CREATE INDEX """ + head + """idx_id_traj_ppa""" + tail+ """        ON """ + head + """close_points_animal""" + tail+ """(id_traj);"""

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()

    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    qurry = 'DROP TABLE IF EXISTS ' + head + 'ppa' + tail+ ';'
    curs.execute(qurry)


    variables = """\
        id_point 	        integer, \n
        temps               time without time zone,\n
        geom                geometry,\n
        id_sub_traj         integer, \n
        id_traj             integer, \n
        date                date,\n
        next_id_point       integer, \n
        next_temps          time without time zone,\n
        next_geom           geometry,\n
        next_id_sub_traj    integer, \n
        next_id_traj        integer, \n
        ppa                 geometry,\n
        x_grid              integer,\n
        y_grid              integer,\n
        x_coord				double precision,
        y_coord 			double precision
        """
    print('here 7')
    
    table_name = head + 'ppa' + tail
    if not cells:
        print('here 8')

        qurry = """\
                create table """ + table_name + """ (
                """+ variables +"""
                );
                """
        curs.execute(qurry)
        conn.commit()

    elif cells:
        print('here 8a')

        bb_1_list_ppa,_ = table_partitioning(table_name, 
                   variables, 
                   'x_grid', 
                   'y_grid', 
                   bbox_grid, 
                   cells, 
                   cells,
                   db)
        
    print('here 9')

    qurry = """\
    insert into """ + head + """ppa""" + tail+ """
    select 
        id_point, 
        temps::time as temps, 
        geom, 
        id_sub_traj, 
        id_traj,
        date_1 as date,
        LEAD(id_point) OVER (ORDER BY id_sub_traj, temps) AS next_id_point,
        LEAD(temps::time) OVER (ORDER BY id_sub_traj, temps) AS next_temps,
        LEAD(geom) OVER (ORDER BY id_sub_traj, temps) AS next_geom,
        LEAD(id_sub_traj) OVER (ORDER BY id_sub_traj, temps) AS next_id_sub_traj,
        LEAD(id_traj) OVER (ORDER BY id_sub_traj, temps) AS next_id_traj,
        ppa,
        x_grid,
        y_grid,
        st_x(geom) as x_coord,
        st_y(geom) as x_coord
    from """ + head + """close_points_animal""" + tail+ """
    WHERE  geom 
                && -- intersects,  gets more rows  -- CHOOSE ONLY THE
                ST_MakeEnvelope (
                    """+ str(bbox[0]) +""",
                    """+ str(bbox[2]) +""",
                    """+ str(bbox[1]) +""",
                    """+ str(bbox[3]) +""",
                    2154)
    order by id_sub_traj, temps;

    alter table """ + head + """ppa""" + tail+ """
    add geom_line geometry;

    update """ + head + """ppa""" + tail+ """ 
    set geom_line = st_makeline(geom,next_geom);

    delete from """ + head + """ppa""" + tail+ """
    where st_length(geom_line) >= 500;

    delete from """ + head + """ppa""" + tail+ """
    where id_traj != next_id_traj;

    delete from """ + head + """ppa""" + tail+ """
    where next_id_traj is null;

    alter table """ + head + """ppa""" + tail+ """
    add buffer geometry;

    update """ + head + """ppa""" + tail+ """ 
    set buffer = st_buffer(ppa,""" + str(buffer_size) + """);
    
    
    CREATE INDEX """ + head + """ppa_index""" + tail+ """
        ON """ + head + """ppa""" + tail+ """
        USING GIST (ppa);

    -- Create an index on the time part of the 'temps' column in the 'ppa' table
    CREATE INDEX """ + head + """ppa_triple_index""" + tail+ """ ON """ + head + """ppa""" + tail+ """ (id_traj, temps, next_temps);
    
    -- Create index on 'id_traj' column in 'ppa' table
    CREATE INDEX """ + head + """idx_id_traj__ppa""" + tail+ """ ON """ + head + """ppa""" + tail+ """(id_traj);

    CREATE INDEX """ + head + """idx_ppa_grid""" + tail+ """ ON """ + head + """ppa""" + tail+ """(x_grid,y_grid);

    
    """

    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close() 

def add_ppa(track, i):

    #print(track.tid)
    if i == track.size()-1:
        return shp.Point(0, 0).wkb
    x1=track.getX(i)
    y1=track.getY(i)
    t1=track.getT(i)
    x2=track.getX(i+1)
    y2=track.getY(i+1)
    t2=track.getT(i+1)

    ds = track.getObs(i).distance2DTo(track.getObs(i + 1))
 
    dx = x2-x1
    dy = y2-y1
    dt = t2-t1
    
    speed = 1.25 * ds/(dt+0.00000000000001) 
        # the major axis of the PPA ellipse based on input speed (in time geography this speed is max speed)
    major = dt * speed
    minor: float = (major ** 2 - ds ** 2) ** 0.5  # calculate minor axis for the ellipse
        
    if dy == 0:
        dy = 0.1
    if dx == 0:
        dx = 0.1
        
    angle: float = np.rad2deg(math.atan(abs(dy / dx)))  # angle of the ellipse
        
    if dx * dy < 0:
            # the rotation angle of the PPA ellipse in 2nd and 4th quadrants
        angle = 180 - angle
    center = [(x1+x2)/2 ,(y1+y2)/2]

    #p = ellipse_polyline(center, major, minor, angle, 100)
    n=25
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)  # Return evenly spaced numbers over a specified interval

    st = np.sin(t)
    ct = np.cos(t)

    angle = np.deg2rad(angle)  # rotation angle of ellipse in radius unit
    sa = np.sin(angle)
    ca = np.cos(angle)

    p = np.empty((n, 2))

    # divide the major and minor axis by 2.0
    p[:, 0] = center[0] + major / 2.0 * ca * ct - minor / 2.0 * sa * st
    p[:, 1] = center[1] + major / 2.0 * sa * ct + minor / 2.0 * ca * st
    #print(track.tid)
    return shp.Polygon(shp.LinearRing(p)).wkb

def table_partitioning(table_name, variables, x_parition, y_partition, bbox, x_cells, y_cells,db):
    conn = psycopg2.connect(database=db, user='postgres')
    curs = conn.cursor()

    qurry = """\
        create table """ + table_name + """ (
        """+ variables +"""
        )PARTITION BY RANGE ("""+ x_parition +""");
        """
    #print(qurry)

    curs.execute(qurry)

    x_breaks = np.linspace(bbox[0],bbox[1], x_cells+1)
    y_breaks = np.linspace(bbox[2],bbox[3], y_cells+1)

    bb_list = []
    bb_1_list = []
    bb_2_list = []

    for i in range(len(x_breaks)-1):
        #print("---"+str(i)+"---")
        qurry = """\
            create table """ + table_name+'_x'+str(i+1) + """ PARTITION OF """+table_name+"""
            FOR VALUES FROM ("""+str(x_breaks[i]) +""") TO ("""+ str(x_breaks[i+1])+""")
	        PARTITION BY RANGE (""" + y_partition + """);
            """
        #print(qurry)
        curs.execute(qurry)

        for j in range(len(y_breaks)-1):
            qurry = """\
            create table """ + table_name+'_x'+str(i+1)+'_y'+str(j+1) + """ PARTITION OF """+table_name+'_x'+str(i+1)+"""
            FOR VALUES FROM ("""+str(y_breaks[j]) +""") TO ("""+ str(y_breaks[j+1])+""")

            """
            curs.execute(qurry)
       
            bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
            bb_2_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))

            # Right neighbor (i, j) -> (i, j+1)
            if j < y_cells-1:
                bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
                bb_2_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+2))

            # Bottom neighbor (i, j) -> (i+1, j)
            if i < x_cells-1:
                bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
                bb_2_list.append(table_name+'_x'+str(i+2)+'_y'+str(j+1))

            # Bottom-right diagonal neighbor (i, j) -> (i+1, j+1)
            if i < x_cells-1 and j < y_cells-1:
                bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
                bb_2_list.append(table_name+'_x'+str(i+2)+'_y'+str(j+2))

    conn.commit()
    curs.close()
    conn.close()

    return bb_1_list, bb_2_list

def create_filltered_da_table(source_table, head, tail, db, buffer_size, esp, mode, cells = [], bbox = [], bbox_grid = [], time_max=None):

    # create close hum_points in tkl
    conn = psycopg2.connect(database=db, user='postgres')

    curs = conn.cursor()

    qurry = """\

    SELECT 
        '1',
        ti.id_traj_2 AS id_traj,
        st_x(p.geom),
        st_y(p.geom),
        st_z(p.geom),
        p.temps,
        p.*,
        FLOOR((st_x(p.geom) - 942749.5) / 25) as x_grid,
        FLOOR((st_y(p.geom) - 6504411.5) / 25) as y_grid,
        ti.date_2
    FROM (select distinct id_traj_2, date_2 from """+source_table+""")  ti
    LEFT JOIN sub_trajectories st ON st.id_traj = ti.id_traj_2
    LEFT JOIN points p ON p.id_sub_traj = st.id_sub_traj
    WHERE p.geom IS NOT NULL
    and extract(year from p.temps) != 1970
    and extract(year from p.temps) != 1971
    and temps is not null
    and st_x(p.geom) >	"""+ str(bbox[0]) +"""
    and st_x(p.geom) <	"""+ str(bbox[1]) +"""
    and st_y(p.geom) >	"""+ str(bbox[2]) +"""
    and st_y(p.geom) <	"""+ str(bbox[3]) +"""
    order by id_traj,temps;"""

    curs.execute(qurry)
    print('Querry compleated')
    r = curs.fetchall()
    print('Querry data saved in variable')

    af_list = ['id_point',
            'id_sub_traj',
            'geom',
            'temps',
            'outlier',
            'grid_x',
            'grid_y',
            'date_2']
    print('af_list created')

    tracks = add_traces_from_lists(r,af_list)
    print('Data placed in track collection')
    print('Prefiltered num of traj ' + str(len(tracks)))

    #simplify
    for trace__ in tracks:
        trace__.cleanDuplicates("XY")
    print('Duplicates deleated num of traj ' + str(len(tracks)))

    id_traj = []
    
    tracks_simp = track_collection.TrackCollection()
    
    print('Starting simplicifation')
    for trace in tracks:

        trace_simp = simplify(trace, esp, mode = mode, time_max=time_max)
        tracks_simp.addTrack(trace_simp)

        id_traj.extend([trace.tid]*len(trace_simp))
        
    print('Simplification finished')
    print('Number of traj after filtering' + str(len(tracks_simp)))

    #create da table
    conn = psycopg2.connect(database=db, user='postgres')

    curs = conn.cursor()
    
    qurry = 'DROP TABLE IF EXISTS ' + head + 'da' + tail+ ';'
    curs.execute(qurry)
    conn.commit()
    print('Dropped table if exists')

    variables = """\
        id_point 	        integer, \n
        temps               time without time zone,\n
        geom                geometry,\n
        id_sub_traj         integer, \n
        id_traj             integer, \n
        date                date,\n
        next_id_point       integer, \n
        next_temps          time without time zone,\n
        next_geom           geometry,\n
        next_id_sub_traj    integer, \n
        next_id_traj        integer, \n
        x_grid              integer,\n
        y_grid              integer,\n
        next_x_grid         integer,\n
        next_y_grid         integer,\n
        x_coord				double precision,
        y_coord 			double precision,
        geom_line           geometry,
        da                  geometry  
        """

    table_name =  head + 'da' + tail

    if not cells:
        print('here 8')

        qurry = """\
                create table """ + table_name + """ (
                """+ variables +"""
                );
                """
        
        curs.execute(qurry)
        conn.commit()
    elif cells:

        print('here 8a')

        _,bb_2_list_da = table_partitioning(table_name, 
                   variables, 
                   'x_grid', 
                   'y_grid', 
                   bbox_grid, 
                   cells, 
                   cells,
                   db)
    
    conn = psycopg2.connect(database=db, user='postgres')
    print('Event table created')

    curs = conn.cursor()

    d  = list(zip(
        tracks_simp.getAnalyticalFeature('id_point')[0:-1],  # Pull the first 10 data points
        tracks_simp.getTimestamps_str()[0:-1],  # Pull the first 10 data points
        tracks_simp.getAnalyticalFeature('geom')[0:-1],  # Pull the first 10 data points
        tracks_simp.getAnalyticalFeature('id_sub_traj')[0:-1],  # Pull the first 10 data points
        id_traj[0:-1],  # Pull the first 10 data points
        tracks_simp.getAnalyticalFeature('date_2')[0:-1],  # Pull the first 10 data points

        tracks_simp.getAnalyticalFeature('id_point')[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getTimestamps_str()[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('geom')[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('id_sub_traj')[1:],  # Pull the next 10 data points (shifted by 1)
        id_traj[1:],  # Pull the next 10 data points (shifted by 1)

        tracks_simp.getAnalyticalFeature('grid_x')[0:-1],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('grid_y')[0:-1],
        tracks_simp.getAnalyticalFeature('grid_x')[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('grid_y')[1:]   # Pull the next 10 data points (shifted by 1)
    ))

    print('Data prepared')

    curs.executemany("""
            insert into """ + head + """da""" + tail+ """(
                id_point, 
                temps, 
                geom, 
                id_sub_traj, 
                id_traj,
                date,
                next_id_point,
                next_temps,
                next_geom,
                next_id_sub_traj,
                next_id_traj,
                x_grid,
                y_grid,
                next_x_grid,
                next_y_grid
            )
                VALUES( %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s                   
                        )
                """,d)

    conn.commit()
    curs.close()
    conn.close()
    print('DA table created')

    #populate da table
    conn = psycopg2.connect(database=db, user='postgres')

    curs = conn.cursor()

    print('Filtering DA table')

    qurry = """\

    delete from """ + head + """da""" + tail+ """
    where id_traj != next_id_traj;

    delete from """ + head + """da""" + tail+ """
    where id_point = next_id_point;

    delete from """ + head + """da""" + tail+ """
    where next_id_traj is null;

    update """ + head + """da""" + tail+ """ 
    set geom_line = st_makeline(geom,next_geom);

    -- delete from """ + head + """da""" + tail+ """
    -- where st_length(geom_line) >= 500;

    update """ + head + """da""" + tail+ """ 
    set da = ST_Simplify(st_buffer(ST_SetSRID(geom_line, 2154),""" + str(buffer_size)+ """),1);"""


    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close()
    print('Finished')

    return tracks, tracks_simp, id_traj

def simplify(track, tolerance, verbose=True, time_max = None):
     """
     Generic method to simplify a track. The process "Track simplification" 
     generally returns a new simplified track. Tolerance is in the unit 
     of track observation coordinates.
     
     Differents modes of simplification are implemented in tracklib:
          
     - MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)
               tolerance is max allowed deviation with respect to straight line
     - MODE_SIMPLIFY_VISVALINGAM (2)
               tolerance is maximal triangle area of 3 consecutive points
     - MODE_SIMPLIFY_SQUARING (3)
               tolerance is threshold on flat and right angles
     - MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION (4)
               tolerance is typical max deviation with respect to straight line
     - MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO (5)
               tolerance is typical elongation ratio of min bounding rectangle
     - MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION (6)
               tolerance is max allowed deviation with respect to straight line
     - MODE_SIMPLIFY_FREE (7)
               tolerance is a customed function to minimize
     - MODE_SIMPLIFY_FREE_MAXIMIZE (8)
               tolerance is a customed function to maximize

     """
     if time_max is None:
          return douglas_peucker(track, tolerance)
     else:
          track_simp = douglas_peucker(track, tolerance)
          return read_time(track, track_simp, time_max)
    
def douglas_peucker (track, eps):
    """
    Function to simplify a GPS track with Douglas-Peucker algorithm.

    The Douglas-Peucker algorithm reduce the number of a line by reducing
    the number of points. The result should keep the original shape.

    Parameters
    ----------
    :param track Track: GPS track
    :param eps float: length threshold epsilon (sqrt of triangle area)
    :return Track: simplified track

    """

    L = track.getObsList()
    
    temp_lists = {}
    if len(track.getListAnalyticalFeatures()) > 0:
        AF_list = track.getListAnalyticalFeatures()
        for list_name in (AF_list):
            temp_lists[list_name] = track.getAnalyticalFeature(list_name)  # Assign values to each list
   

    n = len(L)
    if n <= 2:
        track_sp = track.Track(L)
        if len(track.getListAnalyticalFeatures()) > 0:
            for af in AF_list:
                track_sp.createAnalyticalFeature(af, temp_lists[list_name])
        return track_sp

    dmax = 0
    imax = 0

    for i in range(0, n):
        x0 = L[i].position.getX()
        y0 = L[i].position.getY()
        xa = L[0].position.getX()
        ya = L[0].position.getY()
        xb = L[n - 1].position.getX()
        yb = L[n - 1].position.getY()
        d = distance_to_segment(x0, y0, xa, ya, xb, yb)
        if d > dmax:
            dmax = d
            imax = i

    if dmax < eps:
        track_sp = track.Track([L[0], L[n - 1]], user_id=track.uid, track_id=track.tid, base=track.base)
        if len(track.getListAnalyticalFeatures()) > 0:
            for af in AF_list:
                track_sp.createAnalyticalFeature(af, temp_lists[list_name][0:n-1])
        return track_sp
    else:
        XY1 = track.Track(L[0:imax], user_id=track.uid, track_id=track.tid, base=track.base)
        XY2 = track.Track(L[imax:n], user_id=track.uid, track_id=track.tid, base=track.base)
        if len(track.getListAnalyticalFeatures()) > 0:
            for af in AF_list:
                XY1.createAnalyticalFeature(af, temp_lists[list_name][0:imax])
                XY2.createAnalyticalFeature(af, temp_lists[list_name][imax:n])

        return douglas_peucker(XY1, eps) + douglas_peucker(XY2, eps)
    
def distance_to_segment(x0: float, y0: float, x1: float, y1: float, x2: float, y2: float) -> float:   
    """Function to compute distance between a point and a segment

    :param x0: point coordinate X
    :param y0: point coordinate Y
    :param x1: segment first point X
    :param y1: segment first point Y
    :param x2: segment second point X
    :param y2: segment second point Y

    :return: Distance between point and projection coordinates
    """

    # Segment length
    l = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))+0.00000000000000000000000000000000000000001

    # Normalized scalar product
    psn = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / l

    X = max(x1, x2)
    Y = max(y1, y2)

    x = min(x1, x2)
    y = min(y1, y2)

    xproj = x1 + psn / l * (x2 - x1)
    yproj = y1 + psn / l * (y2 - y1)

    xproj = min(max(xproj, x), X)
    yproj = min(max(yproj, y), Y)

    # Compute distance
    d = math.sqrt((x0 - xproj) * (x0 - xproj) + (y0 - yproj) * (y0 - yproj))

    return d

def read_time(track, track_simp, time_max):
    j = 0  # Initialize j for tracking position in the track list
    i = 0  # Initialize i for tracking position in the track_simp list
    
    while i < len(track_simp) - 1:  # Ensure i doesn't exceed the second-to-last element of track_simp
        #print(f"Checking i = {i}, timestamp = {track_simp.getObs(i).timestamp}")
        
        # Check if the time gap between consecutive observations in track_simp exceeds the max time threshold
        if track_simp.getObs(i + 1).timestamp - track_simp.getObs(i).timestamp > time_max:
            # Ensure j is at least i (moving j forward if needed)
            if j < i:
                j = i
            
            # Move j to the correct position in track where the timestamp is just before the one in track_simp
            while j < len(track) and track.getObs(j).timestamp <= track_simp.getObs(i).timestamp:
                #print('Moving j to position before track_simp[i]')
                j += 1
            if track.getObs(j).timestamp == track_simp.getObs(i + 1).timestamp:
                #print('there are no inbetween time steps')
                i+=1
                continue
            while j < len(track) and track.getObs(j).timestamp < track_simp.getObs(i + 1).timestamp and track.getObs(j).timestamp-track_simp.getObs(i).timestamp < time_max:
                j +=1
            if  track.getObs(j-1).timestamp > track_simp.getObs(i).timestamp:
                    track_simp.insertObs(track.getObs(j), i + 1)
            elif track.getObs(j-1).timestamp == track_simp.getObs(i).timestamp:
                    track_simp.insertObs(track.getObs(j), i + 1)
            else:
                print('Sothing BAD')
                break
        i += 1

    return track_simp

def add_traces_from_lists(LINES, AF_list):


    tracks = track_collection.TrackCollection
    time_fmt_save = ObsTime.getReadFormat()
    ObsTime.setReadFormat('4Y-2M-2DT2h:2m:2sZ')

    if len(AF_list) != len(LINES[0])- 6:
        raise WrongArgumentError("Error: AF_list : " + str(len(AF_list)) + " does not match extra data " + str(len(LINES[0])- 6))
    else:
        print('Made it to make AF')
        temp_lists = {}
        # Dynamically create lists based on the list_names and values
        for list_name in (AF_list):
            temp_lists[list_name] = []  # Assign values to each list
    
    trace = track.Track([],1)
    trace.no_data_value = -99999
    trace.uid = LINES[0][0]
    trace.tid = LINES[0][1]

    print('created the first trace : ' + str(trace.tid))
    for row in LINES:
        
        id_user = row[0]
        id_traj = row[1]
        EE = row[2]
        NN = row[3]
        UU = row[4]
        TT  = row[5]
        sridd = "ENU"
        #if not row[6] or row[6] == '2154':
        #    sridd = 'ENU'
               
        if id_user != trace.uid or id_traj != trace.tid:
            if trace is None:
                continue
            if trace.size() <= 0:
                continue
            for af in AF_list:
                trace.createAnalyticalFeature(af, temp_lists[af])
                temp_lists[af] = []
            print(type(trace))
            tracks.addTrack(trace)
            trace = track.Track([],1)
            trace.no_data_value = -99999
            trace.uid = id_user
            trace.tid = id_traj


        if id_user == trace.uid and id_traj == trace.tid:
            if TT: 
                time = ObsTime.readTimestamp(str(TT))
            else:
                time = ObsTime()

            if EE == None:
                E = trace.no_data_value
            else:
                try:
                    E = (float)(EE)
                except:
                    raise WrongArgumentError("Parameter E or N is not an instantiation of a float ()")

            if NN == None:
                N = trace.no_data_value
            else:
                try:
                    N = (float)(NN)
                except:
                    raise WrongArgumentError("Parameter E or N is not an instantiation of a float ()")

            if UU == None:
                U = trace.no_data_value
            else:
                try:
                    U = (float)(UU)
                except:
                    raise WrongArgumentError("Parameter E or N is not an instantiation of a float ()")


            if (int(E) != trace.no_data_value) and (int(N) != trace.no_data_value):
                if not sridd in [
                    "ENUCOORDS", "ENU", "GEOCOORDS", "GEO", "ECEFCOORDS", "ECEF",
                ]:
                    raise WrongArgumentError("Error: unknown coordinate type [" + str(sridd) + "]")
                if sridd in ["ENUCOORDS", "ENU"]:
                    point = Obs(ENUCoords(E, N, U), time)
                #if sridd in ["GEOCOORDS", "GEO"]:
                #    point = Obs(GeoCoords(E, N, U), time)
                #if sridd in ["ECEFCOORDS", "ECEF"]:
                #    point = Obs(ECEFCoords(E, N, U), time)
                trace.addObs(point)

            else:
                no_data = trace.no_data_value
                trace.addObs(Obs(makeCoords(no_data, no_data, no_data, sridd), time))

            for i, af in enumerate(AF_list):
                temp_lists[af].append(row[i+6])
    if trace is not None and trace.size() > 0:
        for af in AF_list:
            trace.createAnalyticalFeature(af, temp_lists[af])
        tracks.addTrack(trace)

    return tracks

def create_encounter_events(source_ppa, source_da, source_pairings, head, tail, comp_type, db, search_da = [], search_ppa = []):
    
    # Was create_spottings 
    #spottings became encounter_event

    if comp_type.lower() == 'grid':
        search_by = """\
                            abs(a_.x_grid-b_.x_grid) <= 35
                        and abs(a_.y_grid-b_.y_grid) <= 35
                        and a_.temps <= b_.next_temps 
                        and	b_.temps <= a_.next_temps
                        and	st_intersects(a_.ppa, b_.da)
                    """
    elif comp_type.lower() == 'geom':
        search_by = """\
                            st_intersects(a_.ppa, b_.da)
                        and a_.temps <= b_.next_temps 
                        and	b_.temps <= a_.next_temps
                    """
    else:
        print('Search type not implamented')

    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    qurry = """\
        DROP TABLE IF EXISTS """ + head + """encounter_event""" + tail+ """;
        CREATE TABLE """ + head + """encounter_event""" + tail+ """(
            id_spotting SERIAL PRIMARY KEY,
            id_traj integer,
            id_sub_traj integer,
                id_point integer,
                geom geometry,
                temps time without time zone,
            
                next_id_point integer,
                next_geom geometry,
                next_temps time without time zone,
            
                geom_line geometry,
                ppa geometry,
            
            id_traj_2 integer,
            id_sub_traj_2 integer,
                id_point_2 integer,
                geom_2 geometry,
                temps_2 time without time zone,
            
                next_id_point_2 integer,
                next_geom_2 geometry,
                next_temps_2 time without time zone,
            
                geom_line_2 geometry,
                da geometry,
            shortest_length numeric
        );
    """

    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close()


    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    qurry = """\
        --Finds and saves overlaps
        insert into """ + head + """encounter_event""" + tail+ """(
            id_traj,
            id_sub_traj,
                id_point ,
                geom ,
                temps ,
            
                next_id_point ,
                next_geom ,
                next_temps ,
                
                geom_line,
                -- ppa ,
            
            id_traj_2 ,
            id_sub_traj_2,
                id_point_2 ,
                geom_2 ,
                temps_2 ,
            
                next_id_point_2 ,
                next_geom_2 ,
                next_temps_2 ,
            
                geom_line_2 ,
                -- da,
                shortest_length
                )
                
        select 
            a_.id_traj ,
            a_.id_sub_traj,
                a_.id_point ,
                a_.geom ,
                a_.temps ,
            
                a_.next_id_point ,
                a_.next_geom ,
                a_.next_temps ,
            
                b_.geom_line,
                -- a_.ppa ,
            
            b_.id_traj ,
            b_.id_sub_traj,
                b_.id_point ,
                b_.geom ,
                b_.temps ,
            
                b_.next_id_point ,
                b_.next_geom ,
                b_.next_temps ,
            
                b_.geom_line ,
                -- b_.da,
            ST_Distance(a_.geom_line, b_.geom_line)
        FROM """ + source_ppa + """ AS a_
        inner join """ + source_pairings + """ as c_
            on c_.id_traj_1 = a_.id_traj
        INNER JOIN """ + source_da + """ AS b_
            on c_.id_traj_2 = b_.id_traj
        where""" + search_by 

    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close()
    return qurry

def assign_encoutners(source_table,  db):

    #qurrys specific data

    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    save_print = ObsTime.getPrintFormat()
    ObsTime.setPrintFormat("4Y-2M-2D 2h:2m:2s")
    
    
    qurry = """\

        SELECT 
            id_spotting,

            id_traj,
            id_traj_2,
            id_sub_traj,
            id_sub_traj_2,

            geom,
            next_geom,
            geom_2,
            next_geom_2,

            temps_2,
            next_temps_2

        -- date(temps)     as date_human,
        -- date(temps_2)   as date_animal

        FROM """ + source_table +"""
            -- and time_h is not null
            -- and abs(extract(doy from time_h)-extract(doy from temps)) <= 15
            -- and date(time_h) != '1970-00-00'


        order by 
            id_traj,
            id_traj_2, 
            temps_2
        """
    curs.execute(qurry)

    id_spotting=[]

    id_traj=[]
    id_traj_2=[]
    id_sub_traj=[]
    id_sub_traj_2=[]

    geom=[]
    next_geom=[]
    geom_2=[]
    next_geom_2=[]

    temps_2=[]
    next_temps_2=[]

    date_human=[]
    date_animal=[]

    trace  = track.Track([],1)

    for row in curs.fetchall():

        id_spotting.append(row[0])

        id_traj.append(row[1])
        id_traj_2.append(row[2])
        id_sub_traj.append(row[3])
        id_sub_traj_2.append(row[4])

        geom.append(row[5])
        next_geom.append(row[6])
        geom_2.append(row[7])
        next_geom_2.append(row[8])

        temps_2.append(row[9])
        next_temps_2.append(row[10])

        #date_human.append(row[11])
        #date_animal.append(row[12])

        trace.addObs(Obs(ENUCoords(row[4],row[5],-1),ObsTime.readTimestamp('1970-01-01 '+str(row[9]))))
            
    trace.createAnalyticalFeature('id_spotting', id_spotting)
    trace.createAnalyticalFeature('id_traj', id_traj)
    trace.createAnalyticalFeature('id_traj_2', id_traj_2)
    #trace.createAnalyticalFeature('date_h', date_human)
    #trace.createAnalyticalFeature('date_a', date_animal)


    trace.addAnalyticalFeature(trace_segment)
    tkl.segmentation(trace, ["trace_segment"],"out",[0.5],tkl.MODE_COMPARAISON_AND)
    tracks = tkl.split(trace, "out")
    
    for j in range(len(tracks)):
        id_encounter_create(tracks,j)


    d = list(zip(tracks.getAnalyticalFeature('id_spotting'),tracks.getAnalyticalFeature('id_encounter')))

    psycopg2.extensions.register_adapter(float, nan_to_null)
    psycopg2.extensions.register_adapter(np.bool_, bool_to_bool)

    conn = psycopg2.connect(database= db, user='postgres')

    curs = conn.cursor()

    curs.execute("""
    alter table """ + source_table + """
    add id_encounter integer""")


    curs.executemany("""
    update """ + source_table + """
    set id_encounter = %s
    where id_spotting = %s
    """,(list(zip(tracks.getAnalyticalFeature('id_encounter'),
        tracks.getAnalyticalFeature('id_spotting')))))


    conn.commit()
    curs.close()
    conn.close()
    
    
    ObsTime.setPrintFormat(save_print)

def trace_segment (track, i):
    id_i = track.getObsAnalyticalFeature('id_traj',i)
    id_2 = track.getObsAnalyticalFeature('id_traj',i+1)
    
    name_i = track.getObsAnalyticalFeature('id_traj_2',i)
    name_2 = track.getObsAnalyticalFeature('id_traj_2',i+1)

    time_gap = track.getT(i+1) - track.getT(i)
    
    if id_i != id_2 or name_i != name_2 or time_gap > 8 * 60:
        return 1
    else:
        return 0

def id_encounter_create(track,j):
    track[j].createAnalyticalFeature('id_encounter',j)

def nan_to_null(f,
        _NULL=psycopg2.extensions.AsIs('NULL'),
        _Float=psycopg2.extensions.Float):
    if not np.isnan(f):
        return _Float(f)
    return _NULL

def bool_to_bool(b,
        _NULL=psycopg2.extensions.AsIs('NULL'),
        _Bool=psycopg2.extensions.Boolean):
    if isinstance(b, np.bool_):
        return _Bool(b)
    return _NULL