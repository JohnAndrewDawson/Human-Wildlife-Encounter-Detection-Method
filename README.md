# Human-Wildlife-Encounter-Detection-Method
Human Wildlife Encounter Detection Method 
To use this code please ensure that the POSTGIS database connects to Python and the variable db is updated to the name of the database.

Ensure that the python environment has the required library installed.
•	Tracklib
•	Sys
•	Math
•	shapely 
•	psycopg2
•	numpy 
•	typing 
Ensure that the file my_utils.py is in the same folder as human_wildlife_encounters_main.py
This will run all steps of the method except for the visibility check. To check the visibility criterion is used the visibility.py file must be run in QGIS. This is separated as running QGIS python directly is very sensitive to the QGIS instillation.
