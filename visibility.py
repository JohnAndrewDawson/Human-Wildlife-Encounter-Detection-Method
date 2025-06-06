#from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsProject
from PyQt5.QtCore import QVariant
import psycopg2
import time
start_time = time.time()
import numpy as np

def viss(encounter_event_table, close_points_table, da_tables,height_animal, height_human, db):


    ll_x = 924987.5
    ll_y = 6500012.5


    conn = psycopg2.connect(database= db, user='postgres')
    curs = conn.cursor()
    
    # Your query to fetch the data
    query = """\
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2
        FROM """+ encounter_event_table +"""
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2            
        FROM """+ encounter_event_table +""" 
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(geom)-"""+ str(ll_y) +""")/25 )as y_grid,
            floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2 
        FROM """+ encounter_event_table +""" 
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2             
        FROM """+ encounter_event_table +""" 
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + """+ str(ll_x) +"""+25/2 AS x_c,
        y_grid * 25 + """+ str(ll_y) +"""+25/2 AS y_c,
        x_grid_2 * 25 + """+ str(ll_x) +"""+25/2 AS x_c2,
        y_grid_2 * 25 + """+ str(ll_y) +"""+25/2 AS y_c2
    FROM ttt
    -- where id_encounter_event > 500
    -- and id_encounter_event < 60000
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + """+ str(ll_x) +"""+25/2,
        y_grid * 25 + """+ str(ll_y) +"""+25/2,
        x_grid_2 * 25 + """+ str(ll_x) +"""+25/2,
        y_grid_2 * 25 + """+ str(ll_y) +"""+25/2
    """

    # Execute the query
    curs.execute(query)
    print('query ran : ')
    # Create the vector layer (memory layer in EPSG:2154)
    layer = QgsVectorLayer("Point?crs=EPSG:2154", "MemoryLayer_1", "memory")
    layer2 = QgsVectorLayer("Point?crs=EPSG:2154", "MemoryLayer_2", "memory")

    # Add fields to the layer
    fields = [QgsField('id', QVariant.String)]  # Field for storing 'id_1'
    layer.dataProvider().addAttributes(fields)
    layer.updateFields()

    layer2.dataProvider().addAttributes(fields)
    layer2.updateFields()

    QgsProject.instance().addMapLayer(layer)
    QgsProject.instance().addMapLayer(layer2)

    # Access the data provider
    provider = layer.dataProvider()
    provider2 = layer2.dataProvider()
    gridx = []
    gridy = []
    gridx_2 = []
    gridy_2 = []
    lst2 = []
    id_1=[]
    id_2 =[]
    # Loop through the fetched rows and add them as features to the layer
    for row in curs.fetchall():  # Fetch all rows in one go
        id_1.append(int(row[0]))
        id_2.append(int(row[1]))
        gridx.append(int(row[2]))
        gridy.append(int(row[3]))
        gridx_2.append(int(row[4]))
        gridy_2.append(int(row[5]))
        
        feature = QgsFeature()
        feature2 = QgsFeature()

        # Set the attributes (id_1 is the first column in the result set)
        feature.setAttributes([row[0]])  # row[0] corresponds to 'id_1'
        feature2.setAttributes([row[1]])  # row[0] corresponds to 'id_1'

        # Create the geometry (Point) from x_c and y_c (columns 2 and 3 in the result set)
        point = QgsGeometry.fromPointXY(QgsPointXY(row[6], row[7]))  # x_c and y_c
        point2 = QgsGeometry.fromPointXY(QgsPointXY(row[8], row[9]))  # x_c and y_c
        
        feature.setGeometry(point)
        feature2.setGeometry(point2)

        # Add the feature to the layer
        provider.addFeature(feature)
        provider2.addFeature(feature2)

    # Refresh the layer to update the view
    layer.updateExtents()
    layer2.updateExtents()

    # Ensure the layer is added to the QGIS project
    #QgsProject.instance().addMapLayer(layer)
    #QgsProject.instance().addMapLayer(layer2)

    rad = 5000
    obs_h_1 = height_animal
    obs_h_2 = height_human
    
    lst =[]
    lstt = []
    print('about to run animal points')
    ani_view = processing.run("visibility:createviewpoints", {
        "OBSERVER_POINTS" :  layer,
        'OBSERVER_ID': 'grid_id',
        "DEM" : 'D:/AOI/bouge_elev.tif',
        "RADIUS": rad,
        "OBS_HEIGHT": obs_h_1,
        "TARGET_HEIGHT": obs_h_2,
        "OUTPUT" : QgsProcessing.TEMPORARY_OUTPUT
        #"OUTPUT": 'C:/Users/JADawson/Desktop/Qgis_Pyhton/temp_files/dl_view'
        })


    human_view = processing.run("visibility:createviewpoints", {
        "OBSERVER_POINTS" :  layer2,
        'OBSERVER_ID': 'grid_id_2',
        "DEM" : 'D:/AOI/bouge_elev.tif',
        "RADIUS": rad,
        "OBS_HEIGHT": obs_h_2,
        "TARGET_HEIGHT": obs_h_1,
        "OUTPUT" : QgsProcessing.TEMPORARY_OUTPUT
        #"OUTPUT": 'C:/Users/JADawson/Desktop/Qgis_Pyhton/temp_files/dl_view_2'
        })
        
    try:
        visibility_net = processing.run("visibility:intervisibility", {
            "OBSERVER_POINTS": ani_view['OUTPUT'],
            "TARGET_POINTS"  : human_view['OUTPUT'],
            "WRITE_NEGATIVE" : True,
            "DEM": 'D:/AOI/bouge_elev.tif',
            "OUTPUT" : QgsProcessing.TEMPORARY_OUTPUT
            # "OUTPUT": 'C:/Users/JADawson/Desktop/Qgis_Pyhton/temp_files/dl_vi.shp'
        })['OUTPUT']
        
        QgsProject.instance().addMapLayer(visibility_net)
        
        
        print('here 1')
        # Check feature count
        #if visibility_net.featureCount() >= 1:
        #    print('There is visibility')
        #    lst.append('true')
        #elif visibility_net.featureCount() == 0:
        #    print('There is no visibility')
        #    lst.append('false')
        #else:
        #    lst.append('Something weird happened')
        
        features = visibility_net.getFeatures()
        
        print('here 2')

        for feat in features:
            attrs= feat.attributes()

            lst.append(int(attrs[0])-1)
            lstt.append(int(attrs[1])-1)

            #print(attrs)
            if attrs[2] >= 0:
                lst2.append(True)
            else:
                lst2.append(False)

        #QgsProject.instance().addMapLayer(visibility_net)
        
        # Step 1: Create a dictionary to group booleans by ID
        #id_dict = {}
        #for id_, bool_val in zip(lst1, lst2):
        #    if id_ not in id_dict:
        #        id_dict[id_] = False  # Initialize as False
        #    id_dict[id_] |= bool_val  # Use OR to combine booleans

        # Step 2: Convert the dictionary back to a condensed list of (ID, bool) tuples
        #result = [(id_, value) for id_, value in id_dict.items()]
        #len(result)
        
        
        sorted_truefalse = [None] * len(lst2)
        
        for i, val in enumerate(lst):            
            sorted_truefalse[val] = lst2[i]
            
        """    
        for i, val in enumerate(lst):
            if 0 <= val < len(sorted_truefalse):
                sorted_truefalse[val] = lst2[i]
            else:
                pass

        # Then after the loop, replace all None with False:
        sorted_truefalse = [v if v is not None else True for v in sorted_truefalse]        
        """
 
        result = list(zip(gridx,gridy,gridx_2,gridy_2, sorted_truefalse))

        
        conn = psycopg2.connect(database=db, user='postgres')
        curs = conn.cursor()

        query = """\
        DROP TABLE IF EXISTS vis_grid;
        create table vis_grid(
        x_grid integer,
        y_grid integer,
        x_grid_2 integer,
        y_grid_2 integer,
        vis boolean);
        
        
        """
        curs.execute(query)
        print('here 10')

        curs.executemany("""
            insert into vis_grid(
            x_grid,
            y_grid,
            x_grid_2,
            y_grid_2,
            vis
        )
            VALUES( %s,
                    %s,
                    %s,
                    %s,
                    %s
                    )
            """,result)
        
        print('here 11')

        conn.commit()
        curs.close()
        conn.close()
            
        print('made it here about to print')    
        len(result)
        len(gridx)
        len(sorted_truefalse)
        len(attrs)
        return result, gridx , sorted_truefalse, attrs

    except Exception as e:
        print(f"An error occurred: {e}")
		
	




    conn = psycopg2.connect(database= db, user='postgres')
    curs = conn.cursor()
    ll_x = 924987.5
    ll_y = 6500012.5
    query = """\
    DROP TABLE IF EXISTS ttt;

	CREATE TEMPORARY TABLE ttt AS
	(SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2
        FROM """+ encounter_event_table +"""
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2            
        FROM """+ encounter_event_table +""" 
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(geom)-"""+ str(ll_y) +""")/25 )as y_grid,
            floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2 
        FROM """+ encounter_event_table +""" 
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
            floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
            floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
            floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2             
        FROM """+ encounter_event_table +""" 
        ORDER BY id_encounter_event, x_grid, y_grid
    );

				
	drop table if exists temppp;
	CREATE TEMPORARY TABLE temppp (
		id_encounter_event INTEGER PRIMARY KEY,
		vis BOOLEAN);

	insert into temppp (id_encounter_event, vis)	
	select a_.id_encounter_event, bool_or(b_.vis)
	from ttt as a_
	left join vis_grid as b_
		on			a_.x_grid	= b_.x_grid
		and 		a_.y_grid	= b_.y_grid
		and 		a_.x_grid_2	= b_.x_grid_2
		and 		a_.y_grid_2	= b_.y_grid_2
	group by id_encounter_event;

	alter table """+ encounter_event_table +"""
	DROP COLUMN IF EXISTS vis_grid;
						
	alter table """+ encounter_event_table +"""
	add vis_grid boolean;

	drop index if exists id_encounter_event_"""+ encounter_event_table +"""_index;
	CREATE INDEX id_encounter_event_"""+ encounter_event_table +"""_index 
	ON """+ encounter_event_table +"""(id_encounter_event);


	UPDATE """+ encounter_event_table +""" as a_
	SET vis_grid = (
	SELECT vis
	FROM temppp
	WHERE temppp.id_encounter_event = a_.id_encounter_event)"""
    curs.execute(query)
    
    conn.commit()
    curs.close()
    conn.close()

result, lst1 , lst2, attrs  = viss('dldlencounter_event',
                                    'dldlclose_points_animal',
                                    'dldlhda',
                                    1,
                                    1.6,
                                    'ResRoute')