# Python Console
# Use iface to access QGIS API interface or type help(iface) for more info
# Security warning: typing commands from an untrusted source can harm your computer
exec(Path('C:/Users/JADawson/Desktop/Paper_3/only_updates_the_vis_grid.py').read_text())
   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2            
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25 )as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2 
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2             
        FROM exp_encounter_event_default
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2 AS x_c,
        y_grid * 25 + 6500012.5+25/2 AS y_c,
        x_grid_2 * 25 + 924987.5+25/2 AS x_c2,
        y_grid_2 * 25 + 6500012.5+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM vis_grid as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2,
        y_grid * 25 + 6500012.5+25/2,
        x_grid_2 * 25 + 924987.5+25/2,
        y_grid_2 * 25 + 6500012.5+25/2
    
query ran : 
About to run intervisibility with rad = 1033.4077351297235
must match
35462
4
4
----------
Batch number : 0
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 0
Batch number : 1
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 1
Batch number : 2
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 2
Batch number : 3
Human point length : 35462
Animal point length : 35462
Correct Vis
The network is just pairs
itervis count : 35462
intervis count35462
35462
35462
about to create sorted
created sorted
about to zip results
4
35462
zipped results
here 11
Finished and commited batch 3
--- 257.9504289627075 seconds ---
exec(Path('C:/Users/JADawson/AppData/Local/Temp/tmpjgem69k7.py').read_text())
   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2
        FROM exp_encounter_event_hda_500
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2            
        FROM exp_encounter_event_hda_500
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25 )as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2 
        FROM exp_encounter_event_hda_500
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2             
        FROM exp_encounter_event_hda_500
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2 AS x_c,
        y_grid * 25 + 6500012.5+25/2 AS y_c,
        x_grid_2 * 25 + 924987.5+25/2 AS x_c2,
        y_grid_2 * 25 + 6500012.5+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM vis_grid as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2,
        y_grid * 25 + 6500012.5+25/2,
        x_grid_2 * 25 + 924987.5+25/2,
        y_grid_2 * 25 + 6500012.5+25/2
    
query ran : 
About to run intervisibility with rad = 1357.2290960680157
must match
27426
7
7
----------
Batch number : 0
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
7
100000
zipped results
here 11
Finished and commited batch 0
Batch number : 1
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
7
100000
zipped results
here 11
Finished and commited batch 1
Batch number : 2
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
7
100000
zipped results
here 11
Finished and commited batch 2
Batch number : 3
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
7
100000
zipped results
here 11
Finished and commited batch 3
Batch number : 4
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
7
100000
zipped results
here 11
Finished and commited batch 4
Batch number : 5
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
7
100000
zipped results
here 11
Finished and commited batch 5
Batch number : 6
Human point length : 27426
Animal point length : 27426
Correct Vis
The network is just pairs
itervis count : 27426
intervis count27426
27426
27426
about to create sorted
created sorted
about to zip results
7
27426
zipped results
here 11
Finished and commited batch 6
--- 731.7011177539825 seconds ---
exec(Path('C:/Users/JADawson/AppData/Local/Temp/tmpblju618o.py').read_text())
   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2
        FROM exp_encounter_event_d_gap_h_none
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2            
        FROM exp_encounter_event_d_gap_h_none
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25 )as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2 
        FROM exp_encounter_event_d_gap_h_none
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2             
        FROM exp_encounter_event_d_gap_h_none
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2 AS x_c,
        y_grid * 25 + 6500012.5+25/2 AS y_c,
        x_grid_2 * 25 + 924987.5+25/2 AS x_c2,
        y_grid_2 * 25 + 6500012.5+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM vis_grid as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2,
        y_grid * 25 + 6500012.5+25/2,
        x_grid_2 * 25 + 924987.5+25/2,
        y_grid_2 * 25 + 6500012.5+25/2
    
query ran : 
About to run intervisibility with rad = 13279.837821460475
must match
2574
1
1
----------
Batch number : 0
Human point length : 2574
Animal point length : 2574
Correct Vis
The network is just pairs
itervis count : 2574
intervis count2574
2574
2574
about to create sorted
created sorted
about to zip results
1
2574
zipped results
here 11
Finished and commited batch 0
--- 71.85568189620972 seconds ---
exec(Path('C:/Users/JADawson/AppData/Local/Temp/tmplwszmapf.py').read_text())
   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2
        FROM exp_encounter_event_d_gap_a_none
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2            
        FROM exp_encounter_event_d_gap_a_none
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25 )as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2 
        FROM exp_encounter_event_d_gap_a_none
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2             
        FROM exp_encounter_event_d_gap_a_none
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2 AS x_c,
        y_grid * 25 + 6500012.5+25/2 AS y_c,
        x_grid_2 * 25 + 924987.5+25/2 AS x_c2,
        y_grid_2 * 25 + 6500012.5+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM vis_grid as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2,
        y_grid * 25 + 6500012.5+25/2,
        x_grid_2 * 25 + 924987.5+25/2,
        y_grid_2 * 25 + 6500012.5+25/2
    
