This document provides a step by step prosses to restore the database using PGadmin4. After installing PGadmin4. When opening Pgadmin4 you may receive a password prompt for a password set  during the installation. 
The first step is to create a new database by right clicking database, hover over create and select database. 
<img width="605" height="251" alt="image" src="https://github.com/user-attachments/assets/1fc9619e-1849-4b42-b09b-d5f4334b68fe" />
The following prompt will appear where you must give the data base a name. Here I use ‘ResRoute’ which is used in the accompanying code as the default database name. Then click save. 
<img width="605" height="451" alt="image" src="https://github.com/user-attachments/assets/55d7c09d-4dc2-4309-b2c5-1a2f87d19a8b" />
After creating the database you must add the ‘POSTGIS ‘ extinction; to do this click on the database and select the ‘query tool’ indicated in the image below. 
<img width="605" height="231" alt="image" src="https://github.com/user-attachments/assets/3925f14a-c80b-4268-a3c0-3437c85b2b19" />
Make sure the query tool is connected to the ‘ResRoute’ database by checking the link indicated in the image. After add the command ‘CREATE EXTENTION postgis’ than hit the run indicator depicted in the image.
<img width="605" height="151" alt="image" src="https://github.com/user-attachments/assets/1394c5eb-f679-43e1-b6d3-071af26b5632" />
Finally, restore the database form the backup included in the github file ‘Resroute_with_results.sdl’. To do this right click the ‘ResRoute’ Database and select Restore. In the popup that appears select the file ‘ResRoutes_with_results.sql’ file downloaded from github where it is saved on your computer.
<img width="643" height="554" alt="image" src="https://github.com/user-attachments/assets/faa80b68-5afe-4bf2-a2bd-0a0b86571f0c" />
<img width="605" height="334" alt="image" src="https://github.com/user-attachments/assets/916c1cf7-031a-4c01-bab3-f34cfc017931" />
