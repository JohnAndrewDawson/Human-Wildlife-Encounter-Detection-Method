# Human-Wildlife Encounter Detection Project

This project provides code to detect human-wildlife encounters from trajectory data. It is released alongside a research paper that extensively discusses various applications and results.

## Database Structure

The project uses a SQL database. The data, results, and structured database are accessible in the included file : 
`ResRoute_with_results.sql.

To access this database, create a new database in PostgreSQL and add the PostGIS extension using the following command:

CREATE EXTENSION postgis;

After adding the PostGIS extension, use the ResRoute_with_results.sql file to restore the database.

> **Note**: The database contains some redundant tables used for sensitivity analyses, which are not shown in the diagram.

## Requirements

- SQL environment to extract and query the ResRoute database
- Python (with required libraries installed — see `requirements.txt`)
- QGIS with the Visibility Analysis plugin by ___ (please specify author)

Ensure that `my_utils.py` and `main.py` are located in the same folder, or call `my_utils.py` where you would like to use the functions.

## Workflow Overview

1. **Extract and prepare data**  
   Extract the ResRoute database in your SQL environment.

2. **Run Encounter Events Analysis**  
   In Python, declare the relevant variables and run the function:  
   `my_utils.encounter_events`  
   This will call all functions that can be used before running a QGIS environment.

3. **Run Visibility Analysis in QGIS**  
   Open QGIS with the Visibility Analysis plugin installed. Run the `visibility.py` script, setting the following parameters:
   - Human height
   - Animal height
   - Target encounter events table  
   
   > **Note**: QGIS may become unresponsive during this process. Upon completion, observation points and view lines will be loaded into QGIS, and a visibility boolean column will be added to the encounter events table in SQL.

4. **Run Encounters**  
   Back in Python, run the function:  
   `my_utils.Encounter` as shown in `main.py`.

## Function Call Order

To run the analysis step-by-step or customize experiments, call the following functions in order:

| Step | Function Name              | Description                                     |
|------|----------------------------|-------------------------------------------------|
| 1    | `find_comparable_routes`   | Find comparable trajectories                    |
| 2    | `create_ppa_table`         | Create PPA table                                |
| 3    | `create_filtered_hda_table`| Filter human trajectories & create HAD          |
| 4    | `create_encounter_events`  | Detect encounter events                         |
| 5    | **Visibility Analysis (QGIS)** | Check obstacle conditions (run in QGIS)     |
| 6    | `assign_encounters`      | Group encounter events into encounters            |
| 7    | `create_encounter_table` | Create encounter geometries and encounter table   |

## Additional Notes

- To replicate all experiments from the accompanying paper, use the included script:
  - `recreate_paper.py`
    1. Run the first 5 cells.
    2. Run `visibility.py` for each of the preset variable sets defined in the file.
    3. Run the remaining cells in `recreate_paper.py`.

- You can also run individual functions with different parameters to experiment without rerunning previous steps.