query ran : 
About to run intervisibility with rad = 4439.138739427445
must match
15773
1
1
----------
Batch number : 0
Human point length : 15773
Animal point length : 15773
Correct Vis
The network is just pairs
itervis count : 15773
intervis count15773
15773
15773
about to create sorted
created sorted
about to zip results
1
15773
zipped results
here 11
Finished and commited batch 0
--- 63.284629344940186 seconds ---
exec(Path('C:/Users/JADawson/Desktop/Paper_3/only_updates_the_vis_grid.py').read_text())
   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2            
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25 )as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2 
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2             
        FROM exp_encounter_event_default
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2 AS x_c,
        y_grid * 25 + 6500012.5+25/2 AS y_c,
        x_grid_2 * 25 + 924987.5+25/2 AS x_c2,
        y_grid_2 * 25 + 6500012.5+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM vis_grid_chamois_8_dm as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2,
        y_grid * 25 + 6500012.5+25/2,
        x_grid_2 * 25 + 924987.5+25/2,
        y_grid_2 * 25 + 6500012.5+25/2
    
query ran : 
About to run intervisibility with rad = 1033.4077351297235
must match
35462
4
4
----------
Batch number : 0
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 0
Batch number : 1
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 1
Batch number : 2
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 2
Batch number : 3
Human point length : 35462
Animal point length : 35462
Correct Vis
The network is just pairs
itervis count : 35462
intervis count35462
35462
35462
about to create sorted
created sorted
about to zip results
4
35462
zipped results
here 11
Finished and commited batch 3
--- 341.19658970832825 seconds ---
exec(Path('C:/Users/JADawson/Desktop/Paper_3/only_updates_the_vis_grid.py').read_text())
   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2            
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25 )as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2 
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2             
        FROM exp_encounter_event_default
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2 AS x_c,
        y_grid * 25 + 6500012.5+25/2 AS y_c,
        x_grid_2 * 25 + 924987.5+25/2 AS x_c2,
        y_grid_2 * 25 + 6500012.5+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM vis_grid_chamois_12_dm as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2,
        y_grid * 25 + 6500012.5+25/2,
        x_grid_2 * 25 + 924987.5+25/2,
        y_grid_2 * 25 + 6500012.5+25/2
    
query ran : 
About to run intervisibility with rad = 1033.4077351297235
must match
35462
4
4
----------
Batch number : 0
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 0
Batch number : 1
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 1
Batch number : 2
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 2
Batch number : 3
Human point length : 35462
Animal point length : 35462
Correct Vis
The network is just pairs
itervis count : 35462
intervis count35462
35462
35462
about to create sorted
created sorted
about to zip results
4
35462
zipped results
here 11
Finished and commited batch 3
--- 348.2989032268524 seconds ---
exec(Path('C:/Users/JADawson/Desktop/Paper_3/only_updates_the_vis_grid.py').read_text())
   
    WITH ttt AS (
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            id_point_2,
            geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event, 
            next_id_point,
            next_geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2            
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            id_point,
            geom,
            next_id_point_2,
            next_geom_2,
            floor((st_x(geom)-924987.5)/25) as x_grid, 
            floor((st_y(geom)-6500012.5)/25 )as y_grid,
            floor((st_x(next_geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(next_geom_2)-6500012.5)/25) as y_grid_2 
        FROM exp_encounter_event_default
        UNION ALL	
        SELECT 
            id_encounter_event,
            next_id_point,
            next_geom,
            id_point_2,
            geom_2,
            floor((st_x(next_geom)-924987.5)/25) as x_grid, 
            floor((st_y(next_geom)-6500012.5)/25) as y_grid,
            floor((st_x(geom_2)-924987.5)/25) as x_grid_2, 
            floor((st_y(geom_2)-6500012.5)/25) as y_grid_2             
        FROM exp_encounter_event_default
        ORDER BY id_encounter_event, x_grid, y_grid
    )
    SELECT
        1000000*x_grid + y_grid AS grid_id,
        1000000*x_grid_2 + y_grid_2 AS grid_id_2, 
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2 AS x_c,
        y_grid * 25 + 6500012.5+25/2 AS y_c,
        x_grid_2 * 25 + 924987.5+25/2 AS x_c2,
        y_grid_2 * 25 + 6500012.5+25/2 AS y_c2
    FROM ttt
    WHERE NOT EXISTS (
    SELECT 1
    FROM vis_grid_human_2_m as vg
    WHERE vg.x_grid = ttt.x_grid
      AND vg.y_grid = ttt.y_grid
      AND vg.x_grid_2 = ttt.x_grid_2
      AND vg.y_grid_2 = ttt.y_grid_2
    )
    GROUP BY
        x_grid,
        y_grid,
        x_grid_2,
        y_grid_2,
        x_grid * 25 + 924987.5+25/2,
        y_grid * 25 + 6500012.5+25/2,
        x_grid_2 * 25 + 924987.5+25/2,
        y_grid_2 * 25 + 6500012.5+25/2
    
query ran : 
About to run intervisibility with rad = 1033.4077351297235
must match
35462
4
4
----------
Batch number : 0
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 0
Batch number : 1
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 1
Batch number : 2
Human point length : 100000
Animal point length : 100000
Correct Vis
The network is just pairs
itervis count : 100000
intervis count100000
100000
100000
about to create sorted
created sorted
about to zip results
4
100000
zipped results
here 11
Finished and commited batch 2
Batch number : 3
Human point length : 35462
Animal point length : 35462
Correct Vis
The network is just pairs
itervis count : 35462
intervis count35462
35462
35462
about to create sorted
created sorted
about to zip results
4
35462
zipped results
here 11
Finished and commited batch 3
--- 184.54060530662537 seconds ---
