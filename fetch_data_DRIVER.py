import os, sys, arcpy, importlib
# Please Ignore, Original Test Parameters:
#inputdata = r"C:\Users\lruiyang\Desktop\Age_Adjusted_rate_tool\fake_death.dbf"
#outputfolder = r"C:\Users\lruiyang\Desktop\Age_Adjusted_rate_tool"
#id_field = "GEOID10"
#age_field = "age"
#base_year = "2000"
#r_crit_level = "state"
#r_crit_state = "26"
#r_year = "2010"
#r_geolevel = "county"

#base_year, r_crit_level, r_crit, r_year, r_geolevel, age_structure

## Get Input
outputfolder = arcpy.GetParameterAsText(0) # Set Output folder

base_year = arcpy.GetParameterAsText(1) # Get year for standard age group structure
r_crit_level = "state" # Set Geographic level for base population 
r_crit_state = arcpy.GetParameterAsText(2) # Choose a state for calculation
r_year = arcpy.GetParameterAsText(3) # Set year of base population
r_geolevel = arcpy.GetParameterAsText(4) # Set Geographic level for calculation. Either County or tract for now


# Map States to number
map_state = dict({"NAME":"state","Alabama":"01","Alaska":"02","Arizona":"04","Arkansas":"05","California":"06","Colorado":"08","Connecticut":"09","Delaware":"10","District of Columbia":"11","Florida":"12","Georgia":"13","Hawaii":"15","Idaho":"16","Illinois":"17","Indiana":"18","Iowa":"19","Kansas":"20","Kentucky":"21","Louisiana":"22","Maine":"23","Maryland":"24","Massachusetts":"25","Michigan":"26","Minnesota":"27","Mississippi":"28","Missouri":"29","Montana":"30","Nebraska":"31","Nevada":"32","New Hampshire":"33","New Jersey":"34","New Mexico":"35","New York":"36","North Carolina":"37","North Dakota":"38","Ohio":"39","Oklahoma":"40","Oregon":"41","Pennsylvania":"42","Rhode Island":"44","South Carolina":"45","South Dakota":"46","Tennessee":"47","Texas":"48","Utah":"49","Vermont":"50","Virginia":"51","Washington":"53","West Virginia":"54","Wisconsin":"55","Wyoming":"56","Puerto Rico":"72"})
r_crit = map_state[r_crit_state]

# Import Modules
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import fetch_data as fd # This module fetching data from Census Bureau
fd = importlib.reload(fd) # Make sure newest module is loaded

# Call fetch_data function in fd module. This module return the population matrix for each geographic unit 
# ,and the age structure (percentage of each age group) 
[age_vector, age_exp, r_num_table, r_num_m, r_num_f, r_note_col] = fd.download_age_from_api(base_year, r_crit_level, r_crit, r_year, r_geolevel)

i = 0
ncol = len(r_note_col[0])
while i < len(r_note_col):
	if i == 0:
		r_note_col[i].append("GEOID")
	else:
		indexV = fd.col_erase([fd.sequence(0,ncol)],[0])[0]
		r_note_col[i].append(fd.merge_array_elements(r_note_col[i], indexV))	
	i += 1

    
# Write raw data for male from both standard population years and current year into files
# arcpy.AddMessage("\nWriting male data to file...")
# f = open(outputfolder + "\\" + "RawData_" + r_crit_level + r_crit + "_" + r_geolevel + "_male.data", "w")
# f.write(r_crit_level +'\n')
# f.write(str(r_crit) +'\n')
# f.write(str(age_vector) +'\n')
# f.write(str(age_exp)+'\n')
# f.write(str(r_num_m)+'\n')
# f.write(str(r_note_col)+'\n')
# f.close()

# # Write raw data for female from both standard population years and current year into files
# arcpy.AddMessage("\nWriting female data to file...")
# f = open(outputfolder + "\\" + "RawData_" + r_crit_level + r_crit + "_" + r_geolevel + "_female.data", "w")
# f.write(r_crit_level +'\n')
# f.write(str(r_crit) +'\n')
# f.write(str(age_vector) +'\n')
# f.write(str(age_exp)+'\n')
# f.write(str(r_num_f)+'\n')
# f.write(str(r_note_col)+'\n')
# f.close()

# Write raw data for both gender from both standard population years and current year into files
arcpy.AddMessage("\nWriting both gender data to file...")
f = open(outputfolder + "\\" + "RawData_" + r_crit_level + r_crit + "_" + r_geolevel + ".data", "w")
f.write(r_crit_level +'\n')
f.write(str(r_crit) +'\n')
f.write(str(age_vector) +'\n')
f.write(str(age_exp)+'\n')
f.write(str(r_num_table)+'\n')
f.write(str(r_note_col)+'\n')
f.close()



# Show Message to inform the output of the tool
arcpy.AddMessage("\nCensus Data was downloaded in File Path:")
arcpy.AddMessage("Raw Data: " + outputfolder + "\\" + "RawData_" + r_crit_level + r_crit + "_" + r_geolevel + ".data")
arcpy.AddMessage("\nPlease use the output data file in the next step analysis...\n")