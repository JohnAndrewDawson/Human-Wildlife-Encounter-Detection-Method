#%%# %%
#from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsPointXY, QgsProject
from PyQt5.QtCore import QVariant
import psycopg2
import time
start_time = time.time()
import numpy as np
import ast

from ViewshedAnalysis.algorithms.viewshed_intervisibility import Intervisibility
from ViewshedAnalysis.algorithms.modules import Raster as rst
from ViewshedAnalysis.algorithms.modules import Points as pts
from ViewshedAnalysis.algorithms.modules import visibility as ws

def pairs (self,targets):

     for pt1 in self.pt:

        id1 = self.pt[pt1]["id"]        
        x,y = self.pt[pt1]["pix_coord"]
        
        r = self.pt[pt1]["radius"] #it's pixelised after take !!

        radius_pix= int(r); r_sq = r**2
        
        max_x, min_x = x + radius_pix, x - radius_pix
        max_y, min_y = y + radius_pix, y - radius_pix

        self.pt[pt1]["targets"]={}
        
        pt2 = pt1
        value = targets.pt[pt1]

        id2 = targets.pt[pt2]["id"]

        x2, y2 = value["pix_coord"]

        if id1==id2 and x == x2 and y==y2 : 
            self.pt[pt1]["targets"][pt2]=value
            continue
            
        if min_x <= x2 <= max_x and min_y <= y2 <= max_y:
            if  (x-x2)**2 + (y-y2)**2 <= r_sq:

                self.pt[pt1]["targets"][pt2]=value

def processAlgorithm_pairs(self, parameters, context, feedback):
    print('Correct Vis')
    raster = self.parameterAsRasterLayer(parameters,self.DEM, context)
    observers = self.parameterAsSource(parameters,self.OBSERVER_POINTS,context)
    targets = self.parameterAsSource(parameters,self.TARGET_POINTS,context)
    write_negative = self.parameterAsBool(parameters,self.WRITE_NEGATIVE,context)

    useEarthCurvature = self.parameterAsBool(parameters,self.USE_CURVATURE,context)
    refraction = self.parameterAsDouble(parameters,self.REFRACTION,context)
    precision = 1#self.parameterAsInt(parameters,self.PRECISION,context)

    
    dem = rst.Raster(raster.source())
   
    o= pts.Points(observers)       
    t= pts.Points(targets)
    
    setattr(o, 'pairs', pairs)
    #setattr(t, 'pairs', pairs)
    
    required =["observ_hgt", "radius"]

    miss1 = o.test_fields (required)
    miss2 = t.test_fields (required)

    if miss1 or miss2:

        msg = ("\n ********** \n MISSING FIELDS! \n" +
            "\n Missing in observer points: " + ", ".join(miss1) +
            "\n Missing in target points: " + ", ".join(miss2))
           
        raise QgsProcessingException(msg)
             
    o.take(dem.extent, dem.pix)
    t.take(dem.extent, dem.pix)

    if o.count == 0 or t.count == 0:

        msg = ("\n ********** \n ERROR! \n"
            "\n No view points/target points in the chosen area!")
        
        raise QgsProcessingException(msg)
       
    fds = [("Source", QVariant.String, 'string',255),
           ("Target", QVariant.String, 'string',255),
           ("TargetSize", QVariant.Double, 'double',10,3)]

    qfields = QgsFields()
    for f in fds : qfields.append(QgsField(*f))
    
    (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                        qfields,
                        QgsWkbTypes.LineStringZ, #We store Z Geometry now
                        o.crs)
                        
    feedback.setProgressText("*1* Constructing the network")
    
    print('The network is just pairs')
    o.pairs(o,t)
   
    dem.set_master_window(o.max_radius,
                        curvature =useEarthCurvature,
                        refraction = refraction )
    
    cnt = 0
    
    feedback.setProgressText("*2* Testing visibility")   
    for key, ob in o.pt.items():

        ws.intervisibility(ob, dem, interpolate = precision)
        
        #Get altitude abs for observer
        x,y= ob["pix_coord"]
        radius_pix = dem.radius_pix
        dem.open_window ((x,y))
        data= dem.window
        z_abs =   ob["z"] + data [radius_pix,radius_pix]
        #3D point         
        p1 = QgsPoint(float(ob["x_geog"]), float(ob["y_geog"] ), float(ob["z"]+data [radius_pix,radius_pix]))

        for key, tg in ob["targets"].items():
            
            h = tg["depth"]           
            
            if not write_negative:
                if h<0: continue
            #Get altitude abs for target
            x_tg, y_tg = tg["pix_coord"]  # Target pixel coordinates
            dem.open_window((x_tg, y_tg))
            data= dem.window
            z =   data [radius_pix,radius_pix]
            try: z_targ = tg["z_targ"]
            except : 
                try: z_targ = tg["z"] 
                except : z_targ = 0
            
            p2 = QgsPoint(float(tg["x_geog"]), float(tg["y_geog"] ), float(z+z_targ))

            feat = QgsFeature()
            

            feat.setGeometry(QgsGeometry.fromPolyline([p1, p2]))

            feat.setFields(qfields)
            feat['Source'] = ob["id"]
            feat['Target'] = tg["id"]
            feat['TargetSize'] = float(h) #.                
       
            sink.addFeature(feat, QgsFeatureSink.FastInsert) 
 
        cnt +=1
        feedback.setProgress(int((cnt/o.count) *100))
        if feedback.isCanceled(): return {}

    feedback.setProgressText("*3* Drawing the network")
	

    return {self.OUTPUT: dest_id}

def viss(encounter_event_table, 
         close_points_table, 
         da_tables,
         height_animal, 
         height_human, 
         db):


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

        return result, gridx , sorted_truefalse, attrs

    except Exception as e:
        print(f"An error occurred: {e}")

# Bind the 'pairs' function to the Points class as a method
#setattr(pts, 'pairs', pairs)

# Bind the 'processAlgorithm_pairs' function to the Intervisibility class as a method
setattr(Intervisibility, 'processAlgorithm', processAlgorithm_pairs)


result, lst1 , lst2, attrs  = viss( 'p2_encounter_event', 
         'close_points_table', 
         'da_tables',
         1, 
         1.6, 
         'ResRoute')
