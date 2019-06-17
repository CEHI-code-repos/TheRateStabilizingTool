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

## Get Input
inputdata = arcpy.GetParameterAsText(0) # Input individual level dataset
outputfolder = arcpy.GetParameterAsText(1) # Set Output folder
id_field = arcpy.GetParameterAsText(2) # Identify field with Unique ID
age_field = arcpy.GetParameterAsText(3) # Identify field with age recorded

base_year = arcpy.GetParameterAsText(4) # Get year for standard age group structure
r_crit_level = "state" # Set Geographic level for base population 
r_crit_state = arcpy.GetParameterAsText(5) # Choose a state for calculation
r_year = arcpy.GetParameterAsText(6) # Set year of base population
r_geolevel = arcpy.GetParameterAsText(7) # Set Geographic level for calculation. Either County or tract for now
raw_age = str(arcpy.GetParameterAsText(8)) # Get age category, it's the lower bound of age group

nyear = float(arcpy.GetParameterAsText(9)) # Get number of year


partial_data = str(arcpy.GetParameterAsText(10)).upper() # Turn on to switch to county only version

state_shp = str(arcpy.GetParameterAsText(11)) # Shapefile for selected state. Optional, only needed when calculate spatial Bayesian 
if state_shp == "#":
	state_shp = ""

GeoID = str(arcpy.GetParameterAsText(12)) # GEOID used to identify census boundaries
if GeoID == "#":
	GeoID = ""

# Built-in CDC age structure
## Not in use yet. For future Development
s0 = [0,1,2,5,6,9,10,12,15,18,20,25,30,35,40,45,50,55,60,65,70,75,80,85]
s1 = [0,1,5,15,25,35,45,55,65,75,85]
s2 = [0,12,20,30,40,50,60,70,80]
s3 = [0,18,45,55,65,75]
s4 = [0,18,45,65,75]
s5 = [2,6,12,20,30,40,50,60,70,80]
s6 = [2,18,45,55,65,75]
s7 = [12,20,30,40,50,60,70,80]
s8 = [18,25,45,65]
s9 = [18,25,35,45,65]
s10 = [18,30,40,50,60,70,80]
s11 = [20,30,40,50,60,70,80]
s12 = [20,40,60]
s13 = [20,45,65]
s14 = [25,35,45,65]
s15 = [40,50,65]
s16 = [45,50,65]
s17 = [50,65]
s18 = [65,75]
s19 = [0,5,12,-18]
s20 = [0,18,45,-65]
s21 = [5,18,45,-65]
s22 = [18,25,35,45,-65]

p0 = [0.013818,0.013687,0.04163,0.014186,0.042966,0.01538,0.030069,0.042963,0.043035,0.029133,0.066478,0.06453,0.071044,0.080762,0.081851,0.072118,0.062716,0.048454,0.038793,0.034264,0.031773,0.027,0.017842,0.015508]
p1 = [0.013818,0.055317,0.145565,0.138646,0.135573,0.162613,0.134834,0.087247,0.066037,0.044842,0.015508]
p2 = [0.171738,0.115131,0.131007,0.151806,0.153968,0.11117,0.073057,0.058773,0.03335]
p3 = [0.257736,0.393797,0.134834,0.087247,0.066037,0.060349]
p4 = [0.257736,0.393797,0.222081,0.066037,0.060349]
p5 = [0.057395,0.090917,0.118388,0.134712,0.156099,0.158323,0.114314,0.075124,0.060435,0.034293]
p6 = [0.236742,0.404935,0.138647,0.089715,0.067905,0.062056]
p7 = [0.139004,0.158171,0.183282,0.185893,0.134221,0.088205,0.070959,0.040265]
p8 = [0.128810,0.401725,0.299194,0.170271]
p9 = [0.128810,0.182648,0.219077,0.299194,0.170271]
p10 = [0.215746,0.204517,0.207431,0.149771,0.098425,0.079180,0.044930]
p11 = [0.183707,0.212872,0.215905,0.155890,0.102446,0.082415,0.046765]
p12 = [0.396579,0.371795,0.231626]
p13 = [0.511356,0.311417,0.177227]
p14 = [0.209654,0.251468,0.343431,0.195447]
p15 = [0.357802,0.348494,0.293704]
p16 = [0.206957,0.430351,0.362692]
p17 = [0.542658,0.457342]
p18 = [0.522501,0.477499]
p19 = [0.268242,0.398090,0.333668]
p20 = [0.295022,0.450768,0.254210]
p21 = [0.234438,0.489506,0.276056]
p22 = [0.155243,0.220130,0.264034,0.360593]

#Most common fine age_structure = [0,1,2,5,6,9,10,12,15,18,20,25,30,35,40,45,50,55,60,65,70,75,80,85]
# Format age category to construct an age category array for calculation
split_age = raw_age.split(";")
num_age = []
for str_a in split_age:
	num_age.append(int(str_a))
age_structure = sorted(num_age)
# This part of code enable a new feature in v0.9 - set an maximum age for oldest age category 
if(age_structure[0] < 0):
	cap = age_structure[0]
	age_structure = age_structure[1:]
	age_structure.append(cap)
if(age_structure[0] < 0): # Maximum of one cap per request
	raise ValueError("Please input one cap age only!!!")


# Map States to number
map_state = dict({"NAME":"state","Alabama":"01","Alaska":"02","Arizona":"04","Arkansas":"05","California":"06","Colorado":"08","Connecticut":"09","Delaware":"10","District of Columbia":"11","Florida":"12","Georgia":"13","Hawaii":"15","Idaho":"16","Illinois":"17","Indiana":"18","Iowa":"19","Kansas":"20","Kentucky":"21","Louisiana":"22","Maine":"23","Maryland":"24","Massachusetts":"25","Michigan":"26","Minnesota":"27","Mississippi":"28","Missouri":"29","Montana":"30","Nebraska":"31","Nevada":"32","New Hampshire":"33","New Jersey":"34","New Mexico":"35","New York":"36","North Carolina":"37","North Dakota":"38","Ohio":"39","Oklahoma":"40","Oregon":"41","Pennsylvania":"42","Rhode Island":"44","South Carolina":"45","South Dakota":"46","Tennessee":"47","Texas":"48","Utah":"49","Vermont":"50","Virginia":"51","Washington":"53","West Virginia":"54","Wisconsin":"55","Wyoming":"56","Puerto Rico":"72"})
r_crit = map_state[r_crit_state]

# Import Modules
sys.path.append(os.path.split(os.path.realpath(__file__))[0])
import fetch_data as fd # This module fetching data from Census Bureau
fd = importlib.reload(fd) # Make sure newest module is loaded
import construct_deathdata as cd # This module calculate rates from input data and fetched population data
cd = importlib.reload(cd) # Make sure newest module is loaded
import data_filter as df # This module filtered the result based on input
df = importlib.reload(df) # Make sure newest module is loaded

# Call fetch_data function in fd module. This module return the population matrix for each geographic unit 
# ,and the age structure (percentage of each age group) 
[r_note_col, result, percent] = fd.fetch_data(base_year, r_crit_level, r_crit, r_year, r_geolevel, age_structure)

if partial_data == 'TRUE':
	filt_dict = df.build_filt_dict (inputdata, id_field)
	[result, r_note_col] = df.filter_with_dict (result, r_note_col, "GEOID", filt_dict)

# Write population matrix, and standard population structure into files
f = open(outputfolder + "\\" + "PopAge_structure_" + r_crit_level + r_crit + ".csv", "w")
head = True
for row in result:
	if head:
		headerline = row
		head = False
	temp_text = cd.vect_to_str(row)
	f.writelines(temp_text + "\n")
f.close()

f = open(outputfolder + "\\" + "Standard_Age_structure.csv", "w")
f.writelines(cd.vect_to_str(age_structure) + "\n")
f.writelines(cd.vect_to_str(percent[0]) + "\n")
f.close()

# Call construct_deathdata function in cd module. This module returns the age adjusted rate
outputpath = cd.construct_deathdata(r_note_col, result, percent, inputdata, outputfolder, id_field, age_field, nyear, state_shp, GeoID)

# Update Schema.ini file
f = open(outputfolder + "\\" + "schema.ini", "a")
f.writelines("[Standard_Age_structure.csv]\n")
f.writelines("Format=CSVDelimited\n")
f.writelines("ColNameHeader=True\n")
f.writelines("\n")
f.writelines("[PopAge_structure_" + r_crit_level + r_crit + ".csv]\n")
f.writelines("Format=CSVDelimited\n")
f.writelines("ColNameHeader=True\n")

i = 1
for col in headerline:
	#arcpy.AddMessage(col)
	if col in ["NAME", "state", "county", "tract", "GEOID"]:
		f.writelines("Col" + str(i) + "=" + str(col) + " Text Width 200\n")
	elif col == "Alert":
		f.writelines("Col" + str(i) + "=" + str(col) + " Text Width 200\n")
	elif col == "Population":
		f.writelines("Col" + str(i) + "=" + str(col) + " Long\n")
	else:
		f.writelines("Col" + str(i) + "=" + str(col) + " Double\n")
	i += 1

f.writelines("\n")
f.close()

# Show Message to inform the output of the tool
arcpy.AddMessage("\nFile Path:")
arcpy.AddMessage("Age Adjust Rate: " + outputpath)
arcpy.AddMessage("Age/Pop Table:   " + outputfolder + "\\" + "PopAge_structure_" + r_crit_level + r_crit + ".csv")
arcpy.AddMessage("Age Structure:   " + outputfolder + "\\" + "Standard_Age_structure.csv\n")
